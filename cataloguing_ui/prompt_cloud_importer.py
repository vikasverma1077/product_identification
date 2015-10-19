'''
Reads product_name from .json files, identifies their cat/sub_cat and populates mongodb
Note: Make sure you change vendor name and path before running this file. Default vendor name is : 'HQ-Data'
'''
import os
import re
import sys
import numpy as np
#import logging
import json
import traceback
from multiprocessing import Pool
import csv

from pymongo import MongoClient
client = MongoClient()
db = client.products_db

result_file = "/data/cat_multi/results_"
from flask import Flask, request, Response
from sklearn.externals import joblib
#from config_details import second_level_cat_names
#from logging.handlers import RotatingFileHandler

#from Train_Model.train import ngrams
PARENT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(PARENT_DIR_PATH)

second_level_cat_names=\
            ["Beauty Products and Personal Care",
                  "Camera and Photos",
                  "Mobile Phone, Tablets and Accesories",
                  "Apparel & Accessories",
                  "Watches, Eyewear and Jewellery",
                  "Electronics and Appliances",
                  "Home and Kitchen",
                  "Computers and Laptops",
                  "Shoes and Footwear"
                 ]


second_level_cat_names_set=set(second_level_cat_names)

#logging file path
#LOGGING_PATH='/var/log/cat_subcat_logs/cat_subcat.log'

app = Flask(__name__)
"""
handler = RotatingFileHandler(LOGGING_PATH,maxBytes=10000000,backupCount=5)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

app.logger.info("Loading Process Started")
"""
vectorizer=joblib.load(PARENT_DIR_PATH+'/Models/vectorizer.pkl')
clf_bayes=joblib.load(PARENT_DIR_PATH+'/Models/clf_bayes.pkl')
clf_chi=joblib.load(PARENT_DIR_PATH+'/Models/clf_chi.pkl')
clf_fpr=joblib.load(PARENT_DIR_PATH+'/Models/clf_fpr.pkl')

second_level_vectorizer={}
second_level_clf_bayes={}
second_level_clf_fpr={}
for cat_name in second_level_cat_names_set:
    second_level_vectorizer[cat_name]=joblib.load(PARENT_DIR_PATH+'/Models/SubModels/Vectorizer_'+cat_name)
    second_level_clf_bayes[cat_name]=joblib.load(PARENT_DIR_PATH+'/Models/SubModels/clf_bayes_'+cat_name)
    second_level_clf_fpr[cat_name]=joblib.load(PARENT_DIR_PATH+'/Models/SubModels/clf_fpr_'+cat_name)

#app.logger.info("Loading Process Complete")

def predict_category(product_name):
#    app.logger.info("Request received {}".format(str(product_name)))

    try:
        l_product_name = product_name.lower()
        class1 = clf_bayes.predict(vectorizer.transform([l_product_name]))[0]
        class2_prob_vector = clf_chi.predict_proba(vectorizer.transform([l_product_name]))[0]
        class3_prob_vector = clf_fpr.predict_proba(vectorizer.transform([l_product_name]))[0]

        if len(np.unique(class2_prob_vector))==1:
            class2 = "NA"
        else:
            class2 = clf_bayes.classes_[np.argmax(class2_prob_vector)]
        if len(np.unique(class3_prob_vector))==1:
            class3 = "NA"
        else:
            class3 = clf_bayes.classes_[np.argmax(class2_prob_vector)]

        if class3 == "Delhivery_Others":
            if class1 == class2:
                first_level = class1
            elif class1 == "Delhivery_Others":
                first_level = class2
            elif class2 == "Delhivery_Others":
                first_level = class1
            else:
                first_level = class2
        else:
            first_level = class3

        second_level = ""

        if first_level in second_level_cat_names_set:
            prob_vector = second_level_clf_fpr[first_level].predict_proba(
                second_level_vectorizer[first_level].transform([l_product_name]))[0]
            if len(np.unique(prob_vector))==1:
                second_level = second_level_clf_bayes[first_level].predict(
                    second_level_vectorizer[first_level].transform([l_product_name]))[0]
            else:
                second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]


        # prob_vector= second_level_clf[class_name].predict_proba(
            #second_level_vectorizer[class_name].transform([product_name.lower()]))[0]

        #app.logger.info("Result produced {} --> {}".format(
            #str(first_level), str(second_level)))
    except Exception as err:
        print(
            'Traceback: {}'.format(traceback.format_exc()))
        print(
            'Exec Info: {}'.format(sys.exc_info())[0])
        print(
            'Exception {} occurred against product: {}'.format(
                err, product_name))
    return (first_level,second_level)

#@app.route('/get_category', methods = ['POST'])
def get_category(products):
    try:
        list_product_names = products
        #app.logger.info("Request Received {}".format (str(list_product_names)))
	    #print "Working in Process #%d" % (os.getpid())

        for product_name_dict in list_product_names:
            response = {} 
            response['category'], response['sub_category'] = predict_category(
                    product_name_dict.get('product_name',"").encode('ascii','ignore'))
            
            if response['sub_category']:
                try:
                    subcat = response['sub_category'].split('->')[1]
                except IndexError:
                    subcat= response['sub_category'].split('->')[0]
            else:
                subcat = None

            if 'product_url' not in product_name_dict:
                product_name_dict['product_url'] = None
            if 'retail_price' in product_name_dict:
                product_name_dict['retail_price'] = re.findall(r'\d+',product_name_dict['retail_price'])
                product_name_dict['retail_price'] = int(product_name_dict['retail_price'][0])
            else:
                product_name_dict['retail_price'] = None

            db.products_new.insert({"product_name": product_name_dict['product_name'],
                                "vendor": 'HQ-Data',
                                "category": response['category'],
                                "vendor_cat": response['category'],
                                "sub_category": subcat,
                                "vendor_subcat": subcat,
                                "price": product_name_dict['retail_price'],
                                "product_url": product_name_dict['product_url']})

       
    except Exception as err:
        print(
            'Exception {} occurred against payload: {}'.format(
                err, list_product_names))
        print(str(err))

def create_pool(records, start, end, diff):
    p = Pool(processes=16)
    try:
        while start < end:
            #print records[start:start+diff]
            print(start, diff, end)
            p.apply_async(get_category, args=(records[start:start+diff], ))
            start = start + diff
        p.close()
        p.join()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting...")
        p.terminate()
        p.join()


if __name__ == "__main__":
    path_to_json = os.path.join(os.path.dirname(__file__), 'data/outsource_data/snapdeal/sep/')
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    print(json_files, len(json_files))

    data = []
    records = []
    for js in json_files:
        with open(os.path.join(path_to_json, js)) as json_file:
            for line in json_file:
                data.append(json.loads(line))
    
    # print(data)
    for i in data:
        for j in i:
            try:
                records.append({'product_name': j['record']['product_name'],
                                'product_url': j['record']['product_url'],
                                'retail_price': j['record']['retail_price']
                                })
            except Exception as e:
                pass
    start = 0
    end = len(records)
    diff = int(end/16)
    create_pool(records, start, end, diff)