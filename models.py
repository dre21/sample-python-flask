from datetime import datetime
from utils import db


class Category(db.Model):
    __tablename__ = 'categories'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)

    # define the relationship to products
    products    = db.relationship('Product', backref='category', lazy=True)

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

# TODO 1: Define the association table using db.Table()
# It needs: order_id (FK → orders.id, PK) and product_id (FK → products.id, PK)
order_products = db.Table(
    'order_products',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key = True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key = True)
)


# TODO 2: Define the Order model
class Order(db.Model):
    __tablename__ = 'orders'
    # YOUR CODE HERE — id, total, user_id columns + products relationship
    id          = db.Column(db.Integer, primary_key=True)
    total       = db.Column(db.Float, nullable=False)

    # Foreign key
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # define the relationship to products 
    products    = db.Relationship('Product', secondary=order_products, backref='orders')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(20), server_default='user')  # Added role field with default value
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # define the relationship to products
    orders    = db.relationship('Order', backref='user', lazy=True)

    def to_dict(self):
        # TODO: Return dict WITHOUT password_hash
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }