# config.py
from datetime import timedelta
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'jkbkjbvc-bkjbjkb-jka-kjbjkbkbda'
    JWT_SECRET_KEY = 'kjbjkaebk-kjbjba-kjbajb'  
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    JWT_SECRET_KEY = 'jlbjbalcblibjlbl'
    SQLALCHEMY_TRACK_MODIFICATIONS = False