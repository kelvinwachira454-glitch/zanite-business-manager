from flask_sqlalchemy import SQLAlchemy # type: ignore

db = SQLAlchemy()

from models.user import Business, User
from models.product import Category, Product, StockMovement
from models.customer import Customer
from models.debt import Debt, DebtPayment
from models.sale import Sale, SaleItem
from models.expense import Expense
from models.supplier import Supplier, Purchase
