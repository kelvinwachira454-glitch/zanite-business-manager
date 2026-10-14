import json
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Product, Sale, SaleItem, Customer, Debt
from utils.decorators import require_permission

sales_bp = Blueprint("sales", __name__, url_prefix="/sales")


@sales_bp.route("/new")
@login_required
@require_permission("sales")
def new_sale():
    business_id = current_user.business_id
    products = Product.query.filter_by(business_id=business_id, status="active").order_by(Product.name).all()
    customers = Customer.query.filter_by(business_id=business_id).order_by(Customer.name).all()
    return render_template("new_sale.html", products=products, customers=customers)


@sales_bp.route("/new", methods=["POST"])
@login_required
@require_permission("sales")
def create_sale():
    business_id = current_user.business_id
    cart = json.loads(request.form.get("cart_data", "[]"))

    if not cart:
        flash("Cannot complete a sale with an empty cart.", "error")
        return redirect(url_for("sales.new_sale"))

    customer_id = request.form.get("customer_id", type=int) or None
    payment_method = request.form.get("payment_method", "cash")
    discount = float(request.form.get("discount") or 0)
    amount_paid_raw = request.form.get("amount_paid")

    subtotal = 0
    sale_items = []
    for entry in cart:
        product = Product.query.filter_by(id=entry["product_id"], business_id=business_id).first()
        if not product:
            continue
        quantity = int(entry["quantity"])
        if quantity > product.current_stock:
            flash(f"Not enough stock for {product.name}. Available: {product.current_stock}.", "error")
            return redirect(url_for("sales.new_sale"))
        line_total = quantity * product.selling_price
        subtotal += line_total
        sale_items.append((product, quantity, line_total))

    total_amount = max(0, subtotal - discount)
    amount_paid = float(amount_paid_raw) if amount_paid_raw not in (None, "") else total_amount
    if payment_method == "credit" and amount_paid_raw in (None, ""):
        amount_paid = 0
    balance = max(0, total_amount - amount_paid)

    last_sale = Sale.query.filter_by(business_id=business_id).order_by(Sale.id.desc()).first()
    next_number = (last_sale.id + 1) if last_sale else 1

    sale = Sale(
        business_id=business_id,
        customer_id=customer_id,
        employee_id=current_user.id,
        receipt_number=f"#{next_number:06d}",
        subtotal=subtotal,
        discount=discount,
        total_amount=total_amount,
        payment_method=payment_method,
        amount_paid=amount_paid,
        balance=balance,
    )
    db.session.add(sale)
    db.session.flush()

    for product, quantity, line_total in sale_items:
        db.session.add(SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.selling_price,
            unit_cost=product.buying_price,
            line_total=line_total,
        ))
        product.adjust_stock(-quantity, "sale", f"Sale {sale.receipt_number}")

    if balance > 0:
        if not customer_id:
            flash("A customer must be selected to record a balance as debt.", "error")
            db.session.rollback()
            return redirect(url_for("sales.new_sale"))
        db.session.add(Debt(
            business_id=business_id,
            customer_id=customer_id,
            sale_id=sale.id,
            original_amount=balance,
            balance=balance,
        ))

    db.session.commit()
    flash(f"Sale {sale.receipt_number} completed.", "success")
    return redirect(url_for("sales.receipt", sale_id=sale.id))


@sales_bp.route("/history")
@login_required
@require_permission("sales")
def history():
    business_id = current_user.business_id
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    query = Sale.query.filter_by(business_id=business_id)
    if date_from:
        query = query.filter(Sale.created_at >= datetime.strptime(date_from, "%Y-%m-%d"))
    if date_to:
        query = query.filter(Sale.created_at <= datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S").replace(hour=23, minute=59, second=59) if " " in date_to else datetime.strptime(date_to + " 23:59:59", "%Y-%m-%d %H:%M:%S"))

    sales_list = query.order_by(Sale.created_at.desc()).all()
    return render_template("sales_history.html", sales=sales_list, date_from=date_from, date_to=date_to)


@sales_bp.route("/<int:sale_id>/receipt")
@login_required
@require_permission("sales")
def receipt(sale_id):
    sale = Sale.query.filter_by(id=sale_id, business_id=current_user.business_id).first_or_404()
    return render_template("receipt.html", sale=sale)
