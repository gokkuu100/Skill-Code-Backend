from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Mentor(db.Model):
    mentor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
class Assessment(db.Model):
    assessment_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    time_limit = db.Column(db.String(50))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))
    
    
class Invite(db.Model):
    invite_id = db.Column(db.Integer, primary_key= True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    
class Question(db.Model):
    questions_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    options = db.Column(db.String(255))
    text_question = db.Column(db.String(255))
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'))   
    
class Grade(db.Model):
    grade_id = db.Column(db.Integer,primary_key=True)
    grade = db.Column(db.String(50))
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.assessment_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    
class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True) 
    
class Answer(db.Model):
    answer_id = db.Column(db.Integer, primary_key=True)
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db. Column(db.String(255))
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'))
    
class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    feedback = db.Column(db.String(255))
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))           
            