from pymongo import MongoClient

from app.core import config

client = MongoClient(config.mongodb_uri)


def get_db():
    return client["machine_learning_pipeline"]
