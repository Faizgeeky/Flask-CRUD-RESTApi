# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flasgger import Swagger

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
swagger = Swagger()