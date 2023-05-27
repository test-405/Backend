from db import db


class UserLibraryModel(db.Model):
    __tablename__ = 'user_library'

    user_library_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    library_id = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {
            'user_library_id': self.user_library_id,
            'user_id': self.user_id,
            'library_id': self.library_id
        }
    
    @classmethod
    def get_library_list_by_user_id(cls, _user_id):
        return cls.query.filter_by(user_id=_user_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
