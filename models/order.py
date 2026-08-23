from utils import db
from models.product import order_products


class Order(db.Model):
    __tablename__ = 'orders'

    id      = db.Column(db.Integer, primary_key=True)
    total   = db.Column(db.Float, nullable=False)
    status  = db.Column(db.String(20), nullable=True)

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Many-to-many relationship with products
    products = db.relationship('Product', secondary=order_products, backref='orders')

    def to_dict(self):
        return {
            'id':       self.id,
            'total':    self.total,
            'user_id':  self.user_id,
            'products': [product.to_dict() for product in self.products],
        }
