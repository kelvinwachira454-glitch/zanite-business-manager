from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from models import db, User

employees_bp = Blueprint("employees", __name__, url_prefix="/employees")

AVAILABLE_PERMISSIONS = [
    ("sales", "Record Sales"),
    ("inventory", "Manage Inventory"),
    ("expenses", "Record Expenses"),
    ("customers", "Manage Customers"),
    ("reports", "View Reports"),
]


def _require_owner():
    if current_user.role != "owner":
        abort(403)


@employees_bp.route("/")
@login_required
def list_employees():
    _require_owner()
    employees = User.query.filter_by(business_id=current_user.business_id).order_by(User.role.desc(), User.full_name).all()
    return render_template("employees.html", employees=employees, permissions=AVAILABLE_PERMISSIONS)


@employees_bp.route("/add", methods=["POST"])
@login_required
def add_employee():
    _require_owner()
    email = request.form.get("email", "").strip().lower()
    full_name = request.form.get("full_name", "").strip()
    password = request.form.get("password", "")
    perms = request.form.getlist("permissions")

    if not all([email, full_name, password]):
        flash("Name, email and password are required.", "error")
        return redirect(url_for("employees.list_employees"))

    if User.query.filter_by(email=email).first():
        flash("An account with this email already exists.", "error")
        return redirect(url_for("employees.list_employees"))

    employee = User(
        business_id=current_user.business_id,
        full_name=full_name,
        email=email,
        phone=request.form.get("phone", "").strip(),
        role="employee",
        permissions=",".join(perms),
    )
    employee.set_password(password)
    db.session.add(employee)
    db.session.commit()
    flash(f"{full_name} added as an employee.", "success")
    return redirect(url_for("employees.list_employees"))


@employees_bp.route("/<int:user_id>/toggle-active", methods=["POST"])
@login_required
def toggle_active(user_id):
    _require_owner()
    employee = User.query.filter_by(id=user_id, business_id=current_user.business_id).first_or_404()
    if employee.role == "owner":
        flash("Cannot deactivate the business owner.", "error")
        return redirect(url_for("employees.list_employees"))
    employee.is_active_user = not employee.is_active_user
    db.session.commit()
    flash(f"{employee.full_name} {'activated' if employee.is_active_user else 'deactivated'}.", "success")
    return redirect(url_for("employees.list_employees"))


@employees_bp.route("/<int:user_id>/permissions", methods=["POST"])
@login_required
def update_permissions(user_id):
    _require_owner()
    employee = User.query.filter_by(id=user_id, business_id=current_user.business_id).first_or_404()
    if employee.role == "owner":
        flash("Owner has full access by default.", "error")
        return redirect(url_for("employees.list_employees"))
    employee.permissions = ",".join(request.form.getlist("permissions"))
    db.session.commit()
    flash(f"Permissions updated for {employee.full_name}.", "success")
    return redirect(url_for("employees.list_employees"))
