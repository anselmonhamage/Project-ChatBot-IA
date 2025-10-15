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
    profile_image = db.Column(db.Text, nullable=True)

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
    
    chat_history = db.relationship('ChatHistory', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')

    def __init__(self, name, email, password, tel, profile_image=None):
        self.name = name
        self.email = email
        self.password = password
        self.tel = tel
        self.profile_image = profile_image
        
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


class ChatHistory(TimeStampedModel, db.Model):
    """Modelo para armazenar histórico de conversas
    Preparado para migração futura para Redis
    """
    __tablename__ = "chat_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    model_used = db.Column(db.String(50), nullable=True)
    service_type = db.Column(db.String(20), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    
    user = db.relationship("User", back_populates="chat_history")

    def __init__(self, user_id, message, response=None, model_used=None, service_type=None, session_id=None):
        self.user_id = user_id
        self.message = message
        self.response = response
        self.model_used = model_used
        self.service_type = service_type
        self.session_id = session_id

    def to_dict(self):
        """Serializa para dict (facilita migração para Redis)"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'response': self.response,
            'model_used': self.model_used,
            'service_type': self.service_type,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"{self.__class__.__name__}, id: {self.id}, user: {self.user_id}"
    