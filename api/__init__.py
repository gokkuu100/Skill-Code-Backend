import os
from .models import *
from flask_migrate import Migrate

from flask import Flask, request, jsonify, abort, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_restx import Api, Resource, Namespace, abort
<<<<<<< HEAD
from flask_mail import Mail, Message

=======
from flask_cors import CORS
>>>>>>> 9cfde5f3d525e7a70c6e1970256dbe39180c4361

from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask(__name__)
CORS(app)

# Setup app configs
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
jwt = JWTManager(app)

instance_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
os.makedirs(instance_folder, exist_ok=True)  # Create 'instance' folder if it doesn't exist
db_path = os.path.join(instance_folder, 'skillcode.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'localhost'  # Your email server address
app.config['MAIL_PORT'] = 1025  # Port for your email server
app.config['MAIL_USE_TLS'] = False  # Use TLS encryption
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = None  # Your email address
app.config['MAIL_PASSWORD'] = None  # Your email password

app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

mail = Mail(app)

api = Api(app, version='1.0', title='Skill-Code', description='Api for a Coding Platform')


# Send email invitation
def send_invitation_email(mentor_email, student_email, assessment_title):
    msg = Message('Assessment Invitation', sender=mentor_email, recipients=[student_email])
    msg.body = f'You have been invited to participate in the assessment: {assessment_title}. Login to your account to accept the invitation.'
    mail.send(msg)


# from api import routes, models