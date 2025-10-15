from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import os


app = Flask(__name__)
app.config.from_object('config')

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB tamanho máximo de arquivo

db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Configurar CSRF para aceitar JSON
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Desabilitar check automático
app.config['WTF_CSRF_METHODS'] = ['POST', 'PUT', 'PATCH', 'DELETE']

login_manager = LoginManager()
login_manager.init_app(app)

# Configurar CORS para permitir requests locais
cors = CORS()
cors.init_app(app, resources={
    r"/*": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000", "http://0.0.0.0:8000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-CSRFToken"],
        "supports_credentials": True
    }
})

# Handler de erros para endpoints JSON (AJAX)
@app.errorhandler(Exception)
def handle_error(error):
    """Retorna JSON apenas para chamadas AJAX, HTML para páginas web"""
    # Para erros HTTP (404, 403, etc), usar comportamento padrão do Flask
    if isinstance(error, HTTPException):
        return error
    
    # Identificar endpoints que retornam JSON (AJAX)
    is_json_endpoint = (
        request.path.startswith('/api/') or 
        request.path.startswith('/chat/') or
        request.path.startswith('/user/profile') or
        (request.path == '/chatbot' and request.method == 'POST')
    )
    
    if is_json_endpoint:
        response = jsonify({
            "error": str(error),
            "success": False
        })
        response.status_code = 500
        return response
    
    # Para rotas web (templates), deixar Flask tratar normalmente
    raise error

from app.models import tables
from app.controllers import routes
