from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api, fields


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    api = Api(app, doc='/docs')
    

    from .routes.auth import user_routes
    from .routes.tasks import task_routes
    api.add_namespace(task_routes)
    api.add_namespace(user_routes)
    

    db.init_app(app)

    migrate.init_app(app, db)
    jwt.init_app(app)



    return app