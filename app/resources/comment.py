from datetime import datetime
from flask_restful import Resource, request, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db
from sqlalchemy.orm import sessionmaker
from fuzzywuzzy import fuzz

from models import UserModel, CommentModel, PaperModel, PaperCommentModel, UserCommentModel

from utils.logz import create_logger


class Comment(Resource):
    def __init__(self):
        self.logger = create_logger("comment")

    # 获取论文评论列表
    # page_num(required), page_size(required)
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()

        page_num = request.args.get("page_num", type=int)
        page_size = request.args.get("page_size", type=int)
        paper_id = request.args.get("paper_id", type=int)

        # 找到paper_id对应的所有comment
        paper_comment_list = PaperCommentModel.query.filter_by(paper_id=paper_id).all()
        paper_comment_list = [each.to_json() for each in paper_comment_list]

        # 找到所有comment以及对应的user
        user_comment_list = UserCommentModel.query.filter(UserCommentModel.comment_id.in_([each['comment_id'] for each in paper_comment_list])).all()
        user_comment_list = [each.to_json() for each in user_comment_list]

        # 找到所有comment
        comment_list = CommentModel.query.filter(CommentModel.comment_id.in_([each['comment_id'] for each in paper_comment_list])).all()
        comment_list = [each.to_json() for each in comment_list]
        
        # response里面的comments添加user属性
        for comment in comment_list:
            for user_comment in user_comment_list:
                if comment['comment_id'] == user_comment['comment_id']:
                    comment['user_id'] = user_comment['user_id']
                    comment['username'] = user_comment['username']
                    comment['is_yours'] = user_comment['user_id'] == uid
                    break

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
        user = UserModel.query.filter_by(user_id=uid).first()
        _username = user.to_json()['username']
        self.logger.info("User {} is creating a comment".format(uid))

        # 检查paper_id是否存在
        paper = PaperModel.query.filter_by(paper_id=data["paper_id"]).first()
        if not paper:
            response = {
                "code": 1,
                "error_msg": "There is no paper with id {}".format(data["paper_id"]),
                "data": {}
            }
            return response, 200
        
        comment = CommentModel(content=data["content"], time=datetime.now(), is_markdown=False)
        comment.save_to_db()

        paper_comment = PaperCommentModel(paper_id=data['paper_id'], comment_id=comment.comment_id)
        paper_comment.save_to_db()

        
        user_comment = UserCommentModel(user_id=uid, username=_username, comment_id=comment.comment_id)
        user_comment.save_to_db()

        response =  {
            "code": 0,
            "error_msg": "",
            "data": {
                "id": comment.comment_id,
                "content": comment.content,
                "time": comment.time.isoformat(),
            }
        }
        return response, 200

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
                user_comment = session.query(UserCommentModel).filter_by(comment_id=comment_id).first()
                if comment is None:
                    response = {
                        "code": 1,
                        "error_msg": "There is no comment with id {}".format(comment_id),
                        "data": {},
                    }
                    return response, 200
                session.delete(comment)
                session.delete(paper_comment)
                session.delete(user_comment)
        
            except Exception as e:
                self.logger.error(str(e))
                session.rollback()
                response = {
                    "code": 1,
                    "error_msg": "Failed to delete comment with id {}".format(comment_id),
                    "data": {},
                }
                return response, 200
            else:
                response = {
                    "code": 0,
                    "error_msg": "",
                    "data": {},
                }
                session.commit()
                return response, 200
