import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

USE_SQLITE = os.environ.get("USE_SQLITE", "False").lower() == "true"

if USE_SQLITE:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chatbot.db'
    print("🗄️ Usando SQLite para desenvolvimento")
else:
    server = os.environ.get("MSSQL_SERVER")
    database = os.environ.get("MSSQL_DB")
    driver = os.environ.get("MSSQL_DRIVER")
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://{server}/{database}?driver={driver}"
    print(f"🗄️ Usando SQL Server: {server}/{database}")

secret_key = os.environ.get("SECRET_KEY")

REMEMBER_COOKIE_DURATION = timedelta(days=30)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = secret_key

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "app/static/uploads")
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16777216))  # 16MB (tamanho máximo de arquivo)