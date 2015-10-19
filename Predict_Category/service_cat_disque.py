import logging
from logging.handlers import RotatingFileHandler
import json

from constants import CATFIGHT_LOGGING_PATH
from find_categories import process_product
from settings import client, sentry_client, catfight_input, catfight_output
from objects import categoryModel, dangerousModel

logger = logging.getLogger('Catfight App')
handler = RotatingFileHandler(CATFIGHT_LOGGING_PATH, maxBytes=200000000,
                              backupCount=10)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("Loading Process Started")

try:
    dang_model = dangerousModel()
    cat_model = categoryModel()
except Exception as err:
    logger.error("Error {} while loading models".format(err))
    sentry_client.captureException(
        message = "service_category_disque : Failed to load models",
        extra = {"error" : err})

logger.info("Loading Process Complete")

ERROR_CODE = {
    'MissingProductName' : 'MissingProduct',
    'MissingProductList' : 'MissingProductList',
    'MissingWBN' : 'MissingWBN'
}

def validate_product_args(record):
    value = True
    error_response = {}
    if not record.get('prd', None):
        error_response = {'error': ERROR_CODE['MissingProductName']}
        value = False
    if not record.get('wbn', None):
        error_response = {'error': ERROR_CODE['MissingWBN']}
        value = False
    return value, error_response

def get_category(list_product_names, job_id):
    output_list = []
    logger.info("Request received {}".format(list_product_names))
    if list_product_names:
        for product_name_dict in list_product_names:
            try:
                valid_record, error_response = validate_product_args(product_name_dict)
                if valid_record:
                    result = process_product(product_name_dict,
                                            cat_model,
                                            dang_model,
                                            logger)
                    output_list.append(result)
                else:
                    for key, value in product_name_dict.items():
                        error_response[key] = value
                        output_list.append(error_response)
            except Exception as err:
                logger.error(
                    'get_category:Exception {} occurred against input: {} for job_id {}'.
                    format(err, list_product_names, job_id))
                sentry_client.captureException(
                    message = "Exception occurred against input in get_category",
                    extra = {"error" : err,"job_id" : job_id,
                             "product_name_dict" : product_name_dict})
    else:
        error_response = ERROR_CODE['MissingProductList']
        output_list.append(error_response)

    logger.info("Result produced {}".format(output_list))

    return output_list

def get_products():
    """
    Function to fetch job from disque queue, catfight_input, splitting the job
    into vendor and results, and calling search_addresses to generate products
    for the job passed 
    """
    while True:
        try:
            jobs = client.get_job([catfight_input])
            for queue_name, job_id, job in jobs:
                job_data = json.loads(job)
                vendor = job_data['vendor']
                products = json.loads(job_data['payload'])

                results = get_category(products, job_id)
                if results:
                    results_dict = {}
                    results_dict['vendor'] = vendor
                    results_dict['catfight_results'] = results
                    second_job_id = client.add_job(catfight_output,
                                                   json.dumps(results_dict),
                                                   retry = 5)
                    client.ack_job(job_id)
                    logger.info("Successfully fetched from Disque queue catfight_input GET Job ID {} with job {}".
                                format(job_id, job))
                    logger.info("Successfully added to Disque queue catfight_output with Job ID {} and job {}".
                                format(second_job_id, job))
                else:
                    logger.info("No results found for Job ID {} with job {}".
                                format(job_id, job))
        except Exception as e:
            logger.info("Function get_products failed for Job ID {} with job {} with error {}".
                        format(job_id,job,e))
            sentry_client.captureException(
                message = "get_products failed", 
                extra = {"error" : e})
            pass

if __name__=='__main__':
    get_products()

