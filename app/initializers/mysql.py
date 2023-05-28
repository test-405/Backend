from db import db

def init_db(app=None):
    db.init_app(app)
    with app.app_context():
        import models
        db.create_all()

    return db