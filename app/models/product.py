from datetime import datetime
from app.utils import db


class OrderProduct(db.Model):
    """Association model for orders and products, with quantity."""
    __tablename__ = 'order_products'

    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    quantity   = db.Column(db.Integer, nullable=False, default=1)

    # Relationships back to Order and Product
    order   = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')


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

    # Relationship to OrderProduct
    order_items = db.relationship('OrderProduct', back_populates='product')

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
