from .. import db
from ..models import Product, Sale, SaleItem
from .stock import consume_recipe, move_stock

def create_sale(items, payment):
    sale = Sale(payment=payment, total=0)
    db.session.add(sale)
    db.session.flush()

    total = 0
    for row in items:
        product = db.session.get(Product, int(row["product_id"]))
        qty = float(row["quantity"])
        if not product or not product.active:
            raise ValueError("Produto inválido.")
        if qty <= 0:
            raise ValueError("Quantidade inválida.")

        from ..models import Recipe
        recipe_exists = Recipe.query.filter_by(product_id=product.id).first()

        if recipe_exists:
            consume_recipe(product.id, qty)
        else:
            move_stock(product.id, qty, "saida", "Venda")

        item_total = product.price * qty
        total += item_total
        db.session.add(SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            quantity=qty,
            unit_price=product.price
        ))

    sale.total = total
    db.session.commit()
    return sale
