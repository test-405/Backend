from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from initializers import mysql
from initializers import jwt
from initializers import mongodb

from resources.hello import Hello
from resources.user import UserRegister, UserLogin, User, TokenRefresh, UserLogout
from resources.library import Library
from resources.paper import Paper, PDF
from resources.comment import Comment

from config import GLOBAL_CONFIG

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app, supports_credentials=True)

db = mysql.init_db(app)
if app.config['MONGODB_ON'] == 'True':
    mongo = mongodb.init_db(app)
jwt.init_jwt(app)

api = Api(app)

api.add_resource(UserRegister, "/api/user/register")
api.add_resource(UserLogin, "/api/user/login")
api.add_resource(UserLogout, "/api/user/logout")
api.add_resource(User, "/api/user/<int:user_id>")
api.add_resource(TokenRefresh, "/api/refresh")
api.add_resource(Hello, "/api/hello", "/", "/hello")

# library
api.add_resource(Library, "/api/library", endpoint="library")
api.add_resource(Library, "/api/library/<int:library_id>", endpoint="library_by_id")

# paper
api.add_resource(Paper, "/api/paper", endpoint="paper")
api.add_resource(Paper, "/api/paper/<int:paper_id>", endpoint="paper_by_id")

# pdf
api.add_resource(PDF, "/api/paper/<int:paper_id>/pdf", endpoint="pdf")

# comment 
api.add_resource(Comment, "/api/comment", endpoint="comment")
api.add_resource(Comment, "/api/comment/<int:comment_id>", endpoint="comment_by_id")

# test
if app.config['MONGODB_ON'] == "True" and GLOBAL_CONFIG['test'] == True:
    from resources.paper import PDFTest
    api.add_resource(PDFTest, "/api/pdftest")

if __name__ == "__main__":
    app.run(debug=True)