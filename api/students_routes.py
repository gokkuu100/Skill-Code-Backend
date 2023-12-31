from api import *
from flask import request
import logging

ns = Namespace('SkillCode',description='CRUD endpoints')
api.add_namespace(ns)
jwt = JWTManager(app)

# Set logging level to capture all messages
app.logger.setLevel(logging.DEBUG)

# Route for student sign-up
@ns.route('/students/signup')
class StudentSignupResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            name = data.get('name')
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
            new_student = Student(name=name, email=email, password=password_hash)
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
        

# route to retrieve a student by id
@ns.route('/students/profile')
class ViewMentorResource(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            student_id = current_user.get("student_id")

            if student_id is None:
                app.logger.error("Student id not found, login again")
                return make_response(jsonify({'error':'Student not found'}), 400)
            
            # Retrieve the student with the given id from the database
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

# get all students
# Route to retrieve all students
@ns.route('/students/list')
class AllStudentsResource(Resource):
    def get(self):
        try:
            students = Student.query.all()
            students_data = []

            for student in students:
                student_info = {
                    'id': student.student_id,
                    'name': student.name,
                    'email': student.email
                }
                students_data.append(student_info)

            return make_response(jsonify(students_data))
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Endpoint to view assessment invites and associated notifications for a student
@ns.route('/students/assessment_invites')
class StudentAssessmentInvites(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            student_id = current_user.get("student_id")

            if student_id is None:
                app.logger.error("Student id not found, login again")
                return make_response(jsonify({'error':'Student not found'}), 400)
            
            # Retrieve the Invites with the given student id from the database
            invites = Invite.query.filter_by(student_id=student_id).all()

            if invites:
                invite_data = []
                for invite in invites:
                    print("invite",invite)
                    notifications = Notification.query.filter_by(student_id=student_id, assessment_id=invite.assessment_id).all()
                    print("notification", notifications)
                    notification_data = [notification.content for notification in notifications if not isinstance(notification.content, Response)]
                    
                    # Retrieve the associated assignment for is_accepted attribute
                    assignment = Assignment.query.filter_by(assessment_id=invite.assessment_id, student_id=invite.student_id).first()
                    print("assignments", assignment)
                    is_accepted = assignment.is_accepted if assignment else None

                      # Fetch the associated mentor name
                    mentor_name = invite.assessment.mentor.name if invite.assessment and invite.assessment.mentor else None

                    # Fetch the assessment time limit
                    assessment_time_limit = invite.assessment.time_limit if invite.assessment else None

                    assessment = invite.assessment  # You need to define this relationship in your model
                    data = {
                        "invite_id": invite.invite_id,
                        "assessment_id": invite.assessment_id,
                        "notifications": notification_data,
                        "is_accepted": is_accepted,
                        "assessment_title": assessment.title if assessment else None,
                        "assessment_description": assessment.description if assessment else None,
                        "mentor_name": mentor_name,
                        "assessment_time_limit": assessment_time_limit
                    }
                    invite_data.append(data)

                return make_response(jsonify(invite_data), 200)
            else:
                return make_response(jsonify({"message": "No assessment invites found for this student"}), 404)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            logging.exception(error_message)
            return make_response(jsonify({"message": error_message}), 500)
        
# Endpoint to accept assessment invites and associated notifications for a student
@ns.route('/students/assessments/<int:assessment_id>/accept_invite')
class AcceptAssessmentInvite(Resource):
    @jwt_required()
    def post(self,assessment_id):
        try:
            current_user = get_jwt_identity()
            student_id = current_user.get("student_id")

            if student_id is None:
                app.logger.error("Student id not found, login again")
                return make_response(jsonify({'error':'Student not found'}), 400)
            # Check if the student_id and assessment_id match an existing invite
            invite = Invite.query.filter_by(student_id=student_id, assessment_id=assessment_id).first()

            if invite:
                assignment = Assignment.query.filter_by(student_id=student_id, assessment_id=assessment_id).first()

                if assignment:
                    assignment.is_accepted = True
                    assessment_title = assignment.assessment.title if assignment else "Assessment"
                    student_name = assignment.student.name if assignment else "You"
                    db.session.commit()

                    return make_response(jsonify({"message": f"Hello, {student_name}. {assessment_title} Invite accepted "}))
                else:
                     return make_response(jsonify({"message": f"No assignment found for student {student_id} and assessment {assessment_id}"}), 404)
            else:
                return make_response(jsonify({"message": f"No invite found for student {student_id} and assessment {assessment_id}"}), 404)
            
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            logging.exception(error_message)
            return make_response(jsonify({"message": error_message}), 500)

# route for student to see assigned assessments
@ns.route('/students/assessment_details')

class GetAssessmentResource(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            student_id = current_user.get("student_id")

            if student_id is None:
                app.logger.error("Student id not found, login again")
                return make_response(jsonify({'error':'Student not found'}), 400)
            
            # Query to retrieve assignments associated with the student
            assignments = Assignment.query.filter_by(student_id=student_id).all()

            if assignments:
                assessment_data = []
                for assignment in assignments:
                    assessment = assignment.assessment
                    questions = assessment.questions.all()  # Retrieves all questions related to the assessment
                    student = assignment.student

                    data = {
                        "assignment_id": assignment.assignment_id,
                        "is_accepted": assignment.is_accepted,
                        "assessment_title": assessment.title,
                        "assessment_description": assessment.description,
                        "questions": [
                            {
                                "question_id": question.question_id,
                                # "title": question.title,
                                "options": question.options,
                                "text_question": question.text_question,
                                "correct_answer": question.correct_answer
                            }
                            for question in questions
                        ]
                    }

                    assessment_data.append(data)
                
                # Assuming all assignments belong to the same student
                student = assignments[0].student 

                # Prepare the data to be returned
                response_data = {
                    "assessments": assessment_data,
                    "student_name": student.name if student else "Not assigned",
                    "student_id": student_id
                }

                return make_response(jsonify(response_data))
            else:
                return make_response(jsonify({"message": "No assignments found for this student"}), 404)
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return make_response(jsonify({"message": "An error occurred. Please check the logs for details."}), 500)


# route for students to attempt assessments
@ns.route('/students/assessments/<int:assessment_id>/submit_assessment')
class PostResponsesResource(Resource):
    @jwt_required()
    def post(self, assessment_id):
       
        try:
            current_user = get_jwt_identity()
            student_id = current_user.get("student_id")

            if student_id is None:
                app.logger.error("Student id not found, login again")
                return make_response(jsonify({'error':'Student not found'}), 400)
            
            student = Student.query.filter_by(student_id=student_id).first()
            assessment = Assessment.query.filter_by(assessment_id=assessment_id).first()
            print(assessment.assessment_id)
            if not (assessment and student):
                return make_response(jsonify({"message": "Assessment or student not found."}), 404)

            # Check if the student is assigned to the assessment
            assignment = Assignment.query.filter_by(student_id=student_id, assessment_id=assessment_id).first()

            if assignment:
                if assignment.is_accepted:
                    # Check if the assessment is already submitted by the student
                    existing_response = Response.query.filter_by(student_id=student_id, assignment_id=assignment.assignment_id).first()

                    if existing_response:
                        return make_response(jsonify({"message": "Assessment already submitted by the student."}), 400)

                    responses = request.json  # Expecting a list of responses
                    print("respinses",responses)

                    if not responses or not isinstance(responses, list):
                        return make_response(jsonify({"message": "Invalid or empty responses provided."}), 400)

                    new_responses = []
                    for response_data in responses:
                        question_id = response_data.get('question_id')
                        answer_text = response_data.get('answer_text')

                        # Check if the question exists and is associated with the provided assessment
                        question = Question.query.filter_by(question_id=question_id, assessment_id=assessment.assessment_id).first()
                        print("question",question)
                        if question:
                            new_response = Response(
                                assignment_id=assignment.assignment_id,
                                question_id=question_id,
                                student_id=student_id,
                                answer_text=answer_text
                            )
                            new_responses.append(new_response)
                        else:
                            return make_response(jsonify({"message": "Invalid question ID or not associated with the provided assessment."}), 404)

                    # Add all new responses to the session and commit
                    db.session.add_all(new_responses)
                    db.session.commit()

                    # Calculate the score based on correct answers
                    total_questions = len(new_responses)
                    correct_answers = 0
                    for response in new_responses:
                        question = Question.query.get(response.question_id)
                        if question and response.answer_text == question.correct_answer:
                            correct_answers += 1

                    # Calculate percentage 
                    score_percentage = (correct_answers / total_questions) * 100

                    # Determine grade based on the score
                    if score_percentage >= 80:
                        grade = 'A'
                    elif score_percentage >= 60:
                        grade = 'B'
                    elif score_percentage >= 40:
                        grade = 'C'
                    elif score_percentage >= 20:
                        grade = 'D'
                    else:
                        grade = 'F'

                    # Save the grade
                    new_grade = Grade(
                        student_id=student_id,
                        assessment_id=assessment_id,
                        grade=grade
                    )
                    db.session.add(new_grade)
                    db.session.commit()

                    return make_response(jsonify({"message": f"Responses submitted successfully. Grade: {grade}"}), 200)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            app.logger.exception(error_message)
            return make_response(jsonify({"message": error_message}), 500)

# Route for students to view their grades for a specific assessment
@ns.route('/students/grades/<int:assessment_id>')
class StudentGradeResource(Resource):
    @jwt_required()
    def get(self,  assessment_id):
        try:
            current_user = get_jwt_identity()
            student_id = current_user.get("student_id")

            if student_id is None:
                app.logger.error("Student id not found, login again")
                return make_response(jsonify({'error':'Student not found'}), 400)
            
            student = Student.query.get_or_404(student_id)
            assessment = Assessment.query.get_or_404(assessment_id)

            if assessment is None:
                error_message = {"message": f"No such assessment found for student {student_id}"}
                return make_response(jsonify(error_message), 404)

            grades = Grade.query.filter_by(student_id=student_id, assessment_id=assessment_id).all()

            grade_values = [grade.grade for grade in grades]

            grade_data = {
                'student_id': student.student_id,
                'student_email': student.email,
                'assessment_id': assessment.assessment_id,
                'assessment_title': assessment.title,
                'grade': grade_values
            }

            return make_response(jsonify(grade_data), 200)
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            error_response = {"message": "An error occurred. Please check the logs for details."}
            return make_response(jsonify(error_response), 500)

# Route for students to view their grades
@ns.route('/students/grades')  
class StudentGradeResource(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            student_id = current_user.get("student_id")

            if student_id is None:
                app.logger.error("Student id not found, login again")
                return make_response(jsonify({'error':'Student not found'}), 400)
            
            student = Student.query.get_or_404(student_id)

            grades = Grade.query.filter_by(student_id=student_id).all()

            grade_history = []
            for grade in grades:
                grade_data = {
                    'assessment_id': grade.assessment_id,
                    'grade_id': grade.grade_id,
                    'grade': grade.grade
                }
                grade_history.append(grade_data)

            student_info = {
                'student_id': student.student_id,
                'student_email': student.email,
                'grade_history': grade_history
            }

            return make_response(jsonify(student_info), 200)
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            error_response = {"message": "An error occurred. Please check the logs for details."}
            return make_response(jsonify(error_response), 500)
        
# Route to view question feedback 
@ns.route("/students/assessments/<int:assessment_id>/feedback")
class QuestionFeedbackResource(Resource):
    @jwt_required()
    def get(self, assessment_id):
        try:
            current_user = get_jwt_identity()
            student_id = current_user.get("student_id")

            if student_id is None:
                app.logger.error("Student id not found, login again")
                return make_response(jsonify({'error':'Student not found'}), 400)
            
            feedback = Feedback.query.filter_by(student_id=student_id, assessment_id=assessment_id).all()

            if not feedback:
                return make_response(jsonify({"message": "No feedback found for this student's assessment"}), 404)

            feedback_data = []
            for item in feedback:
                # Get details from related models using the foreign keys
                question = Question.query.get(item.question_id)
                mentor = Mentor.query.get(item.mentor_id)
                assessment = Assessment.query.get(item.assessment_id)
                student = Student.query.get(item.student_id)

                data = {
                    "question_id": item.question_id,
                    "feedback": item.feedback,
                    "mentor_name": mentor.name if mentor else None,
                    "student_name": student.name if student else None,
                    "assessment_title": assessment.title if assessment else None
                    # Add more details if necessary based on your models
                }
                feedback_data.append(data)

            response = {
                "student_id": student_id,
                "assessment_id": assessment_id,
                "feedback": feedback_data
            }

            return make_response(jsonify(response), 200)

        except Exception as e:
            app.logger.exception(f"An error occurred: {str(e)}")
            return make_response(jsonify({"message": "Error occurred while fetching question feedback"}), 500)
        

        # protecting