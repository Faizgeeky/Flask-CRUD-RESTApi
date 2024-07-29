from flask import Flask
from api.route.auth import auth_bp
from api.route.sensor import sensor_bp
from config import Config
from extensions import db, jwt, ma
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)

    ## Initialize Config
    app.config.from_object(Config)
    
    
    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)


    # register all blueprint's
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(sensor_bp, url_prefix='/v1')

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)