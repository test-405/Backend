from flask_restful import Resource, reqparse
from utils.logz import create_logger


class Hello(Resource):
    def __init__(self):
        self.logger = create_logger("hello")

    def get(self):
        return {"message": "Hello, World!"}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        args = parser.parse_args()
        return {"message": "Hello, {}!".format(args["name"])}
