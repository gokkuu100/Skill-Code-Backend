from ..api import *
jwt = JWTManager(app)

@app.route('/')
def home():
    response_body = {
        "Message": "Welcome to the world of heroes"
    }
    return make_response(response_body), 200

# Route for mentor to sign-up
@app.route('/mentors/signup', methods=['POST'])
def mentor_signup():
    data = request.get_json()

    # Retrieve mentor data from request
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify(error='Invalid request data'), 400

    # Check if already exists
    existing_mentor = Mentor.query.filter_by(email=email).first()
    if existing_mentor:
        return jsonify(error='Mentor with this email already exists'), 400

    # Hash password
    password_hash = generate_password_hash(password)

    # New mentor object
    new_mentor = Mentor(name=name, email=email, password=password_hash)
    db.session.add(new_mentor)
    db.session.commit()

    access_token = create_access_token(identity={'email': email, 'role': 'mentor', 'mentor_id': new_mentor.mentor_id})
    return jsonify(access_token=access_token), 200

# Route for mentor login
@app.route('/mentors/login', methods=['POST'])
def mentor_login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify(error='Invalid request data'), 400

    # Retrieve the mentor with the given email from db
    mentor = Mentor.query.filter_by(email=email).first()

    # Check if the mentor exists and the password is correct
    if mentor and check_password_hash(mentor.password, password):
        # Generate JWT token 
        access_token = create_access_token(identity={'email': email, 'role': 'mentor', 'mentor_id': mentor.mentor_id})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(error='Invalid email or password'), 401
    
# Route to view mentor based on id
@app.route('/mentors/<int:mentor_id>', methods=['GET'])
def view_mentor(mentor_id):
    mentor = Mentor.query.get_or_404(mentor_id)
    mentor_data = {
        'id': mentor.mentor_id,
        'name': mentor.name,
        'email': mentor.email,
        'assessments': [{
            'id': assessment.assessment_id,
            'title': assessment.title,
            # 'created_at': assessment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'questions_count': assessment.questions.count()
        } for assessment in mentor.assessments]
    }
    return jsonify(mentor_data)

# Route for student sign-up
@app.route('/students/signup', methods=['POST'])
def student_signup():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify(error='Invalid request data'), 400

    # Check if the student already exists
    existing_student = Student.query.filter_by(email=email).first()
    if existing_student:
        return jsonify(error='Student with this email already exists'), 400

    # Hash the password 
    password_hash = generate_password_hash(password)

    # New student object
    new_student = Student(email=email, password=password_hash)
    db.session.add(new_student)
    db.session.commit()

    access_token = create_access_token(identity={'email': email, 'role': 'student', 'student_id': new_student.student_id})
    return jsonify(access_token=access_token), 200

# Route for student login
@app.route('/students/login', methods=['POST'])
def student_login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify(error='Invalid request data'), 400

    # Retrieve the student with the given email from db
    student = Student.query.filter_by(email=email).first()

    # Check if the student exists and correct password
    if student and check_password_hash(student.password, password):
        # Generate JWT token 
        access_token = create_access_token(identity={'email': email, 'role': 'student', 'student_id': student.student_id})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(error='Invalid email or password'), 401


# # Route to create an assessment
# @app.route('/assessments/create', methods=['POST'])
# @jwt_required()
# def create_assessment():
#     data = request.get_json()
#     title = data.get('title', '')
#     questions_data = data.get('questions', [])

#     if not title or not questions_data:
#         return jsonify(error='Invalid request data'), 400
    
#     # Get mentor_id from the token
#     mentor_id = get_jwt_identity()['mentor_id']

#     assessment = Assessment(title=title, mentor_id=mentor_id)
#     for question_data in questions_data:
#         text = question_data.get('text', '')
#         options = question_data.get('options', [])
#         correct_answer = question_data.get('correct_answer', '')

#         if not text or len(options) != 4 or not correct_answer:
#             return jsonify(error='Invalid question data'), 400

#         question_options = '\n'.join(options)
#         question = Question(text=text, options=question_options, correct_answer=correct_answer)
#         assessment.questions.append(question)

#     db.session.add(assessment)
#     db.session.commit()

#     return jsonify(message='Assessment created successfully')

# View assessment based on its id
@app.route('/assessments/<int:assessment_id>', methods=['GET'])
def view_assessment(assessment_id):
    # Retrieve the assessment based on id
    assessment = Assessment.query.get_or_404(assessment_id)

    # Retrieve questions and answers for the assessment
    questions = []
    for question in assessment.questions:
        questions.append({
            'id': question.question_id,
            'text': question.text_question,
            'options': question.options.split('\n'),  
            'correct_answer': question.correct_answer
        })

    return jsonify({
        'id': assessment.assessment_id,
        'title': assessment.title,
        'questions': questions
    })

