import os
from .models import *
from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask(__name__)

# Setup app configs
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

instance_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
os.makedirs(instance_folder, exist_ok=True)  # Create 'instance' folder if it doesn't exist
db_path = os.path.join(instance_folder, 'skillcode.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)




# from api import routes, models