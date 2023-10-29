from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skill_code.db' 
db = SQLAlchemy(app)

@app.route('/assessments/create', methods=['POST'])
def create():
    data = request.get_json()
    title = data.get('title')
    questions = data.get('questions')
    assessment_type = data.get('type')

    return make_response(jsonify(message='Assessment created successfully'), 200)

from .api import app, routes




if __name__ == '__main__':
    app.run(port=5555, debug=True)



