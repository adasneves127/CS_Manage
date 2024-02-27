import os
import mysql.connector
from src.utils import containers
from src.utils.exceptions import UserNotFoundException, MalformedUserException
import logging


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
            exit(1)
        except Exception as e:
            print("Error: {}".format(e))
            exit(1)

    def get_records(self) -> list:
        return_list = []
        invoice_sql = """
            SELECT a.seq, a.id, concat(b.first_name, ' ', b.last_name),
            concat(c.first_name, ' ', c.last_name), d.stat_desc, e.type_desc,
            a.tax, fees, a.dt_added, a.dt_updated,
            concat(f.first_name, ' ', f.last_name),
            concat(g.first_name, ' ', g.last_name) FROM inv_head a, users b,
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
            return_list.append(row_container)
        
        return row_container
    
    def send_password_reset(self, user: containers.User):
        pass

    def save_user(self, user: containers.User):
        ((user_seq, user_val), (perms_seq, perms_val)) = user.sql()
        print((user_seq, user_val))
        self.cursor.execute(user_seq, user_val)
        self.connection.commit()
        user_seq = self.cursor.lastrowid
        perms_val[0] = user_seq
        print((perms_seq, perms_val))
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
        perms_sql = """SELECT seq, user_seq, inv_edit, inv_view,
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
        perms_sql = """SELECT seq, user_seq, inv_edit, inv_view,
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