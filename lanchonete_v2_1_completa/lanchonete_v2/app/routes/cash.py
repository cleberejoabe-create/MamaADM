from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func
from .. import db
from ..models import CashEntry, Sale

cash_bp = Blueprint("cash", __name__, url_prefix="/caixa")

@cash_bp.route("/")
@login_required
def index():
    entries = CashEntry.query.order_by(CashEntry.created_at.desc()).limit(100).all()
    sales_today = Sale.query.filter(func.date(Sale.created_at) == date.today()).all()
    sales_total = sum(s.total for s in sales_today)
    return render_template("cash.html", entries=entries, sales_total=sales_total)

@cash_bp.route("/novo", methods=["POST"])
@login_required
def new():
    amount = float(request.form["amount"])
    db.session.add(CashEntry(
        type=request.form["type"],
        description=request.form["description"],
        amount=amount
    ))
    db.session.commit()
    flash("Lançamento registrado.")
    return redirect(url_for("cash.index"))
