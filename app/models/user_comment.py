from db import db


class UserCommentModel(db.Model):
    __tablename__ = 'user_comment'

    user_comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    comment_id = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {
            'user_comment_id': self.user_comment_id,
            'user_id': self.user_id,
            'username': self.username,
            'comment_id': self.comment_id
        }
    
    @classmethod
    def get_comment_list_by_user_id(cls, _user_id):
        return cls.query.filter_by(user_id=_user_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
