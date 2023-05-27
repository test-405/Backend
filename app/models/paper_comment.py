from db import db


class PaperCommentModel(db.Model):
    __tablename__ = 'paper_comment'

    paper_comment_id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, nullable=False)
    comment_id = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {
            'paper_comment_id': self.paper_comment_id,
            'paper_id': self.paper_id,
            'comment_id': self.comment_id
        }
    
    @classmethod
    def get_comment_list_by_paper_id(cls, _paper_id):
        return cls.query.filter_by(paper_id=_paper_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
