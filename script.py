import os 
from dotenv import load_dotenv
import ibm_db
load_dotenv()

try:
    conn = ibm_db.connect(os.getenv('KEY'),'','')
    print("Database connected Successfully")
except Exception as err:
    print("Exception Occurs:",err)