from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Mongo:
    def __init__(self):
        self.client = None

mongo = Mongo()