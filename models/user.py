from datetime import datetime
from flask_login import UserMixin # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from models import db


class Business(db.Model):
    __tablename__ = "businesses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    business_type = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(150))
    address = db.Column(db.String(255))
    location = db.Column(db.String(150))
    currency = db.Column(db.String(10), default="KES")
    logo_path = db.Column(db.String(255))
    receipt_footer = db.Column(db.String(255), default="Thank you for shopping with us.")
    low_stock_threshold = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship("User", backref="business", lazy=True, cascade="all, delete-orphan")
    products = db.relationship("Product", backref="business", lazy=True, cascade="all, delete-orphan")
    categories = db.relationship("Category", backref="business", lazy=True, cascade="all, delete-orphan")
    customers = db.relationship("Customer", backref="business", lazy=True, cascade="all, delete-orphan")
    sales = db.relationship("Sale", backref="business", lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship("Expense", backref="business", lazy=True, cascade="all, delete-orphan")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="owner") 
    permissions = db.Column(db.String(255), default="")
    is_active_user = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def has_permission(self, permission):
        if self.role == "owner":
            return True
        return permission in (self.permissions or "").split(",")

    @property
    def is_active(self):
        return self.is_active_user
