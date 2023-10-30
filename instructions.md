## Migrations

```bash
cd Skill-Code-Backend
export FLASK_APP=app.py
flask db init
flask db migrate
flask db upgrade
```

## SEED DB WITH RECORDS

```bash
python3 seed.py
```

## start app
```bash
flask run
```