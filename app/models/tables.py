from flask_login import UserMixin
from app import db


# Podemos fazer a classe User herdar da classe UserMixin para facilitar integração com flask login
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    code_id = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tel = db.Column(db.String(100))

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    questions = db.relationship('Question', backref='author', lazy=True)

    def __init__(self, code_id, password, name, email, tel):
        self.code_id = code_id
        self.password = password
        self.name = name
        self.email = email
        self.tel = tel

    def __repr__(self):
        return f"{self.__class__.__name__}, name: {self.name}: {self.code_id}"

# A Classe que representa a nossa tabela questions em nosso banco de dados
class Question(db.Model):
    __tablename__= "questions"

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, question_text, answer, user_id):
        self.question_text = question_text
        self.answer = answer
        self.user_id = user_id

    def __repr__(self):
        return f"{self.__class__.__name__}, id: {self.id}"
    