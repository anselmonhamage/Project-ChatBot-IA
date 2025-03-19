from flask_login import UserMixin
from app import db

from app.models.base import TimeStampedModel


class User(UserMixin, TimeStampedModel, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tel = db.Column(db.String(15), nullable=True)

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
    
    questions = db.relationship('Question', back_populates='author', passive_deletes=True)
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')

    def __init__(self, name, email, password, tel):
        self.name = name
        self.email = email
        self.password = password
        self.tel = tel
        
    def has_role(self, role):
        return bool(
            Role.query
            .join(Role.users)
            .filter(User.id == self.id)
            .filter(Role.slug == role)
            .count() == 1
        )

    def __repr__(self):
        return f"{self.__class__.__name__}, name: {self.name}: {self.email}"
    

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(36), nullable=False)
    slug = db.Column(db.String(36), nullable=False, unique=True)

    users = db.relationship('User', secondary='user_roles', back_populates='roles')


class UserRole(TimeStampedModel):
    __tablename__ = 'user_roles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)


class Question(db.Model):
    __tablename__= "questions"

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    author = db.relationship("User", back_populates="questions")

    def __init__(self, question_text, answer, user_id):
        self.question_text = question_text
        self.answer = answer
        self.user_id = user_id

    def __repr__(self):
        return f"{self.__class__.__name__}, id: {self.id}"
    