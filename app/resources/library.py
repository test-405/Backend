from flask_restful import Resource, request, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db
from sqlalchemy.orm import sessionmaker
from fuzzywuzzy import fuzz

from models import LibraryModel, UserLibraryModel

from utils.logz import create_logger


class Library(Resource):
    def __init__(self):
        self.logger = create_logger("library")

    def get(self):
        page_num = request.args.get("page_num", type=int)
        page_size = request.args.get("page_size", type=int)
        topic = request.args.get("topic", type=str)

        library_list = LibraryModel.query.filter_by(is_public=True).all()
        library_list = [library.to_json() for library in library_list]

        if topic:
            for library in library_list:
                library["ratio"] = fuzz.ratio(topic, library["topic"])
            library_list = sorted(library_list, key=lambda x: x["ratio"], reverse=True)

        library_list = library_list[: (page_num * page_size)]
        response = {"code": 0, "error_msg": "", "data": {"libraries": library_list}}

        return response, 200

    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "topic", type=str, required=True, help="This field cannot be blank."
        )
        parser.add_argument(
            "desc", type=str, required=True, help="This field cannot be blank."
        )
        parser.add_argument(
            "is_public", type=bool, required=True, help="This field cannot be blank."
        )
        data = parser.parse_args()

        uid = get_jwt_identity()
        self.logger.info("User {} is creating a library".format(uid))

        library = LibraryModel(
            topic=data["topic"], description=data["desc"], is_public=data["is_public"]
        )
        library.save_to_db()

        user_library = UserLibraryModel(user_id=uid, library_id=library.library_id)
        user_library.save_to_db()

        response = {
            "code": 0,
            "error_msg": "",
            "data": library.to_json(),
        }
        return response, 200

    @jwt_required()
    def put(self, library_id):
        parser = reqparse.RequestParser()
        parser.add_argument("topic", type=str, required=False)
        parser.add_argument("desc", type=str, required=False)
        parser.add_argument("is_public", type=bool, required=False)
        data = parser.parse_args()

        uid = get_jwt_identity()
        self.logger.info("User {} is updating library {}".format(uid, library_id))

        user_library = UserLibraryModel.query.filter_by(
            user_id=uid, library_id=library_id
        ).first()
        if user_library is None:
            response = {
                "code": 1,
                "error_msg": "User is not authorized to modify this library",
                "data": {},
            }
            return response, 403

        Session = sessionmaker(bind=db.engine)
        with Session() as session:
            session.begin()
            try:
                library = (
                    session.query(LibraryModel).filter_by(library_id=library_id).first()
                )
                if data["topic"] is not None:
                    library.topic = data["topic"]
                if data["desc"] is not None:
                    library.description = data["desc"]
                if data["is_public"] is not None:
                    library.is_public = data["is_public"]
            except Exception as e:
                self.logger.error(str(e))
                session.rollback()
                response = {
                    "code": 1,
                    "error_msg": "Failed to update library",
                    "data": library.to_json(),
                }
                return response, 500
            else:
                response = {"code": 0, "error_msg": "", "data": library.to_json()}
                session.commit()
                return response, 200

    @jwt_required()
    def delete(self, library_id):
        uid = get_jwt_identity()
        self.logger.info("User {} is deleting library {}".format(uid, library_id))

        Session = sessionmaker(bind=db.engine)
        with Session() as session:
            session.begin()
            try:
                user_library = (
                    session.query(UserLibraryModel)
                    .filter_by(user_id=uid, library_id=library_id)
                    .first()
                )
                if user_library is None:
                    response = {
                        "code": 1,
                        "error_msg": "User is not authorized to delete this library",
                        "data": {},
                    }
                    return response, 403

                library = (
                    session.query(LibraryModel).filter_by(library_id=library_id).first()
                )
                session.delete(library)
                session.delete(user_library)
            except Exception as e:
                self.logger.error(str(e))
                session.rollback()
                response = {
                    "code": 1,
                    "error_msg": "Failed to delete library",
                    "data": {},
                }
                return response, 500
            else:
                response = {
                    "code": 0,
                    "error_msg": "",
                    "data": {},
                }
                session.commit()
                return response, 200
