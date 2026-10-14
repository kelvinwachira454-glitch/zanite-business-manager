import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

ALLOWED_LOGO_EXTENSIONS = {"png", "jpg", "jpeg"}


@settings_bp.route("/")
@login_required
def index():
    if current_user.role != "owner":
        from flask import abort
        abort(403)
    return render_template("settings.html")


@settings_bp.route("/update", methods=["POST"])
@login_required
def update():
    if current_user.role != "owner":
        from flask import abort
        abort(403)

    business = current_user.business
    business.name = request.form.get("name", business.name).strip()
    business.business_type = request.form.get("business_type", business.business_type)
    business.phone = request.form.get("phone", business.phone)
    business.email = request.form.get("email", business.email)
    business.address = request.form.get("address", business.address)
    business.location = request.form.get("location", business.location)
    business.currency = request.form.get("currency", business.currency)
    business.receipt_footer = request.form.get("receipt_footer", business.receipt_footer)
    business.low_stock_threshold = int(request.form.get("low_stock_threshold") or business.low_stock_threshold)

    logo = request.files.get("logo")
    if logo and logo.filename:
        ext = logo.filename.rsplit(".", 1)[-1].lower()
        if ext in ALLOWED_LOGO_EXTENSIONS:
            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
            filename = secure_filename(f"business_{business.id}_logo.{ext}")
            logo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            business.logo_path = f"images/uploads/{filename}"
        else:
            flash("Logo must be a PNG or JPG image.", "error")

    db.session.commit()
    flash("Business settings updated.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_user.check_password(current_password):
        flash("Current password is incorrect.", "error")
        return redirect(url_for("settings.index"))

    if new_password != confirm_password or len(new_password) < 6:
        flash("New passwords must match and be at least 6 characters.", "error")
        return redirect(url_for("settings.index"))

    current_user.set_password(new_password)
    db.session.commit()
    flash("Password updated.", "success")
    return redirect(url_for("settings.index"))
