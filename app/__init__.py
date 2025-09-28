from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    migrate.init_app(app, db)
    jwt.init_app(app)

    from .routes import register_bp, auth_bp
    

    app.register_blueprint(register_bp)
    app.register_blueprint(auth_bp)


    return app