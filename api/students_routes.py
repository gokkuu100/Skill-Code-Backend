from ..api import *

ns = Namespace('SkillCode',description='CRUD endpoints')
api.add_namespace(ns)
jwt = JWTManager(app)



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
        

# # route to display assessment associated to a student and the questions associated to the assessment
# @ns.route('/students/<int:student_id')

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
    

    
# Route for students to view their grades for a specific assessment
@ns.route('/students/grades/<int:student_id>/<int:assessment_id>')
class StudentGradeResource(Resource):
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


@ns.route('/students/<int:student_id>')
class ViewMentorResource(Resource):
    def get(self, student_id):
        try:
            student = Student.query.get_or_404(student_id)
            student_data = {
                'id': student.student_id,
                'name': student.name,
                'email': student.email,
                
                'assignments': [{
                    'id': assignment.assignment_id,
                    'assessment_id': assignment.assessment_id
                } for assignment in student.assignments]
            }
            return make_response(jsonify(student_data))
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500











