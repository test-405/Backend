from db import db


class LibraryModel(db.Model):
    __tablename__ = 'library'

    library_id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(80), nullable=True)
    description = db.Column(db.String(256), nullable=True)
    is_public = db.Column(db.Boolean, nullable=False)

    def to_json(self):
        return {
            'library_id': self.library_id,
            'topic': self.topic,
            'description': self.description,
            'is_public': self.is_public
        }

    @classmethod
    def find_by_id(cls, _library_id):
        return cls.query.filter_by(library_id=_library_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
