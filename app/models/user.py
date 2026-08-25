from datetime import datetime
from app.utils import db


class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    role          = db.Column(db.String(20), server_default='user')
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.now)

    # define the relationship to orders
    orders = db.relationship('Order', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id':         self.id,
            'username':   self.username,
            'role':       self.role,
            'email':      self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
