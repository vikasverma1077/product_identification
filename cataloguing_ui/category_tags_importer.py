''' 
Creates/Updates category collection from category_attrs_mapping.csv file (present in data folder)
'''
import os
import csv
import config

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient(config.MONGO_IP, 27017)
db = client.products_db
'''
Creates a dictionary of all existing tags in database
'''
existing_tag_dict = {}
tag_dict_obj = db.categories.distinct('tags')
for dicts in tag_dict_obj:
    existing_tag_dict.update(dicts)

'''
Returns a code for a given attribute from tag_dict
if not found in tag_dict, calculates a new code and returns that
'''
def get_code(attr):
    if attr in existing_tag_dict:
        return existing_tag_dict[attr]

    for k in range(len(attr)):
        code = attr[:k+1]
        code = code.capitalize()
        if code not in existing_tag_dict.values():
            existing_tag_dict[attr] = code
            return code
    #print(existing_tag_dict)

'''
Updates tags of a given category
'''
def set_code(cat, tag_row, idd):
    '''
    Creates a dict of existing tags of given category
    '''    
    old_tag_dict = {}
    old_tag_list_obj = db.categories.find({"category_name": cat}).distinct('tags')
    for dicts in old_tag_list_obj:
        old_tag_dict.update(dicts)

    if tag_row:
        tags = tag_row.rstrip(';').split(';')
        for tag in tags:
            tag = tag.strip()
            tag = tag.lower()
            if tag not in old_tag_dict:
                old_tag_dict[tag] = get_code(tag)
        res = db.categories.update({'_id': ObjectId(idd)},
                                   {'$set': {'tags': old_tag_dict}})

''' 
Reads csv file and update category and their attributes/tags
'''
fn = os.path.join(os.path.dirname(__file__), 'data/category_attrs_mapping.csv')
reader = csv.reader(open(fn, 'r'), delimiter=',')
next(reader, None)
for row in reader:
    if row[0]:
        cat_obj = db.categories.find_and_modify(
            {"category_name": row[0]},
            {'$setOnInsert': {'par_category': None}},
            new = True,
            upsert = True
        )
        # print(cat_obj)
        set_code(row[0], row[1], cat_obj['_id'])

    if row[2]:
        subcat_obj = db.categories.find_and_modify(
            {"category_name": row[2]},
            {'$setOnInsert':{'par_category': ObjectId(cat_obj['_id'])}},
            new = True,
            upsert = True
        )
        a = db.categories.update({"_id": ObjectId(cat_obj['_id'])},
                                 {'$addToSet': {'children': ObjectId(subcat_obj['_id'])}})
        set_code(row[2], row[3], subcat_obj['_id'])

print(existing_tag_dict)