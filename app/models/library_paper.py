from db import db


class LibraryPaperModel(db.Model):
    __tablename__ = 'library_paper'

    library_paper_id = db.Column(db.Integer, primary_key=True)
    library_id = db.Column(db.Integer, nullable=False)
    paper_id = db.Column(db.Integer, nullable=False)

    def to_json(self):
        return {
            'library_paper_id': self.library_paper_id,
            'library_id': self.library_id,
            'paper_id': self.paper_id
        }
    
    @classmethod
    def get_paper_list_by_library_id(cls, _library_id):
        return cls.query.filter_by(library_id=_library_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
