from src.utils import db_utils
import dotenv
from src.utils.email_utils import send_backup_file
dotenv.load_dotenv()

conn = db_utils.connect()
conn.clear_old_resets()

db_utils.connect.dump_database()
send_backup_file()