from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Expense
from utils.decorators import require_permission

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@expenses_bp.route("/")
@login_required
@require_permission("expenses")
def list_expenses():
    business_id = current_user.business_id
    category = request.args.get("category", "")

    query = Expense.query.filter_by(business_id=business_id)
    if category:
        query = query.filter_by(category=category)

    expenses_list = query.order_by(Expense.expense_date.desc(), Expense.created_at.desc()).all()
    total = sum(e.amount for e in expenses_list)

    return render_template(
        "expenses.html",
        expenses=expenses_list,
        categories=Expense.EXPENSE_CATEGORIES,
        selected_category=category,
        total=total,
    )


@expenses_bp.route("/add", methods=["POST"])
@login_required
@require_permission("expenses")
def add_expense():
    business_id = current_user.business_id
    amount = float(request.form.get("amount") or 0)
    category = request.form.get("category", "Other")

    if amount <= 0:
        flash("Expense amount must be greater than zero.", "error")
        return redirect(url_for("expenses.list_expenses"))

    expense_date_raw = request.form.get("expense_date")
    expense_date = datetime.strptime(expense_date_raw, "%Y-%m-%d").date() if expense_date_raw else datetime.utcnow().date()

    expense = Expense(
        business_id=business_id,
        recorded_by=current_user.id,
        category=category,
        description=request.form.get("description", "").strip(),
        amount=amount,
        payment_method=request.form.get("payment_method", "cash"),
        payee=request.form.get("payee", "").strip(),
        notes=request.form.get("notes", "").strip(),
        expense_date=expense_date,
    )
    db.session.add(expense)
    db.session.commit()
    flash("Expense recorded.", "success")
    return redirect(url_for("expenses.list_expenses"))


@expenses_bp.route("/<int:expense_id>/delete", methods=["POST"])
@login_required
@require_permission("expenses")
def delete_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, business_id=current_user.business_id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect(url_for("expenses.list_expenses"))
