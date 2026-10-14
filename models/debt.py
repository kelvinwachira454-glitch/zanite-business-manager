from datetime import datetime
from models import db


class Debt(db.Model):
    __tablename__ = "debts"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"))
    original_amount = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="open")  # open | paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payments = db.relationship("DebtPayment", backref="debt", lazy=True, cascade="all, delete-orphan")

    def record_payment(self, amount, payment_method="cash", note=None):
        payment = DebtPayment(debt_id=self.id, amount=amount, payment_method=payment_method, note=note)
        db.session.add(payment)
        self.balance = max(0, self.balance - amount)
        if self.balance == 0:
            self.status = "paid"
        return payment


class DebtPayment(db.Model):
    __tablename__ = "debt_payments"

    id = db.Column(db.Integer, primary_key=True)
    debt_id = db.Column(db.Integer, db.ForeignKey("debts.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(30), default="cash")
    note = db.Column(db.String(255))
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
