import os
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{os.getenv("MYSQL_USER")}:{os.getenv("MYSQL_PASSWORD")}'
    f'@{os.getenv("MYSQL_HOST")}/{os.getenv("MYSQL_DB")}'
)

db = SQLAlchemy(app)  # This line initializes SQLAlchemy with your app
migrate = Migrate(app, db)
auth = HTTPTokenAuth(scheme='Bearer')
CORS(app, resources={r"/*": {"origins": "http://localhost"}})

from app import views
