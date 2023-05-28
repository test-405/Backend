from flask_restful import Resource, reqparse, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt_identity
from sqlalchemy.orm import sessionmaker
from fuzzywuzzy import fuzz
from db import db
from models import PaperModel, LibraryModel, LibraryPaperModel, UserLibraryModel, UserPaperModel

from utils.logz import create_logger


class Paper(Resource):
    def __init__(self):
        self.logger = create_logger("paper")

    # 查询论文
    # library_id(required), page_num(required), page_size(required), title, ...
    # fix: 需要检查library_id对应的library, TODO:重复代码优化？
    def get(self):
        library_id = request.args.get("library_id", type=int)
        page_num = request.args.get("page_num", type=int)
        page_size = request.args.get("page_size", type=int)
        title = request.args.get("title", type=str)

        library = LibraryModel.query.filter_by(library_id=library_id).first()

        # 检查library_id对应的library是否存在
        if library is None:
            response = {
                "code": 1,
                "error_msg": "library_id not found",
                "data": {},
            }
            return response, 403
        
        # 如果是public的library，可以直接访问
        if library.to_json()['is_public']:
            # 根据library_id查询关联表，得到librarypaper_list，再根据paper_id查询paper表，得到paper_list
            librarypaper_list = LibraryPaperModel.query.filter_by(library_id=library_id).all()
            paper_id_list = [each.to_json()['paper_id'] for each in librarypaper_list]
            paper_list = PaperModel.query.filter(PaperModel.paper_id.in_(paper_id_list)).all()
            paper_list = [each.to_json() for each in paper_list]

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

        # 辅助函数：private_check
        @jwt_required()
        def private_check():
            uid = get_jwt_identity()
            if uid:
                user_library = UserLibraryModel.query.filter_by(user_id=uid, library_id=library_id).first()
                if user_library is not None:
                    return True
            return False
        
        if private_check():
            # 根据library_id查询关联表，得到librarypaper_list，再根据paper_id查询paper表，得到paper_list
            librarypaper_list = LibraryPaperModel.query.filter_by(library_id=library_id).all()
            paper_id_list = [each.to_json()['paper_id'] for each in librarypaper_list]
            paper_list = PaperModel.query.filter(PaperModel.paper_id.in_(paper_id_list)).all()
            paper_list = [each.to_json() for each in paper_list]

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
        else:
            response = {
                "code": 1,
                "error_msg": "permission denied: private library can only be accessed by owner",
                "data": {},
            }
            return response, 403

    # 添加论文
    # library_id(required), title(required), authors(required), publisher(required), year(required), source(required)
    # TODO: 该library_id对应的library必须存在，如果是私有的，必须是该用户创建的，如果是别人的library，必须是public
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("library_id", type=int, required=True, help="This field cannot be blank.")
        parser.add_argument("title", type=str, required=False)
        parser.add_argument("authors", type=str, required=False)
        parser.add_argument("publisher", type=str, required=False)
        parser.add_argument("year", type=int, required=False)
        parser.add_argument("source", type=str, required=False)
        data = parser.parse_args()

        uid = get_jwt_identity()
        self.logger.info("User {} is adding a paper".format(uid))

        # 检查library_id是否存在
        userlibrary = UserLibraryModel.query.filter_by(library_id=data["library_id"]).first()
        if not userlibrary:
            response = {
                "code": 1,
                "error_msg": "Library {} does not exist".format(data["library_id"]),
                "data": {}
            }
            return response, 404
        
        # 检查library是否属于uid，或者是否是public
        library = LibraryModel.query.filter_by(library_id=data["library_id"]).first()
        is_public = library.to_json()['is_public']
        if userlibrary.to_json()['user_id'] == uid or is_public == 1:
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

            user_paper = UserPaperModel(
                user_id=uid,
                paper_id=paper.paper_id
            )
            user_paper.save_to_db()
        # 如果library不属于uid，也不是public
        else:
            response = {
                "code": 1,
                "error_msg": "Library {} is not public".format(data["library_id"]),
                "data": {}
            }
            return response, 403

    
    # 修改论文
    # paper_id(required), title(required), library_id is not allowed to modify.
    # [fix]用户可以修改自己提交的论文
    # TODO:用户应该也可以修改自己库中别人的论文
    @jwt_required()
    def put(self, paper_id):
        parser = reqparse.RequestParser()
        parser.add_argument("library_id", type=int, required=False)
        parser.add_argument("title", type=str, required=False)
        parser.add_argument("authors", type=str, required=False)
        parser.add_argument("publisher", type=str, required=False)
        parser.add_argument("year", type=int, required=False)
        parser.add_argument("source", type=str, required=False)
        data = parser.parse_args()

        uid = get_jwt_identity()
        self.logger.info("User {} is modifing paper {}".format(uid, paper_id))

        Session = sessionmaker(bind=db.engine)
        with Session() as session:
            session.begin()
            try:
                paper = session.query(PaperModel).filter_by(paper_id=paper_id).first()
                user_paper = session.query(UserPaperModel).filter_by(paper_id=paper_id).first()
                if user_paper.to_json()['user_id'] != uid:
                    response = {
                        "code": 1,
                        "error_msg": "permission denied: user can only modify his own paper",
                        "data": {},
                    }
                    return response, 403
                
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
            except Exception as e:
                self.logger.error(str(e))
                session.rollback()
                response = {
                    "code": 1,
                    "error_msg": "Failed to modify paper",
                    "data": {},
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
    # [fix]用户能删除自己的论文
    # 用户可以删除自己库下的所有论文
    @jwt_required()
    def delete(self, paper_id):
        uid = get_jwt_identity()
        self.logger.info("User {} is deleting paper {}".format(uid, paper_id))


        Session = sessionmaker(bind=db.engine)
        with Session() as session:
            session.begin()
            try:
                paper = session.query(PaperModel).filter_by(paper_id=paper_id).first()
                user_paper = session.query(UserPaperModel).filter_by(paper_id=paper_id).first()
                library_paper = session.query(LibraryPaperModel).filter_by(paper_id=paper_id).first()

                library_id = library_paper.to_json()['library_id']
                user_library = session.query(UserLibraryModel).filter_by(library_id=library_id).first()

                # paper不存在
                if paper is None:
                    response = {
                        "code": 1,
                        "error_msg": "Paper {} does not exist".format(paper_id),
                        "data": {},
                    }
                    return response, 404
                # paper不属于该user，且paper所在的library不属于该user
                if user_paper.to_json()['user_id'] != uid and user_library.to_json()['user_id'] != uid:
                    response = {
                        "code": 1,
                        "error_msg": "permission denied: the paper is not yours or in your library",
                        "data": {},
                    }
                    return response, 403
                
                # 该paper属于该user，或所在library属于该user，均可删除
                session.delete(paper)
                session.delete(user_paper)
                session.delete(library_paper)

            except Exception as e:
                self.logger.error(str(e))
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