from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Customer, Debt
from utils.decorators import require_permission

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")


@customers_bp.route("/")
@login_required
@require_permission("customers")
def list_customers():
    business_id = current_user.business_id
    search = request.args.get("q", "").strip()

    query = Customer.query.filter_by(business_id=business_id)
    if search:
        query = query.filter(Customer.name.ilike(f"%{search}%"))

    customers_list = query.order_by(Customer.name).all()
    return render_template("customers.html", customers=customers_list, search=search)


@customers_bp.route("/add", methods=["POST"])
@login_required
@require_permission("customers")
def add_customer():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Customer name is required.", "error")
        return redirect(url_for("customers.list_customers"))

    customer = Customer(
        business_id=current_user.business_id,
        name=name,
        phone=request.form.get("phone", "").strip(),
        email=request.form.get("email", "").strip(),
        address=request.form.get("address", "").strip(),
    )
    db.session.add(customer)
    db.session.commit()
    flash(f"{name} added to customers.", "success")
    return redirect(url_for("customers.list_customers"))


@customers_bp.route("/<int:customer_id>")
@login_required
@require_permission("customers")
def customer_detail(customer_id):
    customer = Customer.query.filter_by(id=customer_id, business_id=current_user.business_id).first_or_404()
    debts = Debt.query.filter_by(customer_id=customer.id).order_by(Debt.created_at.desc()).all()
    return render_template(
        "customer_detail.html", customer=customer, debts=debts, today=datetime.utcnow().date()
    )


@customers_bp.route("/debts")
@login_required
@require_permission("customers")
def debts():
    business_id = current_user.business_id
    debts_list = (
        Debt.query.filter_by(business_id=business_id, status="open")
        .order_by(Debt.created_at.desc())
        .all()
    )
    customers_list = Customer.query.filter_by(business_id=business_id).order_by(Customer.name).all()
    total_outstanding = sum(d.balance for d in debts_list)
    return render_template(
        "debts.html",
        debts=debts_list,
        customers=customers_list,
        total_outstanding=total_outstanding,
        today=datetime.utcnow().date(),
    )


@customers_bp.route("/debts/add", methods=["POST"])
@login_required
@require_permission("customers")
def add_debt():
    business_id = current_user.business_id
    submitted_customer_id = request.form.get("customer_id", type=int)

    if request.form.get("source") == "customer" and submitted_customer_id:
        fallback = url_for("customers.customer_detail", customer_id=submitted_customer_id)
    else:
        fallback = url_for("customers.debts")

    try:
        amount = round(float(request.form.get("amount") or 0), 2)
    except ValueError:
        amount = 0

    if amount <= 0:
        flash("Enter a debt amount greater than zero.", "error")
        return redirect(fallback)

    new_customer_name = request.form.get("new_customer_name", "").strip()
    customer_id = request.form.get("customer_id", type=int)

    if new_customer_name:
        customer = Customer(
            business_id=business_id,
            name=new_customer_name,
            phone=request.form.get("new_customer_phone", "").strip(),
        )
        db.session.add(customer)
        db.session.flush()
    else:
        customer = Customer.query.filter_by(id=customer_id, business_id=business_id).first()

    if customer is None:
        flash("Select a customer or enter a new customer's name.", "error")
        return redirect(fallback)

    due_date = None
    due_raw = request.form.get("due_date", "").strip()
    if due_raw:
        try:
            due_date = datetime.strptime(due_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("The due date is not valid.", "error")
            db.session.rollback()
            return redirect(fallback)

    debt = Debt(
        business_id=business_id,
        customer_id=customer.id,
        original_amount=amount,
        balance=amount,
        due_date=due_date,
        status="open",
    )
    db.session.add(debt)
    db.session.commit()
    flash(f"Debt of {amount:,.2f} recorded for {customer.name}.", "success")
    return redirect(fallback)


@customers_bp.route("/debts/<int:debt_id>/pay", methods=["POST"])
@login_required
@require_permission("customers")
def pay_debt(debt_id):
    debt = Debt.query.filter_by(id=debt_id, business_id=current_user.business_id).first_or_404()
    amount = float(request.form.get("amount") or 0)

    if amount <= 0 or amount > debt.balance:
        flash("Enter a valid payment amount.", "error")
        return redirect(request.referrer or url_for("customers.debts"))

    debt.record_payment(amount, request.form.get("payment_method", "cash"))
    db.session.commit()
    flash("Payment recorded.", "success")
    return redirect(request.referrer or url_for("customers.debts"))