from datetime import datetime, date
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from ..models import Product, Sale, CashEntry

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@login_required
def index():
    products = Product.query.filter_by(active=True).all()
    today = date.today()
    sales_today = Sale.query.filter(func.date(Sale.created_at) == today).all()
    revenue = sum(s.total for s in sales_today)
    stock_value = sum(p.stock * p.cost for p in products)
    low = [p for p in products if p.stock <= p.min_stock]
    recent = Sale.query.order_by(Sale.created_at.desc()).limit(8).all()
    return render_template(
        "dashboard.html",
        products=products,
        revenue=revenue,
        stock_value=stock_value,
        low=low,
        recent=recent,
        sales_count=len(sales_today)
    )
