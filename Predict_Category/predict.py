import os
import sys
import logging
import json
import re

from flask import Flask, request,Response
from logging.handlers import RotatingFileHandler

from objects import categoryModel, dangerousModel
from find_categories import predict_category
from constants import ALPHA_NUM_REGEX, CACHE_EXPIRY
from settings import r, sentry_client

PARENT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(PARENT_DIR_PATH)

#logging file path
LOGGING_PATH = '/var/log/cat_subcat_logs/cat_subcat.log'

app = Flask(__name__)
handler = RotatingFileHandler(LOGGING_PATH, maxBytes = 100000000, backupCount = 5)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

app.logger.info("Loading Process Started")

try:
    dang_model = dangerousModel()
    cat_model = categoryModel()
except Exception as err:
    app.logger.error("Error {} while loading models".format(err))
    sentry_client.captureException(
        message = "service_category_disque : Failed to load models",
        extra = {"error" : err})
    sys.exit()

app.logger.info("Loading Process Complete")

@app.route('/get_category', methods = ['POST'])
def get_category():
    try:
        list_product_names = list(request.get_json())
        output_list = []

        for product_name_dict in list_product_names:
            app.logger.info("Request received {}".format(product_name_dict))
            results = {}
            results_cache = ''
            
            product_name = product_name_dict.get('product_name', "")
            if product_name:
                product_name_clean = (re.sub(ALPHA_NUM_REGEX, '', product_name)).lower()
                product_name_key = 'catfight:' +':' + product_name_clean
                results_cache = r.get(product_name_key)
                if not results_cache:
                    results = predict_category(product_name.encode('ascii','ignore'),
                                               cat_model, dang_model, app.logger)
                    if results:
                        r.setex(product_name_key, json.dumps(results), CACHE_EXPIRY)
                        results['cached'] = False
                else:
                    results = json.loads(results_cache)
                    results['cached'] = True
            else:
                results['invalid_product_name'] = True
            
            results['waybill'] = product_name_dict.get('wbn', None)
            
            app.logger.info("Result produced {}".format(results))
    
            output_list.append(results)

        return Response(json.dumps(output_list),  mimetype='application/json')
    
    except Exception as err:
        app.logger.error(
            'Exception {} occurred against payload: {}'.format(
                err, list_product_names))

        sentry_client.captureException(
            message = "predict.py: Exception occured",
            extra = {"error" : err, "payload" : list_product_names})

if __name__=='__main__':
    app.run()

