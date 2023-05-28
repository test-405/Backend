from db import db


class UserPaperModel(db.Model):
    __tablename__ = 'user_paper'

    user_paper_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    paper_id = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {
            'user_paper_id': self.user_paper_id,
            'user_id': self.user_id,
            'library_id': self.paper_id
        }
    
    @classmethod
    def get_paper_list_by_user_id(cls, _user_id):
        return cls.query.filter_by(user_id=_user_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
