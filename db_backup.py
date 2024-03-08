from src.utils import db_utils
import dotenv
dotenv.load_dotenv()

db_utils.connect.dump_database()