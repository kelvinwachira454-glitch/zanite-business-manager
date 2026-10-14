from flask import Blueprint, render_template, redirect, url_for, request, flash # type: ignore
from flask_login import login_required, current_user # type: ignore
from models import db, Supplier, Purchase, Product
from utils.decorators import require_permission

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")


@suppliers_bp.route("/")
@login_required
@require_permission("inventory")
def list_suppliers():
    business_id = current_user.business_id
    suppliers = Supplier.query.filter_by(business_id=business_id).order_by(Supplier.name).all()
    products = Product.query.filter_by(business_id=business_id, status="active").order_by(Product.name).all()
    return render_template("suppliers.html", suppliers=suppliers, products=products)


@suppliers_bp.route("/add", methods=["POST"])
@login_required
@require_permission("inventory")
def add_supplier():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Supplier name is required.", "error")
        return redirect(url_for("suppliers.list_suppliers"))

    supplier = Supplier(
        business_id=current_user.business_id,
        name=name,
        contact_person=request.form.get("contact_person", "").strip(),
        phone=request.form.get("phone", "").strip(),
        email=request.form.get("email", "").strip(),
        address=request.form.get("address", "").strip(),
    )
    db.session.add(supplier)
    db.session.commit()
    flash(f"{name} added as a supplier.", "success")
    return redirect(url_for("suppliers.list_suppliers"))


@suppliers_bp.route("/<int:supplier_id>")
@login_required
@require_permission("inventory")
def supplier_detail(supplier_id):
    supplier = Supplier.query.filter_by(id=supplier_id, business_id=current_user.business_id).first_or_404()
    purchases = Purchase.query.filter_by(supplier_id=supplier.id).order_by(Purchase.created_at.desc()).all()
    return render_template("supplier_detail.html", supplier=supplier, purchases=purchases)


@suppliers_bp.route("/<int:supplier_id>/purchase", methods=["POST"])
@login_required
@require_permission("inventory")
def record_purchase(supplier_id):
    supplier = Supplier.query.filter_by(id=supplier_id, business_id=current_user.business_id).first_or_404()
    product = Product.query.filter_by(id=request.form.get("product_id", type=int), business_id=current_user.business_id).first_or_404()

    quantity = int(request.form.get("quantity") or 0)
    unit_cost = float(request.form.get("unit_cost") or 0)

    if quantity <= 0:
        flash("Quantity must be greater than zero.", "error")
        return redirect(url_for("suppliers.supplier_detail", supplier_id=supplier.id))

    purchase = Purchase(
        business_id=current_user.business_id,
        supplier_id=supplier.id,
        product_id=product.id,
        quantity=quantity,
        unit_cost=unit_cost,
        total_cost=quantity * unit_cost,
        payment_status=request.form.get("payment_status", "paid"),
        notes=request.form.get("notes", "").strip(),
    )
    db.session.add(purchase)

    product.buying_price = unit_cost
    product.adjust_stock(quantity, "purchase", f"Purchased from {supplier.name}")

    db.session.commit()
    flash(f"Recorded purchase of {quantity} x {product.name} from {supplier.name}.", "success")
    return redirect(url_for("suppliers.supplier_detail", supplier_id=supplier.id))
