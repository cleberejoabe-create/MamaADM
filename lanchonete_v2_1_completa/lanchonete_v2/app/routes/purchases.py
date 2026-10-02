from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .. import db
from ..models import Product, Supplier, Purchase, PurchaseItem
from ..services.stock import move_stock

purchases_bp = Blueprint("purchases", __name__, url_prefix="/compras")

@purchases_bp.route("/")
@login_required
def index():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    purchases = Purchase.query.order_by(Purchase.created_at.desc()).limit(100).all()
    return render_template("purchases.html", products=products, suppliers=suppliers, purchases=purchases)

@purchases_bp.route("/nova", methods=["POST"])
@login_required
def new():
    try:
        supplier_id = request.form.get("supplier_id") or None
        product_ids = request.form.getlist("product_id")
        quantities = request.form.getlist("quantity")
        costs = request.form.getlist("unit_cost")
        rows = []
        total = 0
        for pid, qty, cost in zip(product_ids, quantities, costs):
            q, c = float(qty), float(cost)
            if pid and q > 0:
                rows.append((int(pid), q, c))
                total += q*c
        if not rows:
            raise ValueError("Adicione itens à compra.")
        purchase = Purchase(supplier_id=supplier_id, total=total)
        db.session.add(purchase)
        db.session.flush()
        for pid, q, c in rows:
            db.session.add(PurchaseItem(purchase_id=purchase.id, product_id=pid, quantity=q, unit_cost=c))
            move_stock(pid, q, "entrada", f"Compra #{purchase.id}")
        db.session.commit()
        flash(f"Compra #{purchase.id} registrada.")
    except ValueError as e:
        db.session.rollback()
        flash(str(e))
    return redirect(url_for("purchases.index"))
