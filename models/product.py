from datetime import datetime
from models import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    products = db.relationship("Product", backref="category", lazy=True)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    sku = db.Column(db.String(50))
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255))
    buying_price = db.Column(db.Float, default=0)
    selling_price = db.Column(db.Float, nullable=False, default=0)
    current_stock = db.Column(db.Integer, default=0)
    minimum_stock_level = db.Column(db.Integer, default=5)
    image_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default="active")  # active | inactive
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    stock_movements = db.relationship(
        "StockMovement", backref="product", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock_level

    @property
    def stock_value(self):
        return self.current_stock * self.buying_price

    def adjust_stock(self, quantity_change, movement_type, note=None):
        self.current_stock += quantity_change
        movement = StockMovement(
            product_id=self.id,
            movement_type=movement_type,
            quantity=quantity_change,
            note=note,
        )
        db.session.add(movement)


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # sale | purchase | adjustment
    quantity = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
