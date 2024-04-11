from src.utils.db_utils import db_connection
import dotenv
from src.utils.email_utils import send_backup_file
from src.utils.db_utils import connect
dotenv.load_dotenv()

with db_connection() as conn:
    conn.clear_old_resets()

    connect.dump_database()
    send_backup_file()
