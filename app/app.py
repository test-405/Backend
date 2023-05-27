from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS # TODO

from db import db
from blocklist import BLOCKLIST
# from resources.item import Item, ItemList
# TODO
from resources.hello import Hello
from resources.user import UserRegister, UserLogin, User, TokenRefresh, UserLogout
from resources.library import Library
from config import mysqlConfig

app = Flask(__name__)
CORS(app) # TODO
app.config["SQLALCHEMY_DATABASE_URI"] = mysqlConfig
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
db.init_app(app)
api = Api(app)

"""
JWT related configuration. The following functions includes:
1) add claims to each jwt
2) customize the token expired error message
"""
app.config["JWT_SECRET_KEY"] = "jose"
jwt = JWTManager(app)

"""
`claims` are data we choose to attach to each jwt payload
and for each jwt protected endpoint, we can retrieve these claims via `get_jwt_claims()`
one possible use case for claims are access level control, which is shown below
"""


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    # TODO: Read from a config file instead of hard-coding
    if identity == 1:
        return {"is_admin": True}
    return {"is_admin": False}


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh_token_required"}
        ),
        401,
    )


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )


# JWT configuration ends


with app.app_context():
    import models  # noqa: F401

    db.create_all()


# api.add_resource(Item, "/item/<string:name>")
# api.add_resource(ItemList, "/item")
api.add_resource(UserRegister, "/api/user/register")
api.add_resource(UserLogin, "/api/user/login")
api.add_resource(UserLogout, "/api/user/logout")
api.add_resource(User, "/api/user/<int:user_id>")
api.add_resource(TokenRefresh, "/api/refresh")
api.add_resource(Hello, "/api/hello", "/", "/hello")

# library
api.add_resource(Library, "/api/library", endpoint="library")
api.add_resource(Library, "/api/library/<int:library_id>", endpoint="library_by_id")

if __name__ == "__main__":
    app.run(debug=True)