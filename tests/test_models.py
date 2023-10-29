import pytest
from api import app, db, Mentor, Assessment, Invite,Assignment, Question, Response, Feedback, Grade, Student, Answer, Notification

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Skill-Code-Backend/skillcode.db'
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():  
            yield client

def test_mentor_model(client):
    with app.app_context():  

        mentor = Mentor(name="John Doe", email="john@example.com", password="password")
        db.session.add(mentor)
        db.session.commit()

        mentor_from_db = Mentor.query.get(mentor.mentor_id)
        assert mentor.name == mentor_from_db.name
        assert mentor.email == mentor_from_db.email

def test_assessment_model(client):
    with app.app_context():
        mentor = Mentor.query.filter_by(name="John Doe").first()

        assessment = Assessment(title="Test Assessment", description="Assessment description", time_limit="60 minutes", mentor_id=mentor.mentor_id)
        db.session.add(assessment)

        db.session.commit()

        assessment_from_db = Assessment.query.get(assessment.assessment_id)
        assert assessment.title == assessment_from_db.title
        assert assessment.description == assessment_from_db.description
        assert assessment.time_limit == assessment_from_db.time_limit
        assert assessment.mentor_id == assessment_from_db.mentor_id

def test_get_assessment(client):
    with app.app_context():
        assessment_from_db = Assessment.query.filter_by(title="Test Assessment").first()

        assert assessment_from_db is not None
        assert assessment_from_db.title == "Test Assessment"
        assert assessment_from_db.description == "Assessment description"
        assert assessment_from_db.time_limit == "60 minutes"

def test_create_and_get_assignment(client):
    with app.app_context():
        assignment = Assignment(
            assessment_id=1,
            mentor_id=1,
            student_id=1,
            is_accepted=True
        )
        db.session.add(assignment)
        db.session.commit()

        assignment_from_db = Assignment.query.get(assignment.assignment_id)

        assert assignment_from_db is not None
        assert assignment_from_db.assessment_id == 1
        assert assignment_from_db.mentor_id == 1
        assert assignment_from_db.student_id == 1
        assert assignment_from_db.is_accepted is True


def test_create_and_get_invite(client):
    with app.app_context():
        invite = Invite(
            assessment_id=1,
            mentor_id=1,
            student_id=1
        )
        db.session.add(invite)
        db.session.commit()

        invite_from_db = Invite.query.get(invite.invite_id)

        assert invite_from_db is not None
        assert invite_from_db.assessment_id == 1
        assert invite_from_db.mentor_id == 1
        assert invite_from_db.student_id == 1


def test_create_and_get_question(client):
    with app.app_context():
        question = Question(
            title="What is 2 + 2?",
            options="A: 3, B: 4, C: 5, D: 6",
            text_question=None,
            correct_answer="B: 4",
            assessment_id=1,
            assignment_id=None,
            mentor_id=1
        )
        db.session.add(question)
        db.session.commit()

        question_from_db = Question.query.get(question.question_id)

        assert question_from_db is not None
        assert question_from_db.title == "What is 2 + 2?"
        assert question_from_db.options == "A: 3, B: 4, C: 5, D: 6"
        assert question_from_db.text_question is None
        assert question_from_db.correct_answer == "B: 4"
        assert question_from_db.assessment_id == 1
        assert question_from_db.assignment_id is None
        assert question_from_db.mentor_id == 1

def test_create_and_get_grade(client):
    with app.app_context():
        grade = Grade(
            grade="A",
            assessment_id=1,
            student_id=1,
            assignment_id=None
        )
        db.session.add(grade)
        db.session.commit()

        grade_from_db = Grade.query.get(grade.grade_id)

        assert grade_from_db is not None
        assert grade_from_db.grade == "A"
        assert grade_from_db.assessment_id == 1
        assert grade_from_db.student_id == 1
        assert grade_from_db.assignment_id is None


def test_create_and_get_student(client):
    with app.app_context():
        student = Student(
            name="Alice",
            password="password123",
            email="alice@example.com"
        )
        db.session.add(student)
        db.session.commit()

        student_from_db = Student.query.get(student.student_id)

        assert student_from_db is not None
        assert student_from_db.name == "Alice"
        assert student_from_db.password == "password123"
        assert student_from_db.email == "alice@example.com"

def test_create_and_get_answer(client):
    with app.app_context():
        question = Question(title="Sample Question")
        db.session.add(question)
        db.session.commit()

        answer = Answer(
            option_a="Option A",
            option_b="Option B",
            option_c="Option C",
            option_d="Option D",
            question_id=question.question_id
        )
        db.session.add(answer)
        db.session.commit()

        answer_from_db = Answer.query.get(answer.answer_id)

        assert answer_from_db is not None
        assert answer_from_db.option_a == "Option A"
        assert answer_from_db.option_b == "Option B"
        assert answer_from_db.option_c == "Option C"
        assert answer_from_db.option_d == "Option D"
        assert answer_from_db.question_id == question.question_id

def test_create_and_get_feedback_with_existing_data(client):
    with app.app_context():

        existing_mentor = Mentor.query.first()
        existing_question = Question.query.first()

        feedback = Feedback(
            feedback="Great work!",
            question_id=existing_question.question_id,
            mentor_id=existing_mentor.mentor_id
        )
        db.session.add(feedback)
        db.session.commit()

        feedback_from_db = Feedback.query.get(feedback.feedback_id)

        assert feedback_from_db is not None
        assert feedback_from_db.feedback == "Great work!"
        assert feedback_from_db.question_id == existing_question.question_id
        assert feedback_from_db.mentor_id == existing_mentor.mentor_id

def test_create_and_get_notification(client):
    with app.app_context():

        existing_student = Student.query.first()

        notification = Notification(
            content="You have a new message.",
            student_id=existing_student.student_id
        )
        db.session.add(notification)
        db.session.commit()

        notification_from_db = Notification.query.get(notification.notification_id)

        assert notification_from_db is not None
        assert notification_from_db.content == "You have a new message."
        assert notification_from_db.student_id == existing_student.student_id

def test_create_and_get_response(client):
    with app.app_context():

        existing_assignment = Assignment.query.first()
        existing_question = Question.query.first()
        existing_student = Student.query.first()

        response = Response(
            assignment_id=existing_assignment.assignment_id,
            question_id=existing_question.question_id,
            student_id=existing_student.student_id,
            answer_text="This is the answer",
            score=90
        )
        db.session.add(response)
        db.session.commit()

        response_from_db = Response.query.get(response.response_id)

        assert response_from_db is not None
        assert response_from_db.assignment_id == existing_assignment.assignment_id
        assert response_from_db.question_id == existing_question.question_id
        assert response_from_db.student_id == existing_student.student_id
        assert response_from_db.answer_text == "This is the answer"
        assert response_from_db.score == 90
