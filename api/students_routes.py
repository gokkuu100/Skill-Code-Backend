from ..api import *
import logging

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
        

# route to retrieve a student by id
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

# Endpoint to view assessment invites and associated notifications for a student
@ns.route('/students/<int:student_id>/assessment_invites')
class StudentAssessmentInvites(Resource):
    def get(self, student_id):
        try:
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

# route for student to see assigned assessments
@ns.route('/assessment_details/<int:student_id>')
class GetAssessmentResource(Resource):
    def get(self, student_id):
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
                            "title": question.title,
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

            return jsonify(response_data)
        else:
            return jsonify({"message": "No assignments found for this student"}), 404



    
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
    

# Route to accept an invite
@ns.route("/students")
class AcceptInviteStudentResource(Resource):
    # @jwt_required
    def post(self):
        pass   
    