from .. import db
from ..models import Product, StockMovement, Recipe

def move_stock(product_id, quantity, movement_type, reason=""):
    product = db.session.get(Product, product_id)
    if not product:
        raise ValueError("Produto não encontrado.")
    if movement_type == "saida":
        if product.stock < quantity:
            raise ValueError(f"Estoque insuficiente para {product.name}.")
        product.stock -= quantity
    else:
        product.stock += quantity
    db.session.add(StockMovement(
        product_id=product.id,
        type=movement_type,
        quantity=quantity,
        reason=reason
    ))
    return product

def consume_recipe(product_id, sale_quantity):
    recipe = Recipe.query.filter_by(product_id=product_id).all()
    for item in recipe:
        move_stock(item.ingredient_id, item.quantity * sale_quantity, "saida",
                   f"Consumo da ficha técnica de {item.product.name}")
