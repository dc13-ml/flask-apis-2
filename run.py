from app import app
from db import db

db.init_app(app)

@app.before_first_request
def create_tables():
    # based on the 'SQLALCHEMY_DATABASE_URI' config parameter
    db.create_all()
