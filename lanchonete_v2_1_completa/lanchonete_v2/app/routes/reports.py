from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from ..models import Sale, SaleItem, Product

reports_bp = Blueprint("reports", __name__, url_prefix="/relatorios")

@reports_bp.route("/")
@login_required
def index():
    now = datetime.now()
    start = now - timedelta(days=30)
    sales = Sale.query.filter(Sale.created_at >= start).order_by(Sale.created_at).all()
    by_product = {}
    for sale in sales:
        for item in sale.items:
            by_product.setdefault(item.product.name, {"qty":0, "revenue":0})
            by_product[item.product.name]["qty"] += item.quantity
            by_product[item.product.name]["revenue"] += item.quantity * item.unit_price
    ranking = sorted(by_product.items(), key=lambda x: x[1]["qty"], reverse=True)
    return render_template("reports.html", sales=sales, ranking=ranking)
