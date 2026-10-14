from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Business, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        business_name = request.form.get("business_name", "").strip()
        owner_name = request.form.get("owner_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        business_type = request.form.get("business_type", "").strip()
        location = request.form.get("location", "").strip()
        currency = request.form.get("currency", "KES").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([business_name, owner_name, email, password]):
            flash("Please fill in all required fields.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        business = Business(
            name=business_name,
            business_type=business_type,
            phone=phone,
            email=email,
            location=location,
            currency=currency or "KES",
        )
        db.session.add(business)
        db.session.flush()

        user = User(
            business_id=business.id,
            full_name=owner_name,
            email=email,
            phone=phone,
            role="owner",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome to Zanite, {owner_name}. Your business account is ready.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        if not user.is_active_user:
            flash("This account has been deactivated. Contact your business owner.", "error")
            return render_template("login.html")

        login_user(user, remember=remember)
        return redirect(url_for("dashboard.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
