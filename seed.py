from faker import Faker
import bcrypt
import random

from api import *


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


fake = Faker()
with app.app_context():
    Student.query.delete()
    Mentor.query.delete()
    Assessment.query.delete()
    Assignment.query.delete()
    Invite.query.delete()
    Question.query.delete()
    Notification.query.delete()
    Feedback.query.delete()
    Grade.query.delete()
    Answer.query.delete()

    
def seed_table(model, count):
    for _ in range(count):
        data = create_fake_data(model)
        if data is None:
            continue
        instance = model(**data)
        db.session.add(instance)


def create_fake_data(model):
    if model == Mentor:
        password = fake.password()
        hashed_password = hash_password(password)

        return {
            'name': fake.name(),
            'email': fake.email(),
            'password': hashed_password,
        }


    elif model == Student:
        password = fake.password()
        hashed_password = hash_password(password)

        return {
            'name': fake.name(),
            'email': fake.email(),
            'password': hashed_password,
        }
    
    elif model == Assessment:
        return {
            'title': fake.catch_phrase(),
            'description': fake.text(),
            'time_limit': str(fake.random_int(min=30, max=120)),
            'mentor': Mentor.query.order_by(db.func.random()).first()
        }

    elif model == Assignment:
            assessment = Assessment.query.order_by(db.func.random()).first()
            mentor_id = assessment.mentor_id if assessment else None  # Get mentor_id from associated assessment
            mentor = Mentor.query.get(mentor_id) if mentor_id else None  # Fetch mentor with mentor_id

            student = Student.query.order_by(db.func.random()).first()
            
            return {
                'assessment': assessment,
                'mentor': mentor,
                'student': student,
                'is_accepted': fake.boolean(chance_of_getting_true=50)
            }
    
    elif model == Question:
        mentor = Mentor.query.order_by(db.func.random()).first()
        assignment = Assignment.query.order_by(db.func.random()).first()
        assessment = Assessment.query.order_by(db.func.random()).first()
        
        title = fake.sentence()
        
        options = [
            f'A:{fake.word()}, B:{fake.word()}, C:{fake.word()}, D:{fake.word()}',
            f'A:{fake.word()}, B:{fake.word()}, C:{fake.word()}, D:{fake.word()}',
            
        ]
        options_text = fake.random_element(options)
        
        text_question = fake.sentence()
        
        correct_answer = f"{fake.random_element(['A', 'B', 'C', 'D'])}"
        
        if mentor and assignment and assessment:
            question_data = {
                'title': title,
                'options': options_text,
                'text_question': text_question,
                'correct_answer': correct_answer,
                'mentor': mentor,
                'assignment_id': assignment.assignment_id,  
                'assessment_id': assessment.assessment_id, 
            }
            question = Question(**question_data)
            db.session.add(question)
        
    
    elif model == Grade:
        assessment = Assessment.query.order_by(db.func.random()).first()
        student = Student.query.order_by(db.func.random()).first()
        assignment = Assignment.query.order_by(db.func.random()).first()
        return {
            'grade': fake.random_element(elements=("A", "B", "C", "D", "F")),
            'assessment': assessment,
            'student': student,
            'assignment': assignment
        }
    
    elif model == Feedback:
        student = Student.query.order_by(db.func.random()).first()
        mentor = Mentor.query.order_by(db.func.random()).first()
        question = Question.query.order_by(db.func.random()).first()
        assessment = Assessment.query.order_by(db.func.random()).first()
        return {
            'student_id': student.student_id,
            'mentor_id': mentor.mentor_id,
            'question_id': question.question_id,
            'assessment_id': assessment.assessment_id,
            'feedback': fake.text(max_nb_chars=255)
        }
    
    elif model == Invite:
        # Fetch 20 random assignments
        assignments = Assignment.query.order_by(db.func.random()).limit(20).all()

        if assignments:
            for assignment in assignments:
                # Create an invite for each of the 20 random assignments
                new_invite = Invite(
                    assessment_id=assignment.assessment_id,
                    mentor_id=assignment.mentor_id,
                    student_id=assignment.student_id
                )
                db.session.add(new_invite)  # Add the new invite to the session


    
    elif model == Notification:
        # Get a random invite
        invite = Invite.query.order_by(db.func.random()).first()

        if invite:
            return {
                'content': fake.sentence(),
                'student_id': invite.student_id,
                'assessment_id': invite.assessment_id
            }
        else:
            # If no invites are found, consider setting assessment_id and student_id to None or any default value
            return {
                'content': fake.sentence(),
                'student_id': None,
                'assessment_id': None
            }
        
    elif model == Response:
        assignment = Assignment.query.order_by(db.func.random()).first()
        question = Question.query.order_by(db.func.random()).first()
        student = Student.query.order_by(db.func.random()).first()
        return {
            'assignment_id': assignment.assignment_id,
            'question_id': question.question_id,
            'student_id': student.student_id,
            'answer_text': fake.text(max_nb_chars=255),
            'score': fake.random_int(min=0, max=10)
        }
    

    elif model == Answer:
        question = Question.query.order_by(db.func.random()).first()
        if question is None:
            return None

        return {
            'option_a': fake.word(),
            'option_b': fake.word(),
            'option_c': fake.word(),
            'option_d': fake.word(),
            'question_id': question.question_id,
        }





# Create an application context
with app.app_context():
    Student.query.delete()
    Mentor.query.delete()
    Assessment.query.delete()
    Assignment.query.delete()
    Invite.query.delete()
    Question.query.delete()
    Notification.query.delete()
    Feedback.query.delete()
    Grade.query.delete()
    Answer.query.delete()

    # Seed each table
    tables_to_seed = [Mentor, Student, Assessment, Assignment, Question, Grade, Feedback, Response, Invite, Answer, Notification]
    for table in tables_to_seed:
        table_name = table.__name__
        count = 20 if table != Invite else 1  
        seed_table(table, count)
        db.session.commit()
        print(f"Successfully seeded {count} records in the {table_name} table.")

   


    # for _ in range(20):
        # mentor = Mentor.query.order_by(db.func.random()).first()
        # assignment = Assignment.query.order_by(db.func.random()).first()
        # assessment = Assessment.query.order_by(db.func.random()).first()
        
        # title = fake.sentence()
        
        # options = [
        #     f'A:{fake.word()}, B:{fake.word()}, C:{fake.word()}, D:{fake.word()}',
        #     f'A:{fake.word()}, B:{fake.word()}, C:{fake.word()}, D:{fake.word()}',
        #     # Add more sets of options as needed
        # ]
        # options_text = fake.random_element(options)
        
        # text_question = fake.sentence()
        
        # correct_answer = f"{fake.random_element(['A', 'B', 'C', 'D'])}:{fake.word()}"
        
        # if mentor and assignment and assessment:
        #     question_data = {
        #         'title': title,
        #         'options': options_text,
        #         'text_question': text_question,
        #         'correct_answer': correct_answer,
        #         'mentor': mentor,
        #         'assignment_id': assignment.assignment_id,  # Corrected to 'assignment_id'
        #         'assessment_id': assessment.assessment_id,  # Set the appropriate field
        #     }
        #     question = Question(**question_data)
        #     db.session.add(question)
        # else:
        #     # Handle the case where mentor, assignment, or assessment is not found
        #     continue

# Remove the application context (clean up)
app.app_context().pop()


# Commit the changes
db.session.commit()