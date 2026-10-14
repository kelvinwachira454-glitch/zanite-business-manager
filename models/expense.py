from datetime import datetime
from models import db


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(30), default="cash")
    payee = db.Column(db.String(150))
    notes = db.Column(db.String(255))
    expense_date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    EXPENSE_CATEGORIES = [
        "Rent", "Electricity", "Water", "Transport", "Salaries",
        "Stock Purchases", "Internet", "Marketing", "Repairs", "Licenses", "Other",
    ]
