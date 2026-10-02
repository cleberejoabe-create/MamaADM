from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .. import db
from ..models import Supplier

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/fornecedores")

@suppliers_bp.route("/")
@login_required
def index():
    return render_template("suppliers.html", suppliers=Supplier.query.order_by(Supplier.name).all())

@suppliers_bp.route("/novo", methods=["POST"])
@login_required
def new():
    db.session.add(Supplier(
        name=request.form["name"],
        phone=request.form.get("phone"),
        document=request.form.get("document"),
        notes=request.form.get("notes")
    ))
    db.session.commit()
    flash("Fornecedor cadastrado.")
    return redirect(url_for("suppliers.index"))

@suppliers_bp.route("/<int:id>/excluir")
@login_required
def delete(id):
    s = db.session.get(Supplier, id)
    if s:
        db.session.delete(s)
        db.session.commit()
    return redirect(url_for("suppliers.index"))
