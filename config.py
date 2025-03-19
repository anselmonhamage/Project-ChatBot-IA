import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

server = os.environ.get("MSSQL_SERVER")
database = os.environ.get("MSSQL_DB")
driver = os.environ.get("MSSQL_DRIVER")
secret_key = os.environ.get("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://{server}/{database}?driver={driver}"
REMEMBER_COOKIE_DURATION = timedelta(days=30)
SQLALCHEMY_TRACK_MODIFICATION = False
SECRET_KEY = secret_key