from app import db
from datetime import datetime, timezone

class TimeStampedModel(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)
    