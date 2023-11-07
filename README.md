
# Skill Assessment Flask App

This Flask application manages skill assessments.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create the database and apply migrations:

```bash
python create_db.py
python manage.py db upgrade
```

## Seeding Fake Data

To populate the database with test data:

```bash
python seed_db.py
```

## Running the Application

Start the Flask application:

```bash
python app.py
```

Access the application at `http://localhost:6000`.

## Endpoints

- `POST /assessments/create`: Create a new assessment.

### Assessment JSON Format

```json
{
    "title": "Assessment Title",
    "description": "Assessment Description",
    "time_limit": "60 minutes",
    "type": "Technical"
}
```

## Known Issues

- None
