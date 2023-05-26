from db import db


class PaperModel(db.Model):
    __tablename__ = 'paper'

    paper_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    authors = db.Column(db.String(256), nullable=True)
    publisher = db.Column(db.String(256), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    source = db.Column(db.String(256), nullable=True)

    def json(self):
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': self.authors,
            'publisher': self.publisher,
            'year': self.year,
            'source': self.source
        }

    @classmethod
    def find_by_id(cls, _paper_id):
        return cls.query.filter_by(paper_id=_paper_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
