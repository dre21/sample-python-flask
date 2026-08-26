from app.utils import db


class Order(db.Model):
    __tablename__ = 'orders'

    id      = db.Column(db.Integer, primary_key=True)
    total   = db.Column(db.Float, nullable=False)
    status  = db.Column(db.String(20), nullable=True)

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship to OrderProduct (association model)
    order_items = db.relationship('OrderProduct', back_populates='order')

    def to_dict(self):
        return {
            'id':       self.id,
            'total':    self.total,
            'user_id':  self.user_id,
            'products': [
                {
                    'product_id': item.product_id,
                    'quantity':   item.quantity,
                }
                for item in self.order_items
            ],
        }
