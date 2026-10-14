from datetime import datetime
from models import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(150))
    address = db.Column(db.String(255))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)

    sales = db.relationship("Sale", backref="customer", lazy=True)
    debts = db.relationship("Debt", backref="customer", lazy=True, cascade="all, delete-orphan")

    @property
    def total_purchases(self):
        return sum(sale.total_amount for sale in self.sales)

    @property
    def outstanding_balance(self):
        return sum(debt.balance for debt in self.debts if debt.balance > 0)
