from datetime import datetime
from utils import db


class Product(db.Model):
    __tablename__ = 'products'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    sku         = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    price       = db.Column(db.Float, nullable=False)
    stock_qty   = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.now)

    def show_detail(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'sku':         self.sku,
            'description': self.description,
            'price':       self.price,
            'stock_qty':   self.stock_qty,
            'is_active':   self.is_active,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
        }

    def show_list(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'sku':         self.sku,
            'price':       self.price,
            'stock_qty':   self.stock_qty,
            'is_active':   self.is_active                
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(20), server_default='user')  # Added role field with default value
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        # TODO: Return dict WITHOUT password_hash
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }