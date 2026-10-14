from datetime import datetime, timedelta
from collections import defaultdict
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, Sale, SaleItem, Expense, Product, Debt

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    business_id = current_user.business_id
    today = datetime.utcnow().date()

    today_sales = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
        Sale.business_id == business_id, func.date(Sale.created_at) == today
    ).scalar()

    today_expenses = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.business_id == business_id, Expense.expense_date == today
    ).scalar()

    today_profit = today_sales - today_expenses

    outstanding_debts = db.session.query(func.coalesce(func.sum(Debt.balance), 0)).filter(
        Debt.business_id == business_id, Debt.status == "open"
    ).scalar()

    products = Product.query.filter_by(business_id=business_id, status="active").all()
    low_stock_items = sum(1 for p in products if p.is_low_stock)
    total_products = len(products)

    trend_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    trend_labels = [d.strftime("%a") for d in trend_days]

    sales_trend, expense_trend, profit_trend = [], [], []
    for d in trend_days:
        day_sales = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.business_id == business_id, func.date(Sale.created_at) == d
        ).scalar()
        day_expenses = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.business_id == business_id, Expense.expense_date == d
        ).scalar()
        sales_trend.append(round(day_sales, 2))
        expense_trend.append(round(day_expenses, 2))
        profit_trend.append(round(day_sales - day_expenses, 2))

    top_products_query = (
        db.session.query(SaleItem.product_name, func.sum(SaleItem.quantity).label("qty"))
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(Sale.business_id == business_id)
        .group_by(SaleItem.product_name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(5)
        .all()
    )
    top_products_labels = [row[0] for row in top_products_query]
    top_products_values = [int(row[1]) for row in top_products_query]

    payment_query = (
        db.session.query(Sale.payment_method, func.sum(Sale.total_amount))
        .filter(Sale.business_id == business_id)
        .group_by(Sale.payment_method)
        .all()
    )
    payment_labels = [row[0] for row in payment_query]
    payment_values = [round(row[1], 2) for row in payment_query]

    expense_cat_query = (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .filter(Expense.business_id == business_id)
        .group_by(Expense.category)
        .all()
    )
    expense_cat_labels = [row[0] for row in expense_cat_query]
    expense_cat_values = [round(row[1], 2) for row in expense_cat_query]

    return render_template(
        "dashboard.html",
        today_sales=today_sales,
        today_expenses=today_expenses,
        today_profit=today_profit,
        outstanding_debts=outstanding_debts,
        low_stock_items=low_stock_items,
        total_products=total_products,
        trend_labels=trend_labels,
        sales_trend=sales_trend,
        expense_trend=expense_trend,
        profit_trend=profit_trend,
        top_products_labels=top_products_labels,
        top_products_values=top_products_values,
        payment_labels=payment_labels,
        payment_values=payment_values,
        expense_cat_labels=expense_cat_labels,
        expense_cat_values=expense_cat_values,
        low_stock_products=[p for p in products if p.is_low_stock][:5],
    )
