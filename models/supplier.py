from datetime import datetime
from models import db


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    contact_person = db.Column(db.String(150))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(150))
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    purchases = db.relationship("Purchase", backref="supplier", lazy=True, cascade="all, delete-orphan")

    @property
    def total_purchased(self):
        return sum(p.total_cost for p in self.purchases)


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default="paid")  # paid | pending
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")
