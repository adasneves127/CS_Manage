import os
import mysql.connector
from src.utils import containers
from src.utils.exceptions import UserNotFoundException, MalformedUserException
import logging
import bcrypt
from typing import NoReturn
from src.utils.app_utils import load_app_info

class connect:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.environ['DB_HOST'],
                user=os.environ['DB_USER'],
                password=os.environ['DB_PASSWORD'],
                database=os.environ['DB_NAME']
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as e:
            print("Access denied: {}".format(e))
            exit(1)
        except KeyError as e:
            print("Environment variable not found: {}".format(e))
            raise SystemError
        except Exception as e:
            print("Error: {}".format(e))
            exit(1)

    def get_all_finances(self) -> list:
        return_list = []
        invoice_sql = """
            SELECT a.seq, a.id, concat(b.first_name, ' ', b.last_name),
            concat(c.first_name, ' ', c.last_name), d.stat_desc, e.type_desc,
            a.tax, fees, a.dt_added, a.dt_updated,
            concat(f.first_name, ' ', f.last_name),
            concat(g.first_name, ' ', g.last_name), inv_date FROM inv_head a, users b,
            users c, statuses d, record_types e, users f, users g WHERE
            a.creator = b.seq AND a.approver = c.seq AND
            a.record_status = d.seq AND a.record_type = e.seq AND
            a.added_by = f.seq AND a.updated_by = g.seq;"""
        self.cursor.execute(invoice_sql)
        rows = self.cursor.fetchall()
        line_sql = """
        SELECT a.inv_seq, a.line_id, b.item_desc, b.item_price, a.qty,
        concat(c.first_name, ' ', c.last_name), 
        concat(d.first_name, ' ', d.last_name),
        a.dt_added, a.dt_updated FROM
        inv_line a, valid_items b, users c, users d WHERE
        a.inv_seq = %s AND a.item_seq = b.seq AND a.added_by = c.seq
        AND a.updated_by = d.seq"""
        for row in rows:
            self.cursor.execute(line_sql, (row[0],))
            lines = self.cursor.fetchall()
            row_container = containers.finance(row, lines)
            return_list.append(row_container.__dict__)
        
        return return_list
    
    def send_password_reset(self, user: containers.User):
        pass

    def get_all_items(self, inv_date):
        sql = "SELECT seq, id, item_desc, item_price, item_type FROM valid_items where effective_start < %s and effective_end > %s"
        self.cursor.execute(sql, (inv_date, inv_date))
        return self.cursor.fetchall()

    def save_user(self, user: containers.User):
        ((user_seq, user_val), (perms_seq, perms_val)) = user.sql()
        self.cursor.execute(user_seq, user_val)
        self.connection.commit()
        user_seq = self.cursor.lastrowid
        perms_val[0] = user_seq
        self.cursor.execute(perms_seq, perms_val)
        self.connection.commit()
        # Send Password Reset Email if not a system user
        if not user.system_user:
            self.send_password_reset(user.email)
            
    def get_user_by_seq(self, user_seq: int) -> containers.User:
        user_sql = """SELECT seq, user_name,
        first_name, last_name, email, system_user, theme, added_by,
        updated_by, dt_added, dt_updated FROM users WHERE seq = %s"""
        self.cursor.execute(user_sql, (user_seq,))
        user = self.cursor.fetchone()
        if user is None:
            raise UserNotFoundException
        self.cursor.fetchall() # flush the cursor
        perms_sql = """SELECT seq, inv_edit, inv_view,
        doc_edit, doc_view, inv_admin, doc_admin, approve_invoices,
        receive_emails, user_admin, added_by, updated_by, dt_added,
        dt_updated
        FROM permissions WHERE user_seq = %s"""
        self.cursor.execute(perms_sql, (user_seq,))
        perms = self.cursor.fetchone()
        if perms is None:
            raise MalformedUserException
        self.cursor.fetchall() # Flush the cursor
        return containers.User.from_sql(user, perms)
    
    def get_user_by_user_name(self, user_name: str) -> containers.User:
        user_sql = """SELECT seq, user_name,
        first_name, last_name, email, system_user, theme, added_by,
        updated_by, dt_added, dt_updated FROM users WHERE user_name = %s"""
        self.cursor.execute(user_sql, (user_name,))
        user = self.cursor.fetchone()
        if user is None:
            raise UserNotFoundException
        self.cursor.fetchall() # flush the cursor
        perms_sql = """SELECT seq, inv_edit, inv_view,
        doc_edit, doc_view, inv_admin, doc_admin, approve_invoices,
        receive_emails, user_admin, added_by, updated_by, dt_added,
        dt_updated
        FROM permissions WHERE user_seq = %s"""
        self.cursor.execute(perms_sql, (user[0],))
        perms = self.cursor.fetchone()
        if perms is None:
            raise MalformedUserException
        self.cursor.fetchall() # flush the cursor
        return containers.User.from_sql(user, perms)
    
    def check_user_valid(self, username: str, password: str) -> containers.User:
        sql = "SELECT seq, user_name, password FROM users WHERE user_name = %s"
        self.cursor.execute(sql, (username,))
        results = self.cursor.fetchall()
        if len(results) != 1:
            return (False, "", "")
        
        (user_seq, user_id, hashed_pass) = results[0]
        if hashed_pass is None:
            return (False, "", "")
        
        if not bcrypt.checkpw(password.encode('utf-8'), hashed_pass.encode('utf-8')):
            return (False, "", "")
        
        return (True, user_seq, user_id)
    
    def is_user_admin(self, user_seq: int) -> bool:
        sql = "SELECT user_admin FROM permissions WHERE user_seq = %s"
        self.cursor.execute(sql, (user_seq,))
        results = self.cursor.fetchall()
        if len(results) != 1:
            return False
        return results[0][0]
    
    def can_user_view_finances(self, user_seq: int) -> bool | NoReturn:
        sql = "SELECT inv_view, inv_admin FROM permissions WHERE user_seq = %s"
        self.cursor.execute(sql, (user_seq,))
        results = self.cursor.fetchall()
        if len(results) != 1:
            return False
        return results[0][0] == 1 or results[0][1] == 1
        
    def get_all_statuses(self) -> list:
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
        valid_statuses = self.get_all_statuses()
        sql = """
        SELECT a.seq, a.id, concat(b.first_name, ' ', b.last_name),
            concat(c.first_name, ' ', c.last_name), d.stat_desc, e.type_desc,
            a.tax, fees, a.dt_added, a.dt_updated,
            concat(f.first_name, ' ', f.last_name),
            concat(g.first_name, ' ', g.last_name), inv_date FROM inv_head a, users b,
            users c, statuses d, record_types e, users f, users g WHERE
            a.creator = b.seq AND a.approver = c.seq AND
            a.record_status = d.seq AND a.record_type = e.seq AND
            a.added_by = f.seq AND a.updated_by = g.seq"""
        status_filters_include = []
        status_filters_exclude = []
        for status in valid_statuses:
            should_filter = filter_data["status"].get(status, False)
            if should_filter:
                status_filters_include.append(f"d.stat_desc = '{status}'")
            else:
                status_filters_exclude.append(f"d.stat_desc != '{status}'")
        
        type_filters_include = []
        type_filters_exclude = []
        for current_type in valid_types:
            should_filter = filter_data["types"].get(current_type, False)
            if should_filter:
                type_filters_include.append(f"e.type_desc = '{current_type}'")
            else:
                type_filters_exclude.append(f"e.type_desc != '{current_type}'")
        
        status_include_sql = " OR ".join(status_filters_include)
        status_exclude_sql = " AND ".join(status_filters_exclude)
        
        type_include_sql = " OR ".join(type_filters_include)
        type_exclude_sql = " AND ".join(type_filters_exclude)
        
        if status_include_sql:
            sql += f" AND ({status_include_sql})"
        
        if status_exclude_sql:
            sql += f" AND ({status_exclude_sql})"
        
        if type_include_sql:
            sql += f" AND ({type_include_sql})"
            
        if type_exclude_sql:
            sql += f" AND ({type_exclude_sql})"
        
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        line_sql = """
        SELECT a.inv_seq, a.line_id, b.item_desc, b.item_price, a.qty,
        concat(c.first_name, ' ', c.last_name), 
        concat(d.first_name, ' ', d.last_name),
        a.dt_added, a.dt_updated FROM
        inv_line a, valid_items b, users c, users d WHERE
        a.inv_seq = %s AND a.item_seq = b.seq AND a.added_by = c.seq
        AND a.updated_by = d.seq"""
        for row in rows:
            self.cursor.execute(line_sql, (row[0],))
            lines = self.cursor.fetchall()
            row_container = containers.finance(row, lines)
            return_list.append(row_container.__dict__)
        
        return return_list
    
    def get_record_by_seq(self, seq):
        SQL = """
        SELECT a.seq, a.id, concat(b.first_name, ' ', b.last_name),
            concat(c.first_name, ' ', c.last_name), d.stat_desc, e.type_desc,
            a.tax, fees, a.dt_added, a.dt_updated,
            concat(f.first_name, ' ', f.last_name),
            concat(g.first_name, ' ', g.last_name), inv_date FROM inv_head a, users b,
            users c, statuses d, record_types e, users f, users g WHERE
            a.creator = b.seq AND a.approver = c.seq AND
            a.record_status = d.seq AND a.record_type = e.seq AND
            a.added_by = f.seq AND a.updated_by = g.seq
            AND a.seq = %s"""
        self.cursor.execute(SQL, (seq,))
        rows = self.cursor.fetchall()[0]
        line_sql = """
        SELECT a.inv_seq, a.line_id, b.item_desc, b.item_price, a.qty,
        concat(c.first_name, ' ', c.last_name), 
        concat(d.first_name, ' ', d.last_name),
        a.dt_added, a.dt_updated FROM
        inv_line a, valid_items b, users c, users d WHERE
        a.inv_seq = %s AND a.item_seq = b.seq AND a.added_by = c.seq
        AND a.updated_by = d.seq"""
        self.cursor.execute(line_sql, (seq,))
        lines = self.cursor.fetchall()
        row_container = containers.finance(rows, lines)
        return row_container.__dict__
    
    def get_user_by_full_name(self, full_name: str) -> int:
        sql = "SELECT seq FROM users WHERE concat(first_name, ' ', last_name) = %s"
        self.cursor.execute(sql, (full_name,))
        return self.cursor.fetchone()[0]
    
    def get_type_seq(self, type_desc: str) -> int:
        sql = "SELECT seq FROM record_types WHERE type_desc = %s"
        self.cursor.execute(sql, (type_desc,))
        return self.cursor.fetchone()[0]
    
    def get_status_seq(self, status_desc: str) -> int:
        sql = "SELECT seq FROM statuses WHERE stat_desc = %s"
        self.cursor.execute(sql, (status_desc,))
        return self.cursor.fetchone()[0]
    
    def get_item_seq(self, item_info: dict, eff_date: str) -> int:
        sql = """SELECT seq FROM valid_items WHERE
                item_desc = %s AND effective_start < %s 
                and effective_end > %s"""
        values = (item_info['item_desc'], eff_date, eff_date)
        self.cursor.execute(sql, values)
        return self.cursor.fetchone()[0]
    
    def create_record(self, record_data: dict, user: containers.User):
        sql = """INSERT INTO inv_head (id, creator, approver, inv_date,
        record_status, record_type, tax, fees, added_by, updated_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        creator = self.get_user_by_full_name(record_data['header']['creator'])
        approver = self.get_user_by_full_name(record_data['header']['approver'])
        record_type = self.get_type_seq(record_data['header']['type'])
        status_type = self.get_status_seq(record_data['header']['status'])
        
        values = (record_data['header']['id'], creator, approver, record_data['header']['inv_date'],
                  record_type, status_type,
                  record_data['header']['tax'], record_data['header']['fees'], user.seq,
                  user.seq)
        self.cursor.execute(sql, values)
        self.connection.commit()
        record_seq = self.cursor.lastrowid
        for line in record_data['lines']:
            sql = """INSERT INTO inv_line (inv_seq, line_id, item_seq, qty, added_by, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s)"""
            item_seq = self.get_item_seq(line,record_data['header']['inv_date'])
            values = (record_seq, line['line_id'], item_seq, line['qty'], user.seq, user.seq)
            self.cursor.execute(sql, values)
            self.connection.commit()
        
    def check_invoice_info(self, user_full_name: str, user_pin: str) -> tuple:
        sql = """SELECT a.seq, a.user_name, a.invoicePin, a.first_name, a.last_name,
        b.inv_admin, b.inv_edit, b.approve_invoices FROM users a, permissions b WHERE
        a.seq = b.user_seq and concat(a.first_name, ' ', a.last_name) = %s"""
        self.cursor.execute(sql, (user_full_name,))
        user = self.cursor.fetchone()
        if user is None:
            return (False, False, False)
        if user[2] != user_pin:
            return (False, False, False)
        return (user[5] == 1, user[6] == 1, user[7] == 1)

    def get_all_invoice_users(self):
        sql = """SELECT a.seq, concat(a.first_name, ' ', a.last_name) 
        FROM users a, permissions b WHERE system_user = 0 AND
        a.seq = b.user_seq and (b.inv_admin = 1 or b.inv_edit = 1)"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def get_all_approvers(self):
        sql = """SELECT a.seq, concat(a.first_name, ' ', a.last_name) 
        FROM users a, permissions b WHERE
        a.seq = b.user_seq and (b.inv_admin = 1 or b.approve_invoices = 1) ORDER BY a.seq"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def get_lines(self, seq):
        sql = """SELECT a.line_id, b.item_desc, a.qty FROM inv_line a, valid_items b
        WHERE a.item_seq = b.seq AND a.inv_seq = %s"""
        self.cursor.execute(sql, (seq,))
        return self.cursor.fetchall()
    
    def edit_record(self, seq: int, data: dict):
        sql = """UPDATE inv_head SET id = %s, creator = %s, approver = %s,
        inv_date = %s, record_status = %s, record_type = %s, tax = %s,
        fees = %s, updated_by = %s WHERE seq = %s"""
        creator = self.get_user_by_full_name(data['header']['creator'])
        approver = self.get_user_by_full_name(data['header']['approver'])
        record_type = self.get_type_seq(data['header']['type'])
        status_type = self.get_status_seq(data['header']['status'])
        values = (data['header']['id'], creator, approver, data['header']['inv_date'],
                  record_type, status_type,
                  data['header']['tax'], data['header']['fees'], data['header']['updated_by'], seq)
        self.cursor.execute(sql, values)
        self.connection.commit()
        existing_line_ids = [x[0] for x in self.get_lines(seq)]
        for line in data['lines']:
            if line['line_id'] in existing_line_ids:
                sql = """UPDATE inv_line SET line_id = %s, item_seq = %s, qty = %s, updated_by = %s
                WHERE inv_seq = %s AND line_id = %s"""
                item_seq = self.get_item_seq(line, data['header']['inv_date'])
                values = (line['line_id'], item_seq, line['qty'], data['header']['updated_by'], seq, line['line_id'])
                self.cursor.execute(sql, values)
                self.connection.commit()
            else:
                sql = """INSERT INTO inv_line (inv_seq, line_id, item_seq, qty, added_by, updated_by)
                VALUES (%s, %s, %s, %s, %s, %s)"""
                item_seq = self.get_item_seq(line, data['header']['inv_date'])
                values = (seq, line['line_id'], item_seq, line['qty'], data['header']['updated_by'], data['header']['updated_by'])
                self.cursor.execute(sql, values)
                self.connection.commit()
        
    def get_pending_finances(self):
        return_list = []
        invoice_sql = """
            SELECT a.seq, a.id, concat(b.first_name, ' ', b.last_name),
            concat(c.first_name, ' ', c.last_name), d.stat_desc, e.type_desc,
            a.tax, fees, a.dt_added, a.dt_updated,
            concat(f.first_name, ' ', f.last_name),
            concat(g.first_name, ' ', g.last_name), inv_date FROM inv_head a, users b,
            users c, statuses d, record_types e, users f, users g WHERE
            a.creator = b.seq AND a.approver = c.seq AND
            a.record_status = d.seq AND a.record_type = e.seq AND
            a.added_by = f.seq AND a.updated_by = g.seq AND a.approver = 0 ORDER BY a.seq;"""
        self.cursor.execute(invoice_sql)
        rows = self.cursor.fetchall()
        line_sql = """
        SELECT a.inv_seq, a.line_id, b.item_desc, b.item_price, a.qty,
        concat(c.first_name, ' ', c.last_name), 
        concat(d.first_name, ' ', d.last_name),
        a.dt_added, a.dt_updated FROM
        inv_line a, valid_items b, users c, users d WHERE
        a.inv_seq = %s AND a.item_seq = b.seq AND a.added_by = c.seq
        AND a.updated_by = d.seq"""
        print(invoice_sql)
        for row in rows:
            self.cursor.execute(line_sql, (row[0],))
            lines = self.cursor.fetchall()
            row_container = containers.finance(row, lines)
            return_list.append(row_container.__dict__)
        
        return return_list
    
    def change_preferences(self, target_user: int, current_user: containers.User, new_prefs: dict):
        sql = """UPDATE users SET user_name = %s, theme = %s, email=%s, updated_by = %s WHERE seq = %s"""
        email_domain = load_app_info()['public']['email_domain']
        email = new_prefs.get('email').removesuffix(email_domain)
        self.cursor.execute(sql, (new_prefs.get('uname'), new_prefs.get('theme'), email, current_user.seq, target_user))
        self.connection.commit()
    
    def change_password(self, target_seq: int, current_user: containers.User, new_password: str):
        sql = """UPDATE users SET password = %s, updated_by = %s WHERE seq = %s"""
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        self.cursor.execute(sql, (hashed, current_user.seq, target_seq))
        self.connection.commit()
    
    def change_approver_pin(self, target_seq: int, current_user: containers.User, new_pin: str):
        sql = """UPDATE users SET finance_pin = %s, updated_by = %s WHERE seq = %s"""
    
    def __del__(self):
        self.connection.close()