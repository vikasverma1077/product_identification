import config

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient(config.MONGO_IP, 27017)
db = client.products_db


def add_user(user_dict):
    '''
    Adds a user to the users dict
    '''
    to_retain = ['id', 'name', 'gender', 'email', 'link']
    print(user_dict)
    data_dict = {}
    for key in to_retain:
        if key in user_dict:
            data_dict[key] = user_dict[key]
    print(data_dict)
    try:
        user_c = db.users.find({'id': data_dict['id']}).count()
        print('******************success*********************')
        if user_c < 1:
            data_dict.update({'tags':0, 'tags_verified':0})
            a = db.users.update({'id': data_dict['id']}, data_dict, upsert=True)
            print('update result...', a)
            return a
        else:
            return 0
    except Exception as e:
        print('##################error#######################')
        print(str(e))


def get_tag_count(user_id):
    tags = db.users.find_one({"id": user_id})
    return tags['tags'], tags['tags_verified']


def inc_tag_count(user_id, admin=False):
    if admin:
        db.users.update({'id': user_id}, {'$inc': {'tags_verified': 1}})
    else:
        db.users.update({'id': user_id}, {'$inc': {'tags': 1}})

def dcr_tag_count(user_id, admin=False):
    if admin:
        db.users.update({'id': user_id}, {'$inc': {'tags_verified': -1}})
    else:
        db.users.update({'id': user_id}, {'$inc': {'tags': -1}})    

def get_users():
    return db.users.find({},{'name':1, 'tags':1, 'tags_verified':1, 'email':1, 'id':1, '_id':0}).sort([('tags', -1)])