from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .. import db
from ..models import Product, StockMovement
from ..services.stock import move_stock

stock_bp = Blueprint("stock", __name__, url_prefix="/estoque")

@stock_bp.route("/")
@login_required
def index():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(100).all()
    return render_template("stock.html", products=products, movements=movements)

@stock_bp.route("/movimentar", methods=["POST"])
@login_required
def move():
    try:
        move_stock(
            int(request.form["product_id"]),
            float(request.form["quantity"]),
            request.form["type"],
            request.form.get("reason", "")
        )
        db.session.commit()
        flash("Movimentação registrada.")
    except ValueError as e:
        db.session.rollback()
        flash(str(e))
    return redirect(url_for("stock.index"))
