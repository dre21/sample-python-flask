from datetime import datetime
from utils import db


# Association table for the many-to-many relationship between Orders and Products
order_products = db.Table(
    'order_products',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)


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

    # Foreign key
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    def show_detail(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'sku':         self.sku,
            'description': self.description,
            'price':       self.price,
            'stock_qty':   self.stock_qty,
            'is_active':   self.is_active,
            'category':    self.category.name if self.category else None,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
        }

    def show_list(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'sku':         self.sku,
            'price':       self.price,
            'stock_qty':   self.stock_qty,
            'category':    self.category.name if self.category else None,
            'is_active':   self.is_active
        }

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'sku':         self.sku,
            'description': self.description,
            'price':       self.price,
            'stock_qty':   self.stock_qty,
            'is_active':   self.is_active,
            'category_id': self.category_id,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
        }
