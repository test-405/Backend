from flask_restful import Resource, reqparse, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt_identity
from sqlalchemy.orm import sessionmaker
from fuzzywuzzy import fuzz
from db import db
from models import PaperModel, LibraryPaperModel, UserLibraryModel

from utils.logz import create_logger


class Paper(Resource):
    def __init__(self):
        self.logger = create_logger("paper")

    # 查询论文
    # library_id(required), page_num(required), page_size(required), title, ...
    def get(self):
        library_id = request.args.get("library_id", type=int)
        page_num = request.args.get("page_num", type=int)
        page_size = request.args.get("page_size", type=int)
        title = request.args.get("title", type=str)
        
        # 根据library_id查询关联表，得到librarypaper_list，再根据paper_id查询paper表，得到paper_list
        librarypaper_list = LibraryPaperModel.query.filter_by(library_id=library_id).all()
        paper_id_list = [each.json()['paper_id'] for each in librarypaper_list]

        paper_list = []
        for paper_id in paper_id_list:
            paper = PaperModel.query.filter_by(paper_id=paper_id).first()
            paper_list.append(paper.json())

        # 如果查询提供了title，则对paper_list进行模糊匹配
        if title:
            for paper in paper_list:
                paper["ratio"] = fuzz.ratio(title, paper["title"])
            paper_list = sorted(paper_list, key=lambda x: x["ratio"], reverse=True)
        
        paper_list = paper_list[:(page_num) * page_size]
        response = {
            "code": 0,
            "error_msg": "string",
            "data": {
                "papers": paper_list
            }
        }
        return response, 200

    # 添加论文
    # library_id(required), title(required), authors(required), publisher(required), year(required), source(required)
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("library_id", type=int, required=True, help="This field cannot be blank.")
        parser.add_argument("title", type=str, required=True, help="This field cannot be blank.")
        parser.add_argument("authors", type=str, required=True, help="This field cannot be blank.")
        parser.add_argument("publisher", type=str, required=True, help="This field cannot be blank.")
        parser.add_argument("year", type=int, required=True, help="This field cannot be blank.")
        parser.add_argument("source", type=str, required=True, help="This field cannot be blank.")
        data = parser.parse_args()

        uid = get_jwt_identity()
        self.logger.info("User {} is adding a paper".format(uid))

        paper = PaperModel(
            title=data["title"],
            authors=data["authors"],
            publisher=data["publisher"],
            year=data["year"],
            source=data["source"]
        )
        paper.save_to_db()

        library_paper = LibraryPaperModel(
            library_id=data["library_id"],
            paper_id=paper.paper_id
        )
        library_paper.save_to_db()
    
    # 修改论文
    # paper_id(required), title(required), library_id is not allowed to modify.
    @jwt_required()
    def put(self, paper_id):
        parser = reqparse.RequestParser()
        parser.add_argument("library_id", type=int, required=True, help="This field cannot be blank.")
        parser.add_argument("title", type=str, required=True, help="This field cannot be blank.")
        parser.add_argument("authors", type=str, required=True, help="This field cannot be blank.")
        parser.add_argument("publisher", type=str, required=True, help="This field cannot be blank.")
        parser.add_argument("year", type=int, required=True, help="This field cannot be blank.")
        parser.add_argument("source", type=str, required=True, help="This field cannot be blank.")
        data = parser.parse_args()

        uid = get_jwt_identity()
        self.logger.info("User {} is modifing paper {}".format(uid, paper_id))

        Session = sessionmaker(bind=db.engine)
        with Session() as session:
            session.begin()
            try:
                paper = session.query(PaperModel).filter_by(paper_id=paper_id).first()
                if data["title"] is not None:
                    paper.title = data["title"]
                if data["authors"] is not None:
                    paper.authors = data["authors"]
                if data["publisher"] is not None:
                    paper.publisher = data["publisher"]
                if data["year"] is not None:
                    paper.year = data["year"]
                if data["source"] is not None:
                    paper.source = data["source"]
            except:
                session.rollback()
                response = {
                    "code": 1,
                    "error_msg": "Failed to modify paper",
                    "data": paper.to_json(),
                }
                return response, 500
            else:
                response = {
                    "code": 0,
                    "error_msg": "",
                    "data": paper.to_json()
                }
                session.commit()
                return response, 200
    
    # 删除论文
    # 用户只能删除自己创建的文献库下的论文
    # 根据paper_id，找到所在的lib，先检验lib是否存在并属于该用户
    @jwt_required()
    def delete(self, paper_id):
        uid = get_jwt_identity()
        self.logger.info("User {} is deleting paper {}".format(uid, paper_id))

        library_paper = LibraryPaperModel.query.filter_by(paper_id=paper_id).first()
        library_id = library_paper.json()['library_id']
        if library_id is None:
            response = {
                "code": 1,
                "error_msg": "This paper is not in any librarys ",
                "data": {},
            }
            return response, 403
        
        user_library = UserLibraryModel.query.filter_by(user_id=uid, library_id=library_id).first()
        if user_library is None:
            response = {
                "code": 1,
                "error_msg": "This paper is not in your librarys ",
                "data": {},
            }
            return response, 403
        
        Session = sessionmaker(bind=db.engine)
        with Session() as session:
            session.begin()
            try:
                paper = session.query(PaperModel).filter_by(paper_id=paper_id).first()
                session.delete(paper)
                session.delete(library_paper)
            except:
                session.rollback()
                response = {
                    "code": 1,
                    "error_msg": "Failed to delete paper",
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