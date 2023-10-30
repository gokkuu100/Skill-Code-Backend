from ..api import *

ns = Namespace('SkillCode',description='CRUD endpoints')
api.add_namespace(ns)
jwt = JWTManager(app)


@app.route('/home')
class HomeResource(Resource):
    def get(self):
        response_body = {
            "Message": "Welcome to the world of heroes"
        }
        return make_response(response_body), 200

# Route for mentor to sign-up
@ns.route('/mentors/signup')
class MentorSignupResource(Resource):
    def post(self):
        try:
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
                return make_response(jsonify({"error": 'Mentor with this email already exists'}), 400)

            # Hash password
            password_hash = generate_password_hash(password)

            # New mentor object
            new_mentor = Mentor(name=name, email=email, password=password_hash)
            db.session.add(new_mentor)
            db.session.commit()

            access_token = create_access_token(identity={'email': email, 'role': 'mentor', 'mentor_id': new_mentor.mentor_id})
            return jsonify({'access_token': access_token}), 200
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)

# Route for mentor login
@ns.route('/mentors/login')
class MentorLoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return make_response(jsonify(error='Invalid request data'), 400)

            # Retrieve the mentor with the given email from the database
            mentor = Mentor.query.filter_by(email=email).first()

            if not mentor:
                raise ValueError("Mentor not found")

            if not check_password_hash(mentor.password, password):
                raise ValueError("Invalid password")

            # Generate JWT token
            access_token = create_access_token(identity={'email': email, 'role': 'mentor', 'mentor_id': mentor.mentor_id})
            return make_response(jsonify(access_token=access_token), 200)

        except ValueError as e:
            # Handle specific exceptions and return appropriate responses
            if str(e) == "Mentor not found":
                return make_response(jsonify(error='Mentor not found'), 404)
            elif str(e) == "Invalid password":
                return make_response(jsonify(error='Invalid email or password'), 401)
            else:
                return make_response(jsonify(error='An error occurred'), 500)
        
        except Exception as e:
            # Handle other exceptions and return a generic error response
            return make_response(jsonify(error='An error occurred'), 500)


# Route to view mentor based on id
@ns.route('/mentors/<int:mentor_id>')
class ViewMentorResource(Resource):
    def get(self, mentor_id):
        try:
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
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route for student sign-up
@ns.route('/students/signup')
class StudentSignupResource(Resource):
    def post(self):
        try:
            data = request.get_json()

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return make_response(jsonify({'error': 'Invalid request data'}), 400)

            # Check if the student already exists
            existing_student = Student.query.filter_by(email=email).first()
            if existing_student:
                return make_response(jsonify({'error': 'Student with this email already exists'}), 400)

            # Hash the password
            password_hash = generate_password_hash(password)

            # New student object
            new_student = Student(email=email, password=password_hash)
            db.session.add(new_student)
            db.session.commit()

            access_token = create_access_token(identity={'email': email, 'role': 'student', 'student_id': new_student.student_id})
            return make_response(jsonify({'access_token': access_token}), 200)

        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)


# Route for student login
@ns.route('/students/login')
class StudentLoginResource(Resource):
    def post(self):
        try:
            data = request.get_json()

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return make_response(jsonify(error='Invalid request data'), 400)

            # Retrieve the student with the given email from the database
            student = Student.query.filter_by(email=email).first()

            if not student:
                raise ValueError("Student not found")

            if not check_password_hash(student.password, password):
                raise ValueError("Invalid password")

            # Generate JWT token 
            access_token = create_access_token(identity={'email': email, 'role': 'student', 'student_id': student.student_id})
            return make_response(jsonify(access_token=access_token), 200)

        except ValueError as e:
            # Handle specific exceptions and return appropriate responses
            if str(e) == "Student not found":
                return make_response(jsonify(error='Student not found'), 404)
            elif str(e) == "Invalid password":
                return make_response(jsonify(error='Invalid email or password'), 401)
            else:
                return make_response(jsonify(error='An error occurred'), 500)
        
        except Exception as e:
            # Handle other exceptions and return a generic error response
            return make_response(jsonify(error='An error occurred'), 500)


