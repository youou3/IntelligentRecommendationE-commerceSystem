from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient


db = SQLAlchemy()
mongo_client = None
mongo_db = None


def init_mongo(app):
    global mongo_client, mongo_db
    mongo_client = MongoClient(app.config['MONGO_URI'])
    mongo_db = mongo_client[app.config['MONGO_DB_NAME']]
    return mongo_db


def get_mongo_db():
    return mongo_db
