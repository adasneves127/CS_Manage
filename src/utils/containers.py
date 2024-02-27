from src.utils.app_utils import load_app_info

class finance:
    def __init__(self, header: tuple, lines: list):
        self.header = {
            "seq": header[0],
            "id": header[1],
            "creator": header[2],
            "approver": header[3],
            "status": header[4],
            "type": header[5],
            "tax": header[6],
            "fees": header[7],
            "dt_added": header[8],
            "dt_updated": header[9],
            "added_by": header[10],
            "updated_by": header[11],
            "total": 0
        }
        self.lines = []
        for line in lines:
            self.lines.append(
                {
                    "seq": line[0],
                    "line_id": line[1],
                    "item_desc": line[2],
                    "item_price": line[3],
                    "qty": line[4],
                    "added_by": line[5],
                    "updated_by": line[6],
                    "dt_added": line[7],
                    "dt_updated": line[8]
                }
            )
            self.header['total'] += (line[3] * line[4])
            
    def __str__(self):
        return "Header: {}\nLines: {}".format(self.header, self.lines)
    
    def __repr__(self):
        return "[Finance] Header: {}\nLines: {}".format(self.header, self.lines)
    
    
class User:
    def __init__(self,
                 user_name: str, first_name: str, last_name: str, email: str,
                 is_system_user: bool = False, **kwargs):
        self.user_name = user_name
        self.first_name = first_name
        self.last_name = last_name
        self.system_user = is_system_user
        app_info = load_app_info()
        self.email = email.removesuffix(app_info['email_domain'])
        for(k, v) in kwargs.items():
            setattr(self, k, v)
        
        
    @staticmethod
    def create_user():
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        email = input("Email: ")
        user_name = email.split('@')[0]
        is_system_user = input("System User? (y/n): ").lower() == 'y'
        if is_system_user:
            return User(user_name, first_name, last_name, email, is_system_user)
        # Get Permissions
        is_system_admin = input("System Admin? (y/n): ").lower() == 'y'
        if is_system_admin:
            return User(user_name, first_name, last_name, email, is_system_user, system_admin=True)
        print("Permissions: ")
        print("\t Finance Settings")
        inv_edit = input("\t Edit Records (y/n): ").lower() == 'y'
        inv_view = input("\t View Records (y/n): ").lower() == 'y'
        inv_admin = input("\t Admin (y/n): ").lower() == 'y'
        approve_invoices = input("\t Approve Records (y/n): ").lower() == 'y'
        print("\t Docket")
        doc_edit = input("\t Edit Docket (y/n): ").lower() == 'y'
        doc_view = input("\t View Docket (y/n): ").lower() == 'y'
        doc_admin = input("\t Admin (y/n): ").lower() == 'y'
        print("\t App Settings")
        receive_emails = input("\t Receive Emails (y/n): ").lower() == 'y'
        return User(user_name, first_name, last_name, email, is_system_user, 0,
                    inv_edit=inv_edit, inv_view=inv_view, inv_admin=inv_admin,
                    approve_invoices=approve_invoices, doc_edit=doc_edit, doc_view=doc_view,
                    doc_admin=doc_admin, receive_emails=receive_emails)
        
    
    def sql(self):
        values = self.__dict__
        user_sql = """
        INSERT INTO users (seq, user_name, first_name, last_name, email, system_user,
        added_by, updated_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        user_vals = (1, values.get('user_name'), values.get('first_name'),
                        values.get('last_name'), values.get('email'),
                        values.get('system_user', False), 1, 1)
        
        perms_sql = """
        INSERT INTO permissions (user_seq, inv_edit, inv_view, doc_edit, doc_view,
        inv_admin, doc_admin, approve_invoices, receive_emails, user_admin,
        added_by, updated_by) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        perms_vals = [1, False, False, False, False, False, False, False, False, values.get('system_admin'), 1, 1]
        return ((user_sql, user_vals), (perms_sql, perms_vals))
    
    @staticmethod
    def from_sql(user_info, permissions):
        user = User(user_info[1], user_info[2], user_info[3], user_info[4], user_info[5])
        user.seq = user_info[0]
        user.theme = user_info[6]
        user.added_by = user_info[7]
        user.updated_by = user_info[8]
        user.dt_added = user_info[9]
        user.dt_updated = user_info[10]
        user.inv_edit = permissions[1]
        user.inv_view = permissions[2]
        user.doc_edit = permissions[3]
        user.doc_view = permissions[4]
        user.inv_admin = permissions[5]
        user.doc_admin = permissions[6]
        user.approve_invoices = permissions[7]
        user.receive_emails = permissions[8]
        user.user_admin = permissions[9]
        return user
    
    def __str__(self) -> str:
        attrs = self.__dict__
        return "{" + ", ".join([f"{k}: {v}" for (k, v) in attrs.items() if not k.startswith('_')]) + "]"
    
    def __repr__(self) -> str:
        return f"""[USER]{self.__str__()}"""