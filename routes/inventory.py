from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models import db, Product, Category, StockMovement
from utils.decorators import require_permission

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.route("/products")
@login_required
@require_permission("inventory")
def products():
    business_id = current_user.business_id
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)

    query = Product.query.filter_by(business_id=business_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category_id:
        query = query.filter_by(category_id=category_id)

    products_list = query.order_by(Product.name).all()
    categories = Category.query.filter_by(business_id=business_id).order_by(Category.name).all()

    return render_template(
        "inventory.html", products=products_list, categories=categories, search=search, selected_category=category_id
    )


@inventory_bp.route("/products/add", methods=["POST"])
@login_required
@require_permission("inventory")
def add_product():
    business_id = current_user.business_id

    category_id = request.form.get("category_id", type=int)
    new_category_name = request.form.get("new_category", "").strip()
    if new_category_name:
        category = Category(business_id=business_id, name=new_category_name)
        db.session.add(category)
        db.session.flush()
        category_id = category.id

    product = Product(
        business_id=business_id,
        category_id=category_id,
        sku=request.form.get("sku", "").strip(),
        name=request.form.get("name", "").strip(),
        description=request.form.get("description", "").strip(),
        buying_price=float(request.form.get("buying_price") or 0),
        selling_price=float(request.form.get("selling_price") or 0),
        current_stock=int(request.form.get("initial_stock") or 0),
        minimum_stock_level=int(request.form.get("minimum_stock_level") or 5),
    )

    if not product.name:
        flash("Product name is required.", "error")
        return redirect(url_for("inventory.products"))

    db.session.add(product)
    db.session.flush()

    if product.current_stock > 0:
        db.session.add(
            StockMovement(product_id=product.id, movement_type="purchase", quantity=product.current_stock, note="Initial stock")
        )

    db.session.commit()
    flash(f"{product.name} added to inventory.", "success")
    return redirect(url_for("inventory.products"))


@inventory_bp.route("/products/<int:product_id>/edit", methods=["POST"])
@login_required
@require_permission("inventory")
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id, business_id=current_user.business_id).first_or_404()

    product.name = request.form.get("name", product.name).strip()
    product.sku = request.form.get("sku", product.sku)
    product.description = request.form.get("description", product.description)
    product.buying_price = float(request.form.get("buying_price") or product.buying_price)
    product.selling_price = float(request.form.get("selling_price") or product.selling_price)
    product.minimum_stock_level = int(request.form.get("minimum_stock_level") or product.minimum_stock_level)
    category_id = request.form.get("category_id", type=int)
    if category_id:
        product.category_id = category_id

    db.session.commit()
    flash(f"{product.name} updated.", "success")
    return redirect(url_for("inventory.products"))


@inventory_bp.route("/products/<int:product_id>/adjust-stock", methods=["POST"])
@login_required
@require_permission("inventory")
def adjust_stock(product_id):
    product = Product.query.filter_by(id=product_id, business_id=current_user.business_id).first_or_404()

    quantity = int(request.form.get("quantity") or 0)
    movement_type = request.form.get("movement_type", "adjustment")
    note = request.form.get("note", "").strip()

    if movement_type == "purchase":
        product.adjust_stock(quantity, "purchase", note or "Stock purchase")
    elif movement_type == "adjustment":
        product.adjust_stock(quantity, "adjustment", note or "Manual adjustment")

    db.session.commit()
    flash(f"Stock updated for {product.name}.", "success")
    return redirect(url_for("inventory.products"))


@inventory_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
@require_permission("inventory")
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id, business_id=current_user.business_id).first_or_404()
    product.status = "inactive"
    db.session.commit()
    flash(f"{product.name} removed from active inventory.", "success")
    return redirect(url_for("inventory.products"))


@inventory_bp.route("/products/search")
@login_required
@require_permission("inventory")
def search_products():
    term = request.args.get("q", "").strip()
    query = Product.query.filter_by(business_id=current_user.business_id, status="active")
    if term:
        query = query.filter(Product.name.ilike(f"%{term}%"))
    results = query.order_by(Product.name).limit(10).all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "selling_price": p.selling_price,
            "current_stock": p.current_stock,
        }
        for p in results
    ])
