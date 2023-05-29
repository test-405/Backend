from pymongo import MongoClient
from db import mongo

def init_db(app):
    global mongo
    with app.app_context():
        mongo.client = MongoClient(app.config['MONGODB_URI'])
        return mongo