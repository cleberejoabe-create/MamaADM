from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pathlib import Path
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.config["SECRET_KEY"] = "troque-esta-chave-em-producao"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(Path(app.instance_path) / "lanchonete.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .models import User
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.products import products_bp
    from .routes.stock import stock_bp
    from .routes.sales import sales_bp
    from .routes.purchases import purchases_bp
    from .routes.suppliers import suppliers_bp
    from .routes.cash import cash_bp
    from .routes.reports import reports_bp
    from .routes.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(cash_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(users_bp)

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(
                username="admin",
                password_hash=generate_password_hash("admin123"),
                role="admin"
            ))
            db.session.commit()

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return db.session.get(User, int(user_id))
