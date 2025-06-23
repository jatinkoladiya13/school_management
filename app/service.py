from pymongo import MongoClient
from bson.objectid import ObjectId
from django.conf import settings

client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client[settings.DATABASES['default']['NAME']]
users_collection = db['app_user']

def  commen_init(name):
    return db[name]

def create_user(user_data):
    result = users_collection.insert_one(user_data)
    return str(result.inserted_id)

def get_all_users():
    users = users_collection.find()
    return list(users)