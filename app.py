from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skill_code.db' 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your email server address
app.config['MAIL_PORT'] = 587  # Port for your email server
app.config['MAIL_USE_TLS'] = True  # Use TLS encryption
app.config['MAIL_USERNAME'] = 'your_email@example.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Your email password

db = SQLAlchemy(app)

mail = Mail(app)

# Send email invitation
def send_invitation_email(student_email, assessment_title):
    msg = Message('Assessment Invitation', sender='princewalter422@gmail.com', recipients=[student_email])
    msg.body = f'You have been invited to participate in the assessment: {assessment_title}. Login to your account to accept the invitation.'
    mail.send(msg)


@app.route('/assessments/create', methods=['POST'])
def create():
    data = request.get_json()
    title = data.get('title')
    questions = data.get('questions')
    assessment_type = data.get('type')

    return make_response(jsonify(message='Assessment created successfully'), 200)


from .api import app,  students_routes, mentors_routes



if __name__ == '__main__':
    app.run(port=6000, debug=True, threaded=True )