# Route to view all the assessments
@app.route('/assessments', methods=['GET'])
def list_assessments():
    assessments = Assessment.query.all()

    # Lists the assessments
    assessment_list = []
    for assessment in assessments:
        assessment_data = {
            'id': assessment.assessment_id,
            'title': assessment.title,
            'description': assessment.description,
            # 'created_at': assessment.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
            'questions_count': assessment.questions.count()  
        }
        assessment_list.append(assessment_data)

    return jsonify(assessments=assessment_list)

# # Route to view and answer questions for an assessment
# @app.route('/assessments/<int:assessment_id>/questions/<int:question_number>', methods=['GET', 'POST'])
# # @jwt_required() 
# def view_and_answer_question(assessment_id, question_number):
#     # Retrieve questions on assessment_id and question_number
#     assessment = Assessment.query.get_or_404(assessment_id)
#     question = assessment.questions.filter_by(question_id=question_number).first()

#     if question is None:
#         abort(404, description='Question not found')

#     # Gets student_id according to token
#     student_id = get_jwt_identity().get('student_id')

#     if request.method == 'GET':
#         # Display the question and options
#         return jsonify(question_text=question.text, options=question.options.split('\n'))

#     elif request.method == 'POST':
#         data = request.get_json()
#         user_answer = data.get('answer', '')

#         # Validates answer
#         is_correct = user_answer == question.correct_answer

#         # Saves the response
#         response = Response(
#             assessment_id=assessment_id,
#             question_id=question_number,
#             student_id=student_id,
#             is_correct=is_correct,
#             answer_text=user_answer  
#         )
#         db.session.add(response)
#         db.session.commit()

#         # Determines the next question number
#         next_question_number = question_number + 1

#         # Get the next question
#         next_question = assessment.questions.filter_by(id=next_question_number).first()

#         response_data = {
#             "is_correct": is_correct,
#             "correct_answer": question.correct_answer,
#             "student_id": student_id  
#         }

#         if next_question:
#             response_data["next_question"] = {
#                 "question_text": next_question.text,
#                 "options": next_question.options.split('\n')
#             }
#         else:
#             response_data["message"] = "Assessment completed. Thank you for participating!"

#         return jsonify(response_data)
    
    
# Feedback route
@app.route('/mentors/feedback', methods=['POST'])
# @jwt_required()
def leave_feedback():
    data = request.get_json()
    mentor_id = data.get('mentor_id')
    assessment_id = data.get('assessment_id')
    question_id = data.get('question_id')
    student_id = data.get('student_id')
    text = data.get('text')

    if not mentor_id or not assessment_id or not question_id or not student_id or not text:
        return jsonify(error='Invalid request data'), 400

    # Check if the mentor exists
    mentor = Mentor.query.get(mentor_id)
    if mentor is None:
        return jsonify(error='Mentor not found'), 404

    assessment = Assessment.query.filter_by(assessment_id=assessment_id, mentor_id=mentor_id).first()
    if assessment is None:
        return jsonify(error='Assessment not found or does not belong to the mentor'), 404

    question = Question.query.filter_by(question_id=question_id, assessment_id=assessment_id).first()
    if question is None:
        return jsonify(error='Question not found or does not belong to the assessment'), 404

    # Check if student exists
    student = Student.query.get(student_id)
    if student is None:
        return jsonify(error='Student not found'), 404

    feedback = Feedback(mentor_id=mentor_id, assessment_id=assessment_id, question_id=question_id, student_id=student_id, feedback=text)
    db.session.add(feedback)
    db.session.commit()

    return jsonify(message='Feedback submitted successfully')


# Route for mentors to release grades for an assessment
# @app.route('/mentors/grades', methods=['POST'])
# def release_grades():
#     data = request.get_json()
#     mentor_id = data.get('mentor_id')
#     assessment_id = data.get('assessment_id')
#     student_grades = data.get('student_grades')

#     if not mentor_id or not assessment_id or not student_grades:
#         return jsonify(error='Invalid request data'), 400

#     for student_id, score in student_grades.items():
#         grade = Grade(mentor_id=mentor_id, assessment_id=assessment_id, student_id=student_id, score=score)
#         db.session.add(grade)

#     db.session.commit()

#     return jsonify(message='Grades released successfully')


# Route for students to view their grades for a specific assessment
@app.route('/students/grades/<int:student_id>/<int:assessment_id>', methods=['GET'])
def view_student_grades(student_id, assessment_id):
    student = Student.query.get_or_404(student_id)
    assessment = Assessment.query.get_or_404(assessment_id)

    grades = Grade.query.filter_by(student_id=student_id, assessment_id=assessment_id).all()

    grade_data = {
        'student_id': student.student_id,
        'student_email': student.email,
        'assessment_id': assessment.assessment_id,
        'assessment_title': assessment.title,
        'grades': [{grade.grade_id: grade.grade} for grade in grades]
    }

    return jsonify(grade_data)