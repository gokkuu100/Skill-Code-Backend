import os
from .models import *
from flask_migrate import Migrate

from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_restx import Api, Resource, Namespace, abort

from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask(__name__)
CORS(app)


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


api = Api(app, version='1.0', title='Skill-Code', description='Api for a Coding Platform')




# from api import routes, models