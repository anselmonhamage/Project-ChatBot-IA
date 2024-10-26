import os

from app import app
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get("FLASK_HOST", "0.0.0.0")
port = os.environ.get("FLASK_DEVELOPMENT_PORT", 5000)
debug = os.environ.get("FLASK_DEBUG", False)

if __name__ == "__main__":
    app.run(host=host, port=port)