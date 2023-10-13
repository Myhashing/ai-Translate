from flask import Flask
from config import Config
import logging
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['DEBUG'] = True
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mysql+pymysql://'+app.config['MYSQL_USER']+':'+app.config['MYSQL_PASSWORD']+'@'+app.config['MYSQL_HOST']+'/'+app.config['MYSQL_DB']+'')
db = SQLAlchemy(app)  # This line initializes SQLAlchemy with your app
migrate = Migrate(app, db)

auth = HTTPTokenAuth(scheme='Bearer')
SECRET_KEY = "your_secret_key_here"
CORS(app, resources={r"/*": {"origins": "http://localhost"}})

from app import views
