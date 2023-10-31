@ns.route('/students/login')
class StudentLoginResource(Resource):
    def post(self):

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