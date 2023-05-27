from datetime import datetime
from flask_restful import Resource, request, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db
from sqlalchemy.orm import sessionmaker
from fuzzywuzzy import fuzz

from models import CommentModel, PaperModel, PaperCommentModel

from utils.logz import create_logger


class Comment(Resource):
    def __init__(self):
        self.logger = create_logger("comment")

    # 获取论文评论列表
    # page_num(required), page_size(required)
    def get(self):
        page_num = request.args.get("page_num", type=int)
        page_size = request.args.get("page_size", type=int)

        comment_list = CommentModel.query.all()
        comment_list = [comment.to_json() for comment in comment_list]

        comment_list = comment_list[: (page_num * page_size)]
        response = {"code": 0, "error_msg": "", "data": {"comments": comment_list}}
        return response, 200

    # 添加论文评论
    # content(required), paper_id(required)
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "content", type=str, required=True, help="This field cannot be blank."
        )
        parser.add_argument(
            "paper_id", type=int, required=True, help="This field cannot be blank."
        )
        data = parser.parse_args()

        # uid relation with comment TODO
        uid = get_jwt_identity()
        self.logger.info("User {} is creating a comment".format(uid))

        # 检查paper_id是否存在
        paper = PaperModel.query.filter_by(paper_id=data["paper_id"]).first()
        if not paper:
            response = {
                "code": 1,
                "error_msg": "There is no paper with id {}".format(data["paper_id"]),
                "data": {}
            }
            return response, 404
        
        comment = CommentModel(content=data["content"], time=datetime.now(), is_markdown=False)
        comment.save_to_db()

        paper_comment = PaperCommentModel(paper_id=data['paper_id'], comment_id=comment.comment_id)
        paper_comment.save_to_db()

    # 删除论文评论
    @jwt_required()
    def delete(self, comment_id):
        # uid TODO
        uid = get_jwt_identity()
        self.logger.info("User {} is deleting comment {}".format(uid, comment_id))

        Session = sessionmaker(bind=db.engine)
        with Session() as session:
            session.begin()
            try:
                comment = session.query(CommentModel).filter_by(comment_id=comment_id).first()
                paper_comment = session.query(PaperCommentModel).filter_by(comment_id=comment_id).first()
                if comment is None:
                    response = {
                        "code": 1,
                        "error_msg": "There is no comment with id {}".format(comment_id),
                        "data": {},
                    }
                    return response, 403
                session.delete(comment)
                session.delete(paper_comment)
        
            except Exception as e:
                self.logger.error(str(e))
                session.rollback()
                response = {
                    "code": 1,
                    "error_msg": "Failed to delete comment with id {}".format(comment_id),
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
