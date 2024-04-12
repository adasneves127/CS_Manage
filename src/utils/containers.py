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
            "inv_date": header[12].strftime("%b, %d %Y"),
            "edit_date": header[12].strftime("%Y-%m-%d"),
            "total": 0,
            "item_count": 0,
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
                    "total": round(line[3] * line[4], 2),
                    "added_by": line[5],
                    "updated_by": line[6],
                    "dt_added": line[7],
                    "dt_updated": line[8],
                }
            )
            self.header["item_count"] += line[4]
            self.header["total"] += line[3] * line[4]
            self.__dict__ = {"header": self.header, "lines": self.lines}
        self.header["total"] += self.header["tax"] + self.header["fees"]
        self.header["total"] = round(self.header["total"], 2)

    def __str__(self):
        return "Header: {}\nLines: {}".format(self.header, self.lines)

    def __repr__(self):
        return "[Finance] Header: {}\nLines: {}"\
            .format(self.header, self.lines)

    @staticmethod
    def from_json(json: dict):
        header_tuple = (
            json["header"]["seq"],
            json["header"]["id"],
            json["header"]["creator"],
            json["header"]["approver"],
            json["header"]["status"],
            json["header"]["type"],
            json["header"]["tax"],
            json["header"]["fees"],
            json["header"]["dt_added"],
            json["header"]["dt_updated"],
            json["header"]["added_by"],
            json["header"]["updated_by"],
            json["header"]["inv_date"],
        )
        line_list = []
        for line in json["lines"]:
            line_list.append(
                (
                    line["seq"],
                    line["line_id"],
                    line["item_desc"],
                    line["item_price"],
                    line["qty"],
                    line["added_by"],
                    line["updated_by"],
                    line["dt_added"],
                    line["dt_updated"],
                )
            )
        return finance(header_tuple, line_list)


class User:
    def __init__(
        self,
        user_name: str,
        first_name: str,
        last_name: str,
        email: str,
        is_system_user: bool = False,
        **kwargs,
    ):
        self.user_name = user_name
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = f"{first_name} {last_name}"
        self.system_user = is_system_user
        app_info = load_app_info()
        self.email = email.removesuffix(app_info["public"]["email_domain"])
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def create_user():
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        email = input("Email: ")
        user_name = email.split("@")[0]
        is_system_user = input("System User? (y/n): ").lower() == "y"
        if is_system_user:
            return User(user_name,
                        first_name,
                        last_name, email,
                        is_system_user)
        # Get Permissions
        is_system_admin = input("System Admin? (y/n): ").lower() == "y"
        if is_system_admin:
            return User(
                user_name,
                first_name,
                last_name,
                email,
                is_system_user,
                system_admin=True,
                inv_edit=True,
                inv_view=True,
                inv_admin=True,
                approve_invoices=True,
                doc_edit=True,
                doc_view=True,
                doc_admin=True,
                receive_emails=True,
            )
        print("Permissions: ")
        print("\t Finance Settings")
        inv_edit = input("\t Edit Records (y/n): ").lower() == "y"
        inv_view = input("\t View Records (y/n): ").lower() == "y"
        inv_admin = input("\t Admin (y/n): ").lower() == "y"
        approve_invoices = input("\t Approve Records (y/n): ").lower() == "y"
        print("\t Docket")
        doc_edit = input("\t Edit Docket (y/n): ").lower() == "y"
        doc_view = input("\t View Docket (y/n): ").lower() == "y"
        doc_admin = input("\t Admin (y/n): ").lower() == "y"
        print("\t App Settings")
        receive_emails = input("\t Receive Emails (y/n): ").lower() == "y"
        return User(
            user_name,
            first_name,
            last_name,
            email,
            is_system_user,
            system_admin=False,
            inv_edit=inv_edit,
            inv_view=inv_view,
            inv_admin=inv_admin,
            approve_invoices=approve_invoices,
            doc_edit=doc_edit,
            doc_view=doc_view,
            doc_admin=doc_admin,
            receive_emails=receive_emails,
        )

    def sql(self):
        values = self.__dict__
        user_sql = """
        INSERT INTO users (seq, user_name, first_name, last_name,
        email, system_user,
        added_by, updated_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        user_vals = (
            2,
            values.get("user_name"),
            values.get("first_name"),
            values.get("last_name"),
            values.get("email"),
            values.get("system_user", False),
            1,
            1,
        )

        perms_sql = """
        INSERT INTO permissions (user_seq, inv_edit, inv_view, doc_edit,
        doc_view, inv_admin, doc_admin, approve_invoices, receive_emails,
        user_admin, added_by, updated_by) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        inv_edit = values.get("inv_edit", False)
        inv_view = values.get("inv_view", False)
        doc_edit = values.get("doc_edit", False)
        doc_view = values.get("doc_view", False)
        inv_admin = values.get("inv_admin", False)
        doc_admin = values.get("doc_admin", False)
        approve_invoices = values.get("approve_invoices", False)
        receive_emails = values.get("receive_emails", False)
        perms_vals = [
            2,
            inv_edit,
            inv_view,
            doc_edit,
            doc_view,
            inv_admin,
            doc_admin,
            approve_invoices,
            receive_emails,
            values.get("system_admin"),
            1,
            1,
        ]
        return ((user_sql, user_vals), (perms_sql, perms_vals))

    @staticmethod
    def from_sql(user_info, permissions, voting):
        user = User(
            user_info[1],
            user_info[2],
            user_info[3],
            user_info[4],
            user_info[5]
        )
        user.seq = user_info[0]
        user.theme = user_info[6]
        user.added_by = user_info[7]
        user.updated_by = user_info[8]
        user.dt_added = user_info[9]
        user.dt_updated = user_info[10]
        user.inv_edit = permissions[1] == 1 or permissions[5] == 1
        user.inv_view = permissions[2] == 1 or permissions[5] == 1
        user.doc_edit = permissions[3] == 1 or permissions[6] == 1
        user.doc_view = permissions[4] == 1 or permissions[6] == 1
        user.inv_admin = permissions[5] == 1
        user.doc_admin = permissions[6] == 1
        user.approve_invoices = permissions[7] == 1
        user.receive_emails = permissions[8] == 1
        user.user_admin = permissions[9] == 1

        user.vote = voting

        return user

    def __str__(self) -> str:
        attrs = self.__dict__
        return (
            "{" + ", ".join(
                [f"{k}: {v}" for (k, v) in attrs.items()
                 if not k.startswith("_")]
            ) + "]"
        )

    def __repr__(self) -> str:
        return f"""[USER]{self.__str__()}"""


class Docket:
    def __init__(
        self,
        title: str,
        description: str,
        creator: User,
        assignees: list,
        dt_added,
        status,
    ):
        self.title = title
        self.desc = description
        self.creator_name = creator.full_name
        self.creator_seq = creator.seq
        self.assignees = assignees
        self.dt_added = dt_added
        self.seq = -1
        self.status = status

    @staticmethod
    def from_sql(
        creator: User,
        docket_info: tuple | list,
        assignees: tuple | list,
        dt_added,
        status,
    ):
        docket = Docket(
            docket_info[1],
            docket_info[2],
            creator.full_name,
            creator.seq,
            assignees,
            dt_added,
            status,
        )
        docket.seq = docket_info[0]
        return docket
