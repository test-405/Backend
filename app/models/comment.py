from db import db


class CommentModel(db.Model):
    __tablename__ = 'comment'

    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    is_markdown = db.Column(db.Boolean, nullable=False)

    def to_json(self):
        return {
            'comment_id': self.comment_id,
            'content': self.content,
            'time': self.time.isoformat(),
            'is_markdown': self.is_markdown
        }

    @classmethod
    def find_by_id(cls, _comment_id):
        return cls.query.filter_by(comment_id=_comment_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
