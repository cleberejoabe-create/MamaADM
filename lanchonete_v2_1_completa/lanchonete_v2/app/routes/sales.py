from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..models import Product, Sale
from ..services.sales import create_sale

sales_bp = Blueprint("sales", __name__, url_prefix="/vendas")

@sales_bp.route("/")
@login_required
def index():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    sales = Sale.query.order_by(Sale.created_at.desc()).limit(100).all()
    return render_template("sales.html", products=products, sales=sales)

@sales_bp.route("/nova", methods=["POST"])
@login_required
def new():
    try:
        product_ids = request.form.getlist("product_id")
        quantities = request.form.getlist("quantity")
        items = [{"product_id": pid, "quantity": qty}
                 for pid, qty in zip(product_ids, quantities)
                 if pid and float(qty) > 0]
        if not items:
            raise ValueError("Adicione pelo menos um item.")
        sale = create_sale(items, request.form.get("payment", "Dinheiro"))
        flash(f"Venda #{sale.id} registrada: R$ {sale.total:.2f}.")
    except ValueError as e:
        from .. import db
        db.session.rollback()
        flash(str(e))
    return redirect(url_for("sales.index"))
