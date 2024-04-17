import os
import mysql.connector
from src.utils.containers import User, finance
from src.utils.exceptions import UserNotFoundException, MalformedUserException
import bcrypt
from typing import NoReturn, List, Dict
from src.utils.app_utils import load_app_info
from src.utils import email_utils
from uuid import uuid4
import datetime
import subprocess
from dotenv import load_dotenv
import random
import sys
from contextlib import contextmanager


class connect:
    def __init__(self):
        load_dotenv()
        try:
            self.connection = mysql.connector.connect(
                host=os.environ["DB_HOST"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                database=os.environ["DB_NAME"],
            )
            self.cursor = self.connection.cursor(buffered=True)
        except mysql.connector.Error as e:
            print("Access denied: {}".format(e))
            sys.exit(1)
        except KeyError as e:
            print("Environment variable not found: {}".format(e))
            raise SystemError
        except Exception as e:
            print("Error: {}".format(e))
            sys.exit(1)

    def get_all_finances(self) -> list:
        return_list = []
        invoice_sql = """
            SELECT a.seq, a.id, concat(b.first_name, ' ', b.last_name),
            concat(c.first_name, ' ', c.last_name), d.stat_desc, e.type_desc,
            a.tax, fees, a.dt_added, a.dt_updated,
            concat(f.first_name, ' ', f.last_name),
            concat(g.first_name, ' ', g.last_name), inv_date FROM inv_head a,
            users b, users c, statuses d, record_types e, users f, users g
            WHERE a.creator = b.seq AND a.approver = c.seq AND
            a.record_status = d.seq AND a.record_type = e.seq AND
            a.added_by = f.seq AND a.updated_by = g.seq;"""
        self.cursor.execute(invoice_sql)
        rows = self.cursor.fetchall()
        line_sql = """
        SELECT a.inv_seq, a.line_id, a.item_desc, a.item_price, a.qty,
        concat(c.first_name, ' ', c.last_name),
        concat(d.first_name, ' ', d.last_name),
        a.dt_added, a.dt_updated FROM
        inv_line a, users c, users d WHERE
        a.inv_seq = %s AND a.added_by = c.seq
        AND a.updated_by = d.seq"""
        for row in rows:
            self.cursor.execute(line_sql, (row[0],))
            lines = self.cursor.fetchall()
            row_container = finance(row, lines)
            return_list.append(row_container.__dict__)

        return return_list

    def save_user(self, user: User):
        ((user_seq, user_val), (perms_seq, perms_val)) = user.sql()
        self.cursor.execute(user_seq, user_val)
        self.connection.commit()
        user_seq = self.cursor.lastrowid
        perms_val[0] = user_seq
        self.cursor.execute(perms_seq, perms_val)
        self.connection.commit()
        user.seq = self.cursor.lastrowid
        # Send Password Reset Email if not a system user
        if not user.system_user:
            self.send_password_reset(user)

    def send_password_reset(self, user: User):
        token = self.request_reset_password(user.seq, "SYSTEM")
        app_domain = load_app_info()["public"]["application_url"]
        email_utils.send_password_reset_email(
            user, f"{app_domain}/reset_password/{token}"
        )

    def get_user_by_seq(self, user_seq: int) -> User:
        user_sql = """SELECT seq, user_name,
        first_name, last_name, email, system_user, theme, added_by,
        updated_by, is_active, dt_added, dt_updated FROM users WHERE seq = %s"""
        self.cursor.execute(user_sql, (user_seq,))
        user = self.cursor.fetchone()
        if user is None:
            raise UserNotFoundException
        self.cursor.fetchall()  # flush the cursor
        perms_sql = """SELECT seq, inv_edit, inv_view,
        doc_edit, doc_view, inv_admin, doc_admin, approve_invoices,
        receive_emails, user_admin added_by, updated_by, dt_added,
        dt_updated
        FROM permissions WHERE user_seq = %s"""
        self.cursor.execute(perms_sql, (user_seq,))
        perms = self.cursor.fetchone()
        if perms is None:
            raise MalformedUserException
        self.cursor.fetchall()  # Flush the cursor
        vote_sql = """SELECT a.type_desc FROM voting_types a, vote_perms b
            WHERE a.seq = b.vote_seq AND b.user_seq = %s"""

        self.cursor.execute(vote_sql, (user_seq,))

        voting = self.get_user_vote_perms(user_seq)
        # print(f"User.from_sql with votes: {voting}")

        return User.from_sql(user, perms, voting)

    def get_user_vote_perms(self, user_seq):
        sql = """SELECT a.type_desc, b.granted
        FROM voting_types a, vote_perms b
        WHERE a.seq = b.vote_seq AND b.user_seq = %s"""
        self.cursor.execute(sql, (user_seq,))
        votes = {k: v == 1 for (k, v) in self.cursor.fetchall()}
        return votes

    def get_user_by_user_name(self, user_name: str) -> User:
        user_sql = """SELECT seq, user_name,
        first_name, last_name, email, system_user, theme, added_by,
        updated_by, dt_added, dt_updated FROM users WHERE user_name = %s"""
        self.cursor.execute(user_sql, (user_name,))
        user = self.cursor.fetchone()
        if user is None:
            raise UserNotFoundException
        self.cursor.fetchall()  # flush the cursor
        perms_sql = """SELECT seq, inv_edit, inv_view,
        doc_edit, doc_view, inv_admin, doc_admin, approve_invoices,
        receive_emails, user_admin, doc_vote, added_by, updated_by, dt_added,
        dt_updated
        FROM permissions WHERE user_seq = %s"""
        self.cursor.execute(perms_sql, (user[0],))
        perms = self.cursor.fetchone()
        if perms is None:
            raise MalformedUserException
        self.cursor.fetchall()  # flush the cursor
        return User.from_sql(user, perms)

    def check_user_valid(self, username: str, password: str) -> User:
        sql = """SELECT seq, user_name, password FROM users WHERE
        user_name = %s AND is_active = 1;"""
        self.cursor.execute(sql, (username,))
        results = self.cursor.fetchall()
        if len(results) != 1:
            return (False, "", "")

        (user_seq, user_id, hashed_pass) = results[0]
        if hashed_pass is None:
            return (False, "", "")

        if not bcrypt.checkpw(password.encode("utf-8"),
                              hashed_pass.encode("utf-8")):
            return (False, "", "")

        return (True, user_seq, user_id)

    def is_user_admin(self, user_seq: int) -> bool:
        sql = "SELECT user_admin FROM permissions WHERE user_seq = %s"
        self.cursor.execute(sql, (user_seq,))
        results = self.cursor.fetchall()
        if len(results) != 1:
            return False
        return results[0][0]

    def can_user_edit_finances(self, user_seq: int) -> bool | NoReturn:
        sql = "SELECT inv_edit, inv_admin FROM permissions WHERE user_seq = %s"
        self.cursor.execute(sql, (user_seq,))
        results = self.cursor.fetchall()
        if len(results) != 1:
            return False
        return results[0][0] == 1 or results[0][1] == 1

    def get_all_finance_statuses(self):
        sql = """SELECT a.seq, a.stat_desc,
        CONCAT(b.first_name, ' ', b.last_name),
        CONCAT(c.first_name, ' ', c.last_name),
        a.dt_added, a.dt_updated FROM statuses a, users b, users c
        WHERE a.added_by = b.seq AND a.updated_by = c.seq"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all_finance_status_names(self) -> list:
        sql = "SELECT stat_desc FROM statuses"
        self.cursor.execute(sql)
        return [x[0] for x in self.cursor.fetchall()]

    def get_all_types(self) -> list:
        sql = "SELECT type_desc FROM record_types"
        self.cursor.execute(sql)
        return [x[0] for x in self.cursor.fetchall()]

    def filter_finances(self, filter_data: dict):
        return_list = []
        valid_types = self.get_all_types()
        valid_statuses = self.get_all_finance_status_names()

        allowed_statuses = []
        for status in valid_statuses:
            if status in filter_data['status'] and \
                    filter_data['status'][status]:
                allowed_statuses.append(status)

        allowed_types = []
        for type in valid_types:
            if type in filter_data['types'] and filter_data['types'][type]:
                allowed_types.append(type)

        sql = """
        SELECT a.seq, a.id, concat(b.first_name, ' ', b.last_name),
            concat(c.first_name, ' ', c.last_name), d.stat_desc, e.type_desc,
            a.tax, fees, a.dt_added, a.dt_updated,
            concat(f.first_name, ' ', f.last_name),
            concat(g.first_name, ' ', g.last_name), inv_date FROM inv_head a,
            users b, users c, statuses d, record_types e, users f, users g
            WHERE a.creator = b.seq AND a.approver = c.seq AND
            a.record_status = d.seq AND a.record_type = e.seq AND
            a.added_by = f.seq AND a.updated_by = g.seq ORDER BY a.id"""
        (allowed_statuses, allowed_types, filter_data)

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        finance_filtered_rows = []
        for row in rows:
            if row[4] in allowed_statuses and row[5] in allowed_types:
                finance_filtered_rows.append(row)
        line_sql = """
        SELECT a.inv_seq, a.line_id, a.item_desc, a.item_price, a.qty,
        concat(c.first_name, ' ', c.last_name),
        concat(d.first_name, ' ', d.last_name),
        a.dt_added, a.dt_updated FROM
        inv_line a, users c, users d WHERE
        a.inv_seq = %s AND a.added_by = c.seq
        AND a.updated_by = d.seq"""
        for row in finance_filtered_rows:
            self.cursor.execute(line_sql, (row[0],))
            lines = self.cursor.fetchall()
            row_container = finance(row, lines)
            return_list.append(row_container.__dict__)

        return return_list

    def get_docket_conversations(self, seq):
        SQL = """SELECT a.docket_text, concat(b.first_name, ' ', b.last_name)
        FROM docket_conversations a, users b WHERE a.added_by = b.seq AND
        a.docket_seq = %s"""
        self.cursor.execute(SQL, (seq,))
        conversations = self.cursor.fetchall()
        return conversations

    def get_record_by_seq(self, seq):
        SQL = """
        SELECT a.seq, a.id, concat(b.first_name, ' ', b.last_name),
            concat(c.first_name, ' ', c.last_name), d.stat_desc, e.type_desc,
            a.tax, fees, a.dt_added, a.dt_updated,
            concat(f.first_name, ' ', f.last_name),
            concat(g.first_name, ' ', g.last_name), inv_date FROM inv_head a,
            users b, users c, statuses d, record_types e, users f, users g
            WHERE a.creator = b.seq AND a.approver = c.seq AND
            a.record_status = d.seq AND a.record_type = e.seq AND
            a.added_by = f.seq AND a.updated_by = g.seq
            AND a.seq = %s"""
        self.cursor.execute(SQL, (seq,))
        rows = self.cursor.fetchall()[0]
        line_sql = """
        SELECT a.inv_seq, a.line_id, a.item_desc, a.item_price, a.qty,
        concat(c.first_name, ' ', c.last_name),
        concat(d.first_name, ' ', d.last_name),
        a.dt_added, a.dt_updated FROM
        inv_line a, users c, users d WHERE
        a.inv_seq = %s AND a.added_by = c.seq
        AND a.updated_by = d.seq"""
        self.cursor.execute(line_sql, (seq,))
        lines = self.cursor.fetchall()
        row_container = finance(rows, lines)
        return row_container.__dict__

    def get_user_by_full_name(self, full_name: str) -> User:
        sql = """SELECT seq FROM users WHERE
        concat(first_name, ' ', last_name) = %s"""
        self.cursor.execute(sql, (full_name,))
        return self.get_user_by_seq(self.cursor.fetchone()[0])

    def get_type_seq(self, type_desc: str) -> int:
        sql = "SELECT seq FROM record_types WHERE type_desc = %s"
        self.cursor.execute(sql, (type_desc,))
        return self.cursor.fetchone()[0]

    def get_status_seq(self, status_desc: str) -> int:
        sql = "SELECT seq FROM statuses WHERE stat_desc = %s"
        self.cursor.execute(sql, (status_desc,))
        return self.cursor.fetchone()[0]

    def create_record(self, record_data: dict, user: User):
        sql = """INSERT INTO inv_head (id, creator, approver, inv_date,
        record_status, record_type, tax, fees, added_by, updated_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        creator = self.get_user_by_full_name(record_data["header"]["creator"])
        approve = self.get_user_by_full_name(record_data["header"]["approver"])
        record_type = self.get_type_seq(record_data["header"]["type"])
        status_type = self.get_status_seq(record_data["header"]["status"])

        values = (
            record_data["header"]["id"],
            creator,
            approve,
            record_data["header"]["inv_date"],
            status_type,
            record_type,
            record_data["header"]["tax"],
            record_data["header"]["fees"],
            user.seq,
            user.seq,
        )
        self.cursor.execute(sql, values)
        self.connection.commit()
        record_seq = self.cursor.lastrowid
        for line in record_data["lines"]:
            sql = """INSERT INTO inv_line (inv_seq, line_id, item_desc,
            item_price, qty, added_by, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (
                record_seq,
                line["line_id"],
                line["item_desc"],
                line["item_price"],
                line["qty"],
                user.seq,
                user.seq,
            )
            self.cursor.execute(sql, values)
            self.connection.commit()

    def check_invoice_info(self, user_full_name: str, user_pin: str) -> tuple:
        sql = """SELECT a.seq, a.user_name, a.finance_pin, a.first_name,
        a.last_name, b.inv_admin, b.inv_edit, b.approve_invoices FROM users a,
        permissions b WHERE a.seq = b.user_seq and
        concat(a.first_name, ' ', a.last_name) = %s AND a.is_active = 1"""
        self.cursor.execute(sql, (user_full_name,))
        user = self.cursor.fetchone()
        if user is None:
            return (False, False, False)
        if user[2] != user_pin:
            return (False, False, False)
        return (user[5] == 1, user[6] == 1, user[7] == 1)

    def get_all_finance_users(self):
        sql = """SELECT a.seq, concat(a.first_name, ' ', a.last_name)
        FROM users a, permissions b WHERE system_user = 0 AND
        a.seq = b.user_seq and (b.inv_admin = 1 or b.inv_edit = 1)
        and a.is_active = 1"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all_approvers(self):
        sql = """SELECT a.seq, concat(a.first_name, ' ', a.last_name)
        FROM users a, permissions b WHERE
        a.seq = b.user_seq and (b.inv_admin = 1 or b.approve_invoices = 1)
        and a.is_active = 1 ORDER BY a.seq"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_lines(self, seq):
        sql = """SELECT a.line_id, a.item_desc, a.qty FROM inv_line a WHERE
        a.inv_seq = %s"""
        self.cursor.execute(sql, (seq,))
        return self.cursor.fetchall()

    def edit_record(self, seq: int, data: dict, current_user: User):
        sql = """UPDATE inv_head SET id = %s, creator = %s, approver = %s,
        inv_date = %s, record_status = %s, record_type = %s, tax = %s,
        fees = %s, updated_by = %s WHERE seq = %s"""
        creator = self.get_user_by_full_name(data["header"]["creator"])
        approver = self.get_user_by_full_name(data["header"]["approver"])
        record_type = self.get_type_seq(data["header"]["type"])
        status_type = self.get_status_seq(data["header"]["status"])
        values = (
            data["header"]["id"],
            creator,
            approver,
            data["header"]["inv_date"],
            record_type,
            status_type,
            data["header"]["tax"],
            data["header"]["fees"],
            current_user.seq,
            seq,
        )
        self.cursor.execute(sql, values)
        self.connection.commit()
        existing_line_ids = [x[0] for x in self.get_lines(seq)]
        for line in data["lines"]:
            if line["line_id"] in existing_line_ids:
                sql = """UPDATE inv_line SET line_id = %s, item_desc = %s,
                item_price = %s, qty = %s, updated_by = %s
                WHERE inv_seq = %s AND line_id = %s"""
                values = (
                    line["line_id"],
                    line["item_desc"],
                    line["item_price"],
                    line["qty"],
                    current_user.seq,
                    seq,
                    line["line_id"],
                )
                self.cursor.execute(sql, values)
                self.connection.commit()
            else:
                sql = """INSERT INTO inv_line (inv_seq, line_id, item_desc,
                item_price, qty, added_by, updated_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                values = (
                    seq,
                    line["line_id"],
                    line["item_desc"],
                    line["item_price"],
                    line["qty"],
                    current_user.seq,
                    current_user.seq,
                )
                self.cursor.execute(sql, values)
                self.connection.commit()

    def get_pending_finances(self):
        return_list = []
        invoice_sql = """
            SELECT a.seq, a.id, concat(b.first_name, ' ', b.last_name),
            concat(c.first_name, ' ', c.last_name), d.stat_desc, e.type_desc,
            a.tax, fees, a.dt_added, a.dt_updated,
            concat(f.first_name, ' ', f.last_name),
            concat(g.first_name, ' ', g.last_name), inv_date FROM inv_head a,
            users b, users c, statuses d, record_types e, users f, users g
            WHERE a.creator = b.seq AND a.approver = c.seq AND
            a.record_status = d.seq AND a.record_type = e.seq AND
            a.added_by = f.seq AND a.updated_by = g.seq AND a.approver = 0
            ORDER BY a.seq;"""
        self.cursor.execute(invoice_sql)
        rows = self.cursor.fetchall()
        line_sql = """
        SELECT a.inv_seq, a.line_id, a.item_desc, a.item_price, a.qty,
        concat(c.first_name, ' ', c.last_name),
        concat(d.first_name, ' ', d.last_name),
        a.dt_added, a.dt_updated FROM
        inv_line a, users c, users d WHERE
        a.inv_seq = %s AND a.item_seq = b.seq AND a.added_by = c.seq
        AND a.updated_by = d.seq"""
        (invoice_sql)
        for row in rows:
            self.cursor.execute(line_sql, (row[0],))
            lines = self.cursor.fetchall()
            row_container = finance(row, lines)
            return_list.append(row_container.__dict__)

        return return_list

    def change_preferences(
        self, target_user: int, current_user: User, new_prefs: dict
    ):
        sql = """UPDATE users SET user_name = %s, theme = %s, email=%s,
                 updated_by = %s WHERE seq = %s"""
        email_domain = load_app_info()["public"]["email_domain"]
        email = new_prefs.get("email").removesuffix(email_domain)
        self.cursor.execute(
            sql,
            (
                new_prefs.get("uname"),
                new_prefs.get("theme"),
                email,
                current_user.seq,
                target_user,
            ),
        )
        self.connection.commit()

    def change_password(
        self, target_seq: int, current_user: User, new_password: str
    ):
        sql = """UPDATE users SET password = %s,
                 updated_by = %s WHERE seq = %s"""
        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        self.cursor.execute(sql, (hashed, current_user.seq, target_seq))
        user = self.get_user_by_seq(target_seq)
        email_utils.send_password_updated_email(user)
        self.connection.commit()

    def request_reset_password(self, target_seq: int, requested_ip: str) \
            -> str:
        if self.get_user_by_seq(target_seq).system_user:
            raise UserNotFoundException
        sql = """INSERT INTO password_reset (user_seq, token, created_by)
        VALUES (%s, %s, %s)"""
        values = (target_seq, uuid4().hex, requested_ip)
        self.cursor.execute(sql, values)
        self.connection.commit()
        return values[1]

    def get_user_by_reset_token(self, token: str) -> tuple:
        sql = """SELECT a.seq, a.user_name FROM users a, password_reset b WHERE
        a.seq = b.user_seq AND b.token = %s AND
        b.created_at > NOW() - INTERVAL 1 DAY and a.is_active = 1
        and a.system_user != 1"""
        self.cursor.execute(sql, (token,))
        return self.cursor.fetchone()

    def can_user_edit_docket_record(self, user: User, seq: int):
        # If the user created it, then they can edit it
        sql = """SELECT created_by FROM officer_docket WHERE seq = %s"""
        self.cursor.execute(sql, (seq,))
        creator = self.cursor.fetchone()[0]
        if creator == user.seq:
            return True
        # If the user is an admin, then they can edit it
        sql = """SELECT doc_admin FROM permissions WHERE user_seq = %s"""
        self.cursor.execute(sql, (user.seq,))
        if self.cursor.fetchone()[0] == 1:
            return True

        # If the user is assigned to it, then they can edit it
        sql = """SELECT assigned_to FROM docket_assignees
                 WHERE docket_seq = %s"""
        self.cursor.execute(sql, (seq,))
        results = self.cursor.fetchall()
        for result in results:
            if result[0] == user.seq:
                return True
        # Otherwise, they can't edit this record.
        return False

    def change_approver_pin(
        self, target_seq: int, current_user: User, new_pin: str
    ):
        sql = """UPDATE users SET finance_pin = %s, updated_by = %s
                 WHERE seq = %s"""
        self.cursor.execute(sql, (new_pin, current_user.seq, target_seq))
        self.connection.commit()

    def can_user_view_officer_docket(self, user: User) -> bool:
        sql = """SELECT doc_view, doc_admin FROM permissions
                 WHERE user_seq = %s"""
        self.cursor.execute(sql, (user.seq,))
        result = self.cursor.fetchone()
        return result[0] == 1 or result[1] == 1

    def create_docket_conversation(self, seq: int,
                                   conversation_info: dict, user: User):
        sql = """INSERT INTO docket_conversations
        (docket_seq, docket_text, added_by) VALUES (%s, %s, %s)"""
        self.cursor.execute(sql, (seq, conversation_info['data'], user.seq))
        self.connection.commit()

    def get_docket_viewers(self):
        sql = """SELECT a.seq, CONCAT(a.first_name, ' ', a.last_name)
                 FROM users a, permissions b WHERE a.seq = b.user_seq AND
                 (b.doc_view = 1 OR b.doc_admin = 1) and is_active = 1"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def can_user_edit_officer_docket(self, user: User) -> bool:
        sql = """SELECT doc_edit, doc_admin FROM permissions
                 WHERE user_seq = %s"""
        self.cursor.execute(sql, (user.seq,))
        result = self.cursor.fetchone()
        return result[0] == 1 or result[1] == 1

    def reset_password(self, user_seq: int, new_password: str):
        sql = """UPDATE users SET password = %s, updated_by = %s
                 WHERE seq = %s"""
        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        (sql, (hashed, 0, user_seq))
        self.cursor.execute(sql, (hashed, 1, user_seq))
        email_utils.send_password_updated_email(self.get_user_by_seq(user_seq))
        self.connection.commit()

        # Delete the old token
        sql = """DELETE FROM password_reset WHERE user_seq = %s"""
        self.cursor.execute(sql, (user_seq,))
        self.connection.commit()

    def is_invoice_admin(self, user_seq: int) -> bool:
        sql = """SELECT inv_admin FROM permissions WHERE user_seq = %s"""
        self.cursor.execute(sql, (user_seq,))
        return self.cursor.fetchone()[0] == 1

    def close(self):
        self.connection.close()

    def __del__(self):
        try:
            self.connection.close()
        except Exception:
            return

    @staticmethod
    def dump_database():

        with open("backup.sql", "w") as f:
            subprocess.Popen(
                ["/usr/bin/mysqldump", "-u" + os.environ['DB_BACKUP_USER'],
                 "management", "-p" + os.environ['DB_BACKUP_PASS']],
                stdout=f
            ).communicate()

    def update_finance_status(self, seq, stat_desc, user: User):
        sql = """UPDATE statuses SET stat_desc = %s, updated_by = %s
        WHERE seq = %s"""
        self.cursor.execute(sql, (stat_desc, user.seq, seq))
        self.connection.commit()

    def create_finance_status(self, stat_desc, user: User):
        sql = """INSERT INTO statuses (stat_desc, added_by, updated_by)
        VALUES (%s, %s, %s)"""
        self.cursor.execute(sql, (stat_desc, user.seq, user.seq))
        self.connection.commit()

    def update_docket_status(self, seq, stat_desc, user: User):
        sql = """UPDATE docket_status SET stat_desc = %s, updated_by = %s
        WHERE seq = %s"""
        self.cursor.execute(sql, (stat_desc, user.seq, seq))
        self.connection.commit()

    def get_all_docket_statuses(self):
        sql = """SELECT a.seq, a.stat_desc,
        CONCAT(b.first_name, ' ', b.last_name),
        CONCAT(c.first_name, ' ', c.last_name),
        a.dt_added, a.dt_updated FROM docket_status a, users b, users c
        WHERE a.added_by = b.seq AND a.updated_by = c.seq ORDER BY a.seq"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all_docket_voting_types(self) -> List[str]:
        sql = """SELECT (type_desc) FROM voting_types"""
        self.cursor.execute(sql)
        return [x[0] for x in self.cursor.fetchall()]

    def get_all_record_types(self):
        sql = """SELECT a.seq, a.type_desc,
        CONCAT(b.first_name, ' ', b.last_name),
        CONCAT(c.first_name, ' ', c.last_name),
        a.dt_added, a.dt_updated FROM record_types a, users b, users c
        WHERE a.added_by = b.seq AND a.updated_by = c.seq ORDER BY a.seq"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update_record_type(self, seq, type_desc, user: User):
        sql = (
            """UPDATE record_types SET type_desc = %s, updated_by = %s
            WHERE seq = %s"""
        )
        self.cursor.execute(sql, (type_desc, user.seq, seq))
        self.connection.commit()

    def create_record_type(self, type_desc, user: User):
        sql = """INSERT INTO record_types (type_desc, added_by, updated_by)
        VALUES (%s, %s, %s)"""
        self.cursor.execute(sql, (type_desc, user.seq, user.seq))
        self.connection.commit()

    def get_all_users(self):
        sql = """SELECT a.seq, a.user_name, a.first_name, a.last_name, a.email,
        a.system_user, a.theme, CONCAT(b.first_name, ' ', b.last_name),
        CONCAT(c.first_name, ' ', c.last_name), a.dt_added, a.dt_updated
        FROM users a, users b, users c WHERE a.added_by = b.seq AND
        a.updated_by = c.seq ORDER BY a.system_user, a.is_active, a.seq"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def update_user(self, user_seq, vals, current_user: User):
        sql = """
        UPDATE users SET user_name = %s,
        email = %s,
        first_name = %s,
        last_name = %s,
        theme = %s,
        system_user = %s,
        is_active = %s,
        updated_by = %s
        WHERE
        seq = %s
        """
        values = vals[0:7] + (current_user.seq, user_seq)
        print(sql,values)
        self.cursor.execute(sql, values)
        self.connection.commit()

        sql = """
        UPDATE permissions SET
        receive_emails = %s,
        inv_view = %s,
        inv_edit = %s,
        inv_admin = %s,
        approve_invoices = %s,
        doc_view = %s,
        doc_edit = %s,
        doc_admin = %s,
        user_admin = %s,
        updated_by = %s
        WHERE
        user_seq = %s
        """
        values = vals[7:] + (current_user.seq, user_seq)
        self.cursor.execute(sql, values)
        self.connection.commit()

    def update_user_vote_types(self,
                               user_seq: int,
                               votes: Dict[str, bool],
                               current_user: User):
        self.ensure_vote_perms_exist(user_seq, current_user)
        sql = """UPDATE vote_perms a, voting_types b SET
        a.granted = %s,
        a.updated_by = %s
        WHERE a.vote_seq = b.seq AND a.user_seq = %s
        AND b.type_desc = %s
        """
        values = [(v, current_user.seq, user_seq, k) for k, v in votes.items()]
        print(f"Running sql with values: {values}")
        self.cursor.executemany(sql, values)
        self.connection.commit()

    def ensure_vote_perms_exist(self, user_seq, current_user: User):
        sql = """SELECT seq, type_desc FROM voting_types"""
        self.cursor.execute(sql)
        all_types = [x[0] for x in self.cursor.fetchall()
                     if x[1] != "No Vote"]

        sql = """SELECT vote_seq FROM vote_perms WHERE user_seq = %s"""
        self.cursor.execute(sql, (user_seq,))
        user_types = [x[0] for x in self.cursor.fetchall()]

        need_types = [x for x in all_types if x not in user_types]

        sql = """INSERT INTO vote_perms
        (user_seq, vote_seq, added_by, updated_by) VALUES
        (%s, %s, %s, %s)"""
        cur_seq = current_user.seq
        values = [(user_seq, x, cur_seq, cur_seq) for x in need_types]

        self.cursor.executemany(sql, values)
        self.connection.commit()

    def add_user(self, vals, current_user):
        sql = """
        INSERT INTO users (user_name, email, first_name, last_name, theme,
        system_user, finance_pin, added_by, updated_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        finance_pin = random.randint(1000, 9999)
        values = vals[0:6] + (finance_pin, current_user.seq, current_user.seq)
        self.cursor.execute(sql, values)
        self.connection.commit()

        user_seq = self.cursor.lastrowid
        sql = """
        INSERT INTO permissions (user_seq, receive_emails, inv_view, inv_edit,
        inv_admin, approve_invoices, doc_view, doc_edit, doc_admin, user_admin,
        doc_vote, added_by, updated_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (user_seq,) + vals[6:] + (current_user.seq, current_user.seq)
        (sql, values)
        self.cursor.execute(sql, values)
        self.connection.commit()
        if not self.get_user_by_seq(user_seq).system_user:
            key = self.request_reset_password(user_seq,
                                              f"USER:{current_user.seq}")
            email_utils.send_welcome_email(
                self.get_user_by_seq(user_seq), key, finance_pin
            )
        self.ensure_vote_perms_exist(user_seq, current_user)

    def clear_old_resets(self):
        SQL = """DELETE FROM password_reset WHERE created_at <
        NOW() - INTERVAL 1 DAY"""
        self.cursor.execute(SQL)
        self.connection.commit()

    def get_officer_docket(self):
        sql = """SELECT a.seq, a.title, a.body, d.stat_desc, a.created_at,
        a.updated_at, CONCAT(b.first_name, ' ', b.last_name),
        CONCAT(c.first_name, ' ', c.last_name), a.created_by, e.type_desc FROM
        officer_docket a, users b, users c,
        docket_status d, voting_types e WHERE
        a.created_by = b.seq AND
        a.updated_by = c.seq AND
        a.status = d.seq AND
        a.vote_type = e.seq
        ORDER BY a.seq"""
        self.cursor.execute(sql)
        docket_data = []
        results = self.cursor.fetchall()
        for result in results:
            # Get the assignees
            assignees = self.get_record_assignees(result[0])
            docket_data.append((result, assignees))
        return docket_data

    def get_docket_vote_email_users(self):
        sql = """SELECT a.seq, a.user_name, a.first_name, a.last_name, a.email,
        a.system_user, a.theme, CONCAT(b.first_name, ' ', b.last_name),
        CONCAT(c.first_name, ' ', c.last_name), a.dt_added, a.dt_updated FROM
        users a, users b, users c, permissions d WHERE a.added_by = b.seq AND
        a.updated_by = c.seq AND a.system_user = 0 AND a.seq = d.user_seq AND
        d.doc_vote = 1 AND d.receive_emails = 1"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def create_officer_docket(self, data: dict, user: User):
        sql = """
        INSERT INTO officer_docket
        (title, body, status, vote_type, created_by, updated_by)
        VALUES (%s, %s, %s, %s, %s, %s)"""

        vote_type = self.get_docket_vote_type_by_name(
            data.get("voteType", "No Vote"))

        values = (data["title"], data["body"], 1,
                  vote_type, user.seq, user.seq)
        self.cursor.execute(sql, values)
        self.connection.commit()
        seq = self.cursor.lastrowid
        if data.get('isVote', 'off') == 'on':
            email_utils.alert_docket_creation(
                user, self.get_docket_vote_email_users(), data, seq
            )
        return seq

    def get_docket_vote_type_by_name(self, type_desc):
        sql = """SELECT seq FROM voting_types
        WHERE type_desc = %s"""
        self.cursor.execute(sql, (type_desc,))
        return self.cursor.fetchone()[0]

    def search_officer_docket(self, seq: int):
        sql = """SELECT a.seq, a.title, a.body, d.stat_desc, a.created_at,
        a.updated_at, CONCAT(b.first_name, ' ', b.last_name),
        CONCAT(c.first_name, ' ', c.last_name), e.type_desc FROM
        officer_docket a, users b,users c,
        docket_status d, voting_types e WHERE
        a.created_by = b.seq AND
        a.updated_by = c.seq AND
        a.status = d.seq AND
        a.vote_type = e.seq AND
        a.seq = %s"""
        self.cursor.execute(sql, (seq,))
        docket = self.cursor.fetchone()
        self.cursor.fetchall()
        # Get the votes
        sql = """SELECT vote_type FROM officer_votes WHERE docket_item = %s"""
        self.cursor.execute(sql, (seq,))
        votes = self.cursor.fetchall()
        # Get the assigned people
        sql = """SELECT CONCAT(b.first_name, ' ', b.last_name), b.seq
        FROM docket_assignees a, users b WHERE a.assigned_to = b.seq
        AND a.docket_seq = %s"""
        self.cursor.execute(sql, (seq,))
        assignees = self.cursor.fetchall()
        sql = """SELECT seq, file_name from docket_attachments WHERE
        docket_seq = %s"""
        self.cursor.execute(sql, (seq,))
        attachments = self.cursor.fetchall()
        return docket, votes, assignees, attachments

    def get_assigned_records(self, user: User):
        sql = """SELECT a.seq, a.title, a.body, d.stat_desc, a.created_at,
        a.updated_at, CONCAT(b.first_name, ' ', b.last_name),
        CONCAT(c.first_name, ' ', c.last_name), a.created_by FROM
        officer_docket a, users b, users c, docket_status d,
        docket_assignees e WHERE a.created_by = b.seq AND a.updated_by = c.seq
        AND a.status = d.seq AND a.seq = e.docket_seq AND e.assigned_to = %s
        ORDER BY a.seq"""
        self.cursor.execute(sql, (user.seq,))
        docket_data = []
        results = self.cursor.fetchall()
        for result in results:
            # Get the assignees
            assignees = self.get_record_assignees(result[0])
            docket_data.append((result, assignees))
        return docket_data

    def add_assignee(self, data):
        sql = """INSERT INTO docket_assignees (docket_seq, assigned_to,
        created_by, updated_by) VALUES
        (%s, %s, %s, %s)"""
        values = (data[0], data[1], data[2], data[2])
        self.cursor.execute(sql, values)
        self.connection.commit()
        email_utils.send_assignment_email(
            self.get_user_by_seq(data[1]),
            self.get_user_by_seq(data[2]),
            self.search_officer_docket(data[0]),
        )

    def del_assignee(self, data):
        sql = """DELETE FROM docket_assignees WHERE docket_seq = %s AND
        assigned_to = %s"""
        self.cursor.execute(sql, data[0:2])
        self.connection.commit()
        email_utils.alert_docket_removal(
            self.get_user_by_seq(data[1]),
            self.get_user_by_seq(data[2]),
            self.search_officer_docket(data[0]),
        )

    def update_officer_docket(self, docket, user, seq):
        sql = """UPDATE officer_docket SET title = %s,
        body = %s, status = %s, updated_by = %s WHERE seq = %s"""
        (docket["status"])
        values = (docket["title"], docket["body"],
                  docket["status"], user.seq, seq)
        self.cursor.execute(sql, values)
        self.connection.commit()
        docket_item = self.search_officer_docket(seq)
        email_utils.alert_docket_update(
            user, self.get_record_assignees(seq),
            docket_item,
            self.get_user_by_full_name(docket_item[0][6]).email
        )

    def get_record_assignees(self, seq: int):
        sql = """SELECT assigned_to FROM docket_assignees WHERE
        docket_seq = %s"""
        self.cursor.execute(sql, (seq,))
        return [self.get_user_by_seq(x[0]).__dict__
                for x in self.cursor.fetchall()]

    def can_user_view_finances(self, seq: int):
        sql = """SELECT inv_view, inv_admin FROM permissions WHERE
        user_seq = %s"""
        self.cursor.execute(sql, (seq,))
        results = self.cursor.fetchone()
        return results[0] == 1 or results[1] == 1

    def has_user_voted(self, user: User, seq: int):
        sql = """SELECT * FROM officer_votes WHERE user = %s AND
        docket_item = %s"""
        vals = (user.seq, seq)
        self.cursor.execute(sql, vals)
        return len(self.cursor.fetchall()) > 0

    def save_vote(self, user: User, vote: str, dock_seq: int):
        sql = """INSERT INTO officer_votes (user, vote_type, docket_item)
        VALUES (%s, %s, %s)"""
        values = (user.seq, vote, dock_seq)
        self.cursor.execute(sql, values)
        self.connection.commit()
        email_utils.notify_vote_confirmation(
            user, vote, self.search_officer_docket(dock_seq)
        )

    def get_vote_types_by_docket_seq(self, docket_seq: int):
        sql = """SELECT vote_type FROM officer_votes WHERE docket_item = %s"""
        self.cursor.execute(sql, (docket_seq,))
        return [x[0] for x in self.cursor.fetchall()]

    def close_vote(self, docket_seq: int, user: User):
        votes = self.get_vote_types_by_docket_seq(docket_seq)
        in_favor = votes.count("In Favor")
        opposed = votes.count("Opposed")
        doc_thresh = load_app_info()["private"]["doc_thresh"]
        total_votes = in_favor + opposed
        doc_ratio = in_favor / total_votes
        if doc_ratio >= doc_thresh:
            status = 4
        else:
            status = 5
        sql = (
            """UPDATE officer_docket SET status = %s, updated_by = %s WHERE
            seq = %s"""
        )
        self.cursor.execute(sql, (status, user.seq, docket_seq))
        self.connection.commit()

    def add_attachment(
        self,
        docket_seq: int,
        file_name: str,
        file_data: str,
        current_user: User,
    ):
        SQL = """INSERT INTO docket_attachments (docket_seq, file_name,
        file_data, added_by, updated_by) VALUES (%s,%s,%s,%s,%s)"""
        self.cursor.execute(
            SQL, (docket_seq, file_name, file_data, current_user.seq,
                  current_user.seq)
        )
        self.connection.commit()

    def search_docket_attachments(self, attachment_seq: int):
        SQL = """SELECT file_name, file_data FROM docket_attachments
        WHERE seq = %s"""
        self.cursor.execute(SQL, (attachment_seq,))
        return self.cursor.fetchone()

    def get_docket_attachments(self, docket_seq: int):
        SQL = """SELECT seq, file_name from docket_attachments WHERE
        docket_seq = %s"""
        self.cursor.execute(SQL, (docket_seq,))
        return self.cursor.fetchall()

    def update_attachment(self, seq, file_data):
        SQL = """UPDATE docket_attachments SET file_data = %s where seq = %s"""
        self.cursor.execute(SQL, (file_data, seq))
        self.connection.commit()

    def save_user_request(self, form_data: dict):
        SQL = """INSERT INTO user_requests (name, email, reason) VALUES
        (%s, %s, %s)"""
        values = (
            form_data.get("name"),
            form_data.get("email"),
            form_data.get("reason"),
        )
        self.cursor.execute(SQL, values)
        self.connection.commit()

        # Send the email to confirm to the user that their request was received
        email_utils.send_user_request_confirmation(form_data.get("email"))
        email_utils.alert_admins_new_user_request(
            form_data, self.get_user_admin_emails()
        )

    def get_user_admin_emails(self):
        SQL = """SELECT b.email FROM permissions a, users b WHERE a.user_seq =
        b.seq and a.user_admin = 1"""
        self.cursor.execute(SQL)
        domain = load_app_info()["public"]["email_domain"]
        return [x[0] + domain for x in self.cursor.fetchall()]

    def create_docket_status(self, desc: str, user: User):
        SQL = """INSERT INTO (stat_desc, added_by, updated_by) VALUES
        (%s, %s, %s)"""
        self.cursor.execute(SQL, desc, user.seq, user.seq)
        self.connection.commit()
        pass


@contextmanager
def db_connection():
    connection = connect()
    try:
        yield connection
    finally:
        connection.close()
