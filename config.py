import os

from dotenv import load_dotenv

load_dotenv()

server = os.environ.get("MSSQL_SERVER")
database = os.environ.get("MSSQL_DB")
driver = os.environ.get("MSSQL_DRIVER")
secret_key = os.environ.get("SECRET_KEY")

# configurações de conexão
server = server
database = database
driver = driver

SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://{server}/{database}?driver={driver}"

SQLALCHEMY_TRACK_MODIFICATION = False

SECRET_KEY = secret_key