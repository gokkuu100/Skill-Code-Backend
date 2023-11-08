from ..api import *
from flask_jwt_extended import get_jwt_identity


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
                return make_response(jsonify(error='Invalid request data'), 400)

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
            return make_response(jsonify({'access_token': access_token}), 200)
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
        
# Profile for specific mentor
@ns.route('/mentors/profile')
class ViewMentorResource(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get the mentor ID from the JWT token
            current_user = get_jwt_identity()
            mentor_id = current_user.get("mentor_id")
            
            if mentor_id is None:
                app.logger.error("Mentor ID not found in the JWT data")
                return make_response(jsonify({'error': 'Mentor ID not found'}), 404)

            mentor = Mentor.query.get_or_404(mentor_id)

            # Retrieve assessments created by the mentor
            assessments = Assessment.query.filter_by(mentor_id=mentor_id).all()
            assessment_list = []
            for assessment in assessments:
                assessment_data = {
                    'id': assessment.assessment_id,
                    'title': assessment.title,
                    'description': assessment.description,
                }
                assessment_list.append(assessment_data)

            mentor_data = {
                'id': mentor.mentor_id,
                'name': mentor.name,
                'email': mentor.email,
                'assessments': assessment_list
            }

            return make_response(jsonify(mentor_data), 200)

        except Exception as e:
            app.logger.error(f"An unexpected error occurred: {str(e)}")
            # Return an error response with status code 500 (Internal Server Error)
            return make_response(jsonify({'error': 'An unexpected error occurred'}), 500)


# Assessment create
@ns.route('/assessments/create')
class CreateAssessmentResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()

            # Retrieve assessment data from request
            title = data.get('title')
            description = data.get('description')
            questions_data = data.get('questions', [])

            if not title or not description or not questions_data:
                return jsonify(error='Invalid request data'), 400

            # Get mentor_id from the token
            mentor_id = get_jwt_identity()['mentor_id']

            # Create a new assessment object
            assessment = Assessment(title=title, description=description, mentor_id=mentor_id)
            db.session.add(assessment)
            db.session.commit()

            # Create questions and associate them with the assessment
            for question_data in questions_data:
                question_text = question_data.get('text_question')
                options = question_data.get('options', [])
                correct_answer = question_data.get('correct_answer')

                if not question_text or len(options) != 4 or not correct_answer:
                    db.session.rollback()  # Rollback the transaction if any question data is invalid
                    return make_response(jsonify(error='Invalid question data'), 400)

                # Create a new question object
                question_options = '\n'.join(options)
                question = Question(
                    text_question=question_text,
                    options=question_options,
                    correct_answer=correct_answer,
                    assessment_id=assessment.assessment_id,
                    mentor_id=mentor_id
                )
                db.session.add(question)

            db.session.commit()

            return make_response(jsonify(message='Assessment and questions created successfully', assessment_id=assessment.assessment_id), 201)

        except Exception as e:
            db.session.rollback()  
            return make_response(jsonify(error=str(e)), 500)     
        
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
                    'options': question.options.split('*'),
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
    def get(get):
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


# Route mentor to give feedback on specific question of assessment
@ns.route('/mentors/feedback')
class LeaveFeedbackResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            
            assessment_id = data.get('assessment_id')
            question_id = data.get('question_id')
            student_id = data.get('student_id')
            text = data.get('text')
            mentor_id = get_jwt_identity()['mentor_id']
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

            return make_response(jsonify({"message": 'Feedback submitted successfully'}))

        except Exception as e:
            # Log the error or print to the console for debugging
            print(f"Error: {str(e)}")
            # Return a generic error message or handle the exception as needed
            return make_response(jsonify({"error": 'An error occurred while processing the request'}), 500)

   
# Route to view each student's answer
@app.route('/SkillCode/assessments/<int:assessment_id>/students/<int:student_id>/answers', methods=['GET'])
def get_student_answers(assessment_id, student_id):
    assessment = Assessment.query.get(assessment_id)
    if assessment:
        assignment = Assignment.query.filter_by(assessment_id=assessment_id, student_id=student_id).first()
        if assignment:
            
            responses = assignment.responses
            response_data = []
            for response in responses:
                response_data.append({
                    'question_id': response.question_id,
                    'answer_text': response.answer_text,
                    # 'score': response.score
                })
            return jsonify({'responses': response_data}), 200
        else:
            return jsonify({'error': 'Assignment not found'}), 404
    else:
        return jsonify({'error': 'Assessment not found'}), 404



# Route to send invitations as assignments
@ns.route('/assessments/invite')
class InviteStudentResource(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            assessment_id = data.get('assessment_id')
            student_email = data.get('student_email')

            # Get the mentor_id and mentor's email from the token
            mentor_id = get_jwt_identity().get('mentor_id')
            mentor_email = get_jwt_identity().get('email')

            # Check if the assessment belongs to the logged-in mentor
            assessment = Assessment.query.filter_by(assessment_id=assessment_id, mentor_id=mentor_id).first()
            if not assessment:
                return make_response(jsonify(error='Assessment not found or does not belong to the mentor'), 404)

            # Check if the student with the provided email exists
            student = Student.query.filter_by(email=student_email).first()
            if not student:
                return make_response(jsonify(error='Student not found with the provided email'), 404)

            # Create an assignment record for the student
            assignment = Assignment(
                assessment_id=assessment_id,
                mentor_id=mentor_id,
                student_id=student.student_id,
                is_accepted=False
            )
            db.session.add(assignment)

            # Create an invite record linking the assessment, mentor, and student
            invite = Invite(
                assessment_id=assessment_id,
                mentor_id=mentor_id,
                student_id=student.student_id
            )
            db.session.add(invite)

            db.session.commit()

            # Send invitation email using Flask-Mail with the mentor's email as the sender
            send_invitation_email(mentor_email, student_email, assessment.title)

            return make_response(jsonify(message='Student invited to the assessment successfully'), 201)

        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)



