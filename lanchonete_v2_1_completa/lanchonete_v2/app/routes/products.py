from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .. import db
from ..models import Product, Recipe

products_bp = Blueprint("products", __name__, url_prefix="/produtos")

@products_bp.route("/")
@login_required
def index():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    return render_template("products.html", products=products)

@products_bp.route("/novo", methods=["GET","POST"])
@login_required
def new():
    if request.method == "POST":
        p = Product(
            name=request.form["name"],
            category=request.form.get("category") or "Outros",
            unit=request.form.get("unit") or "un",
            stock=float(request.form.get("stock") or 0),
            min_stock=float(request.form.get("min_stock") or 0),
            cost=float(request.form.get("cost") or 0),
            price=float(request.form.get("price") or 0),
        )
        exp = request.form.get("expiration")
        if exp:
            p.expiration = datetime.strptime(exp, "%Y-%m-%d").date()
        db.session.add(p)
        db.session.commit()
        flash("Produto cadastrado.")
        return redirect(url_for("products.index"))
    return render_template("product_form.html", product=None)

@products_bp.route("/<int:id>/editar", methods=["GET","POST"])
@login_required
def edit(id):
    p = db.session.get(Product, id)
    if not p: return "Produto não encontrado", 404
    if request.method == "POST":
        p.name = request.form["name"]
        p.category = request.form.get("category") or "Outros"
        p.unit = request.form.get("unit") or "un"
        p.min_stock = float(request.form.get("min_stock") or 0)
        p.cost = float(request.form.get("cost") or 0)
        p.price = float(request.form.get("price") or 0)
        exp = request.form.get("expiration")
        p.expiration = datetime.strptime(exp, "%Y-%m-%d").date() if exp else None
        db.session.commit()
        flash("Produto atualizado.")
        return redirect(url_for("products.index"))
    return render_template("product_form.html", product=p)

@products_bp.route("/<int:id>/ficha", methods=["GET","POST"])
@login_required
def recipe(id):
    product = db.session.get(Product, id)
    if not product: return "Produto não encontrado", 404
    if request.method == "POST":
        ingredient = db.session.get(Product, int(request.form["ingredient_id"]))
        qty = float(request.form["quantity"])
        if ingredient and ingredient.id != product.id and qty > 0:
            db.session.add(Recipe(product_id=product.id, ingredient_id=ingredient.id, quantity=qty))
            db.session.commit()
            flash("Ingrediente adicionado à ficha técnica.")
        return redirect(url_for("products.recipe", id=id))
    recipes = Recipe.query.filter_by(product_id=id).all()
    ingredients = Product.query.filter(Product.active == True, Product.id != id).order_by(Product.name).all()
    cost = sum(r.quantity * r.ingredient.cost for r in recipes)
    return render_template("recipe.html", product=product, recipes=recipes, ingredients=ingredients, cost=cost)

@products_bp.route("/ficha/<int:id>/remover")
@login_required
def remove_recipe(id):
    r = db.session.get(Recipe, id)
    if r:
        product_id = r.product_id
        db.session.delete(r)
        db.session.commit()
        return redirect(url_for("products.recipe", id=product_id))
    return redirect(url_for("products.index"))

@products_bp.route("/<int:id>/excluir")
@login_required
def delete(id):
    p = db.session.get(Product, id)
    if p:
        p.active = False
        db.session.commit()
        flash("Produto arquivado.")
    return redirect(url_for("products.index"))
