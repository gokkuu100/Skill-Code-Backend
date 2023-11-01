from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData
from sqlalchemy.orm import validates

metadata = MetaData(naming_convention={
    "fk" : "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db =SQLAlchemy(metadata = metadata)

db = SQLAlchemy()

class Mentor(db.Model, SerializerMixin):
    mentor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    assessments = db.relationship('Assessment', backref='mentor', lazy='dynamic')
    feedback = db.relationship('Feedback', backref='mentor', lazy='dynamic')
    assignments = db.relationship('Assignment', backref='mentor', lazy='dynamic')
    questions = db.relationship('Question', backref='mentor', lazy='dynamic')  # Mentor can create questions

class Assessment(db.Model, SerializerMixin):
    assessment_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    time_limit = db.Column(db.String(50))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))
    
    assignments = db.relationship('Assignment', backref='assigned_assessments', lazy='dynamic')
    questions = db.relationship('Question', backref='assessment', lazy='dynamic')
    notifications = db.relationship('Notification', backref='assessment', lazy='dynamic')

class Assignment(db.Model, SerializerMixin):
    assignment_id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    is_accepted = db.Column(db.Boolean, default=False)
    
    student = db.relationship('Student', backref='assignment_student')
    assessment = db.relationship('Assessment', backref='assessment_assignment')
    responses = db.relationship('Response', backref='assignment_responses', lazy='dynamic')
    # questions = db.relationship('Question', backref='assignment', lazy='dynamic')

class Invite(db.Model, SerializerMixin):
    invite_id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    assessment = db.relationship('Assessment', backref='invites') 

class Question(db.Model, SerializerMixin):
    question_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    options = db.Column(db.String(255))
    text_question = db.Column(db.String(255))
    correct_answer = db.Column(db.String(255))
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'), nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'), nullable=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))

class Grade(db.Model, SerializerMixin):
    grade_id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(50))
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'))

    assessment = db.relationship('Assessment', backref='grades')
    student = db.relationship('Student', backref='grades')
    assignment = db.relationship('Assignment', backref='grades')

class Student(db.Model, SerializerMixin):
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)

    assignments = db.relationship('Assignment', backref='student_assignments', lazy='dynamic')
    notifications = db.relationship('Notification', backref='student', lazy='dynamic')

class Answer(db.Model, SerializerMixin):
    answer_id = db.Column(db.Integer, primary_key=True)
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'))

class Feedback(db.Model, SerializerMixin):
    feedback_id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id')) 
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'))
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'))
    feedback = db.Column(db.String(255))


class Notification(db.Model, SerializerMixin):
    notification_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255))

    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id')) 
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'))


class Response(db.Model, SerializerMixin):
    response_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id')) 
    answer_text = db.Column(db.String(255))
    score = db.Column(db.Integer)

    student = db.relationship('Student', backref='responses') 

    assignment = db.relationship('Assignment', backref='response_assignment') 