# Route to create an assessment
# @ns.route('/assessments/create')
# # @jwt_required()
# def create_assessment():
#     def post(self):

#         data = request.get_json()
#         title = data.get('title', '')
#         questions_data = data.get('questions', [])

#         if not title or not questions_data:
#             return jsonify(error='Invalid request data'), 400
        
#         # Get mentor_id from the token
#         mentor_id = 1
#         # mentor_id = get_jwt_identity()['mentor_id']

#         assessment = Assessment(title=title, mentor_id=mentor_id)
#         for question_data in questions_data:
#             text = question_data.get('text', '')
#             options = question_data.get('options', [])
#             correct_answer = question_data.get('correct_answer', '')

#             if not text or len(options) != 4 or not correct_answer:
#                 return jsonify(error='Invalid question data'), 400

#             question_options = '\n'.join(options)
#             question = Question(text=text, options=question_options, correct_answer=correct_answer)
#             assessment.questions.append(question)

#         db.session.add(assessment)
#         db.session.commit()

#         return jsonify(message='Assessment created successfully')

# View assessment based on its id
@ns.route('/assessments/<int:assessment_id>')
class ViewAssessmentResource(Resource):
    def get(self, assessment_id):
        try:
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
        except Exception as e:
            # Log the error
            app.logger.error(f"An error occurred: {str(e)}")
            # Return an error response
            abort(500, "An error occurred while fetching the assessment.")

# Route to view all the assessments
@ns.route('/assessments')
class AssessmentsResource(Resource):
    def get(post):
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
@ns.route('/mentors/feedback')
# @jwt_required()
class LeaveFeedbackResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            mentor_id = data.get('mentor_id')
            assessment_id = data.get('assessment_id')
            question_id = data.get('question_id')
            student_id = data.get('student_id')
            text = data.get('text')

            if not mentor_id or not assessment_id or not question_id or not student_id or not text:
                return make_response(jsonify({"error": 'Invalid request data'}), 400)

            # Check if the mentor exists
            mentor = Mentor.query.get(mentor_id)
            if mentor is None:
                return make_response(jsonify({"error": 'Mentor not found'}), 404)

            assessment = Assessment.query.filter_by(assessment_id=assessment_id, mentor_id=mentor_id).first()
            if assessment is None:
                return make_response(jsonify({"error": 'Assessment not found or does not belong to the mentor'}), 404)

            question = Question.query.filter_by(question_id=question_id, assessment_id=assessment_id).first()
            if question is None:
                return make_response(jsonify({"error": 'Question not found or does not belong to the assessment'}), 404)

            # Check if student exists
            student = Student.query.get(student_id)
            if student is None:
                return make_response(jsonify({"error": 'Student not found'}), 404)

            feedback = Feedback(mentor_id=mentor_id, assessment_id=assessment_id, question_id=question_id, student_id=student_id, feedback=text)
            db.session.add(feedback)
            db.session.commit()

            return jsonify({"message": 'Feedback submitted successfully'})

        except Exception as e:
            # Log the error or print to the console for debugging
            print(f"Error: {str(e)}")
            # Return a generic error message or handle the exception as needed
            return make_response(jsonify({"error": 'An error occurred while processing the request'}), 500)


# Route for mentors to release grades for an assessment
@ns.route('/mentors/grades')
class ReleaseGradesResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            mentor_id = data.get('mentor_id')
            assessment_id = data.get('assessment_id')
            score = data.get('score')
            student_id = data.get("student_id")
            assignment_id = data.get("assignment")

            if not mentor_id or not assessment_id or not score:
                response = make_response(jsonify(error='Invalid request data'), 400)
                return response

            grade = Grade(assessment_id=assessment_id, student_id=student_id, grade=score, assignment_id = assignment_id)
            db.session.add(grade)
            db.session.commit()

            response = make_response(jsonify(message='Grades released successfully'), 200)
            return response
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            response = make_response(jsonify(error='An error occurred while processing the request'), 500)
            return response


# Route for students to view their grades for a specific assessment
@ns.route('/students/grades/<int:student_id>/<int:assessment_id>')
class StudentGradeResource(Resource,):
    def get(self,student_id,assessment_id):
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