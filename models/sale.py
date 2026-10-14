from datetime import datetime
from models import db


class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    employee_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    receipt_number = db.Column(db.String(30))
    subtotal = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    payment_method = db.Column(db.String(30), default="cash")
    amount_paid = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("SaleItem", backref="sale", lazy=True, cascade="all, delete-orphan")
    employee = db.relationship("User", foreign_keys=[employee_id])

    @property
    def profit(self):
        return sum(item.line_profit for item in self.items)


class SaleItem(db.Model):
    __tablename__ = "sale_items"

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, default=0)
    line_total = db.Column(db.Float, nullable=False)

    product = db.relationship("Product")

    @property
    def line_profit(self):
        return self.line_total - (self.unit_cost * self.quantity)
