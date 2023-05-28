import os
import json
from dotenv import load_dotenv
load_dotenv()

##################
# MYSQL SETTINGS #
##################
MYSQL_USER = os.getenv("MYSQL_USER", default="root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", default="")
MYSQL_HOST = os.getenv("MYSQL_HOST", default="localhost")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", default="paper_test")

##################
# JWT SETTINGS   #
##################
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", default="super-secret")

##################
# USER CONFIG    #
##################
GLOBAL_CONFIG_JSON = os.getenv("GLOBAL_CONFIG_JSON", default="")
GLOBAL_CONFIG = {}
if GLOBAL_CONFIG_JSON != "":
    with open(GLOBAL_CONFIG_JSON, "r") as f:
        config = json.load(f)

####################
# CONFIG READ OVER #
####################

mysqlConfig = "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4" \
    .format(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE)

class Config:
    SQLALCHEMY_DATABASE_URI = mysqlConfig
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    JWT_SECRET_KEY = JWT_SECRET_KEY
