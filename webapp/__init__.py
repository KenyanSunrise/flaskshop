from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()


def create_app(config_file=Config):
    app = Flask(__name__)
    app.config.from_object(config_file)
    db.init_app(app=app)
    migrate.init_app(app, db)
    login.init_app(app)
    from Shop.routes import shop
    app.register_blueprint(shop)
    from auth.services import github_bp, google_bp, yandex_bp
    app.register_blueprint(github_bp, url_prefix="/login")
    app.register_blueprint(google_bp, url_prefix="/login")
    app.register_blueprint(yandex_bp, url_prefix='/login')
    from account.routes import account
    app.register_blueprint(account, url_prefix="/account")
    return app
