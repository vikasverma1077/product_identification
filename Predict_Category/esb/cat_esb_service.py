__author__ = 'delhivery'

import httplib
import json
import sys
import traceback

from zato.server.service import Service

QUEUED = 'Q'
ERROR_CODE = {
    'MissingProduct': 'MissingProduct',
    'MissingProductList':'MissingProductList'
}


def validate_product_args(record):
    value = True
    error_response = {}
    if not record.get('product_name', None):
        error_response = {'error': ERROR_CODE['MissingProduct']}
        value = False
    return value, error_response


def is_valid_product_payload(payload):
    valid = True
    response = []
    if not payload:
        response.append({'error': ERROR_CODE['MissingProductList']})
        valid = False
    else:
        for record in payload:
            valid_record, error_response = validate_product_args(record)
            if error_response:
                for key, value in record.items():
                    error_response[key] = value
                response.append(error_response)
            valid = valid and valid_record
    return valid, response


class CategoryService(Service):
    '''
    Service to get categories from products synchronously
    '''

    @staticmethod
    def get_name():
        return 'get_category'

    def handle(self):
        payload = self.request.payload

        data = []
        extra = []

        for record in payload:
            data_ = {
                'product_name': record.pop('product_name'),
                'wbn': record.pop('waybill', '')
            }
            data.append(data_)
            extra.append(record)

        try:
            outgoing = self.outgoing.plain_http.get('ProductCategory')
            headers = {'Content-type': 'application/json'}
            
            segments = outgoing.conn.post(
                self.cid,
                data=json.dumps(data),
                headers=headers)
            
            response = []
            
            if segments.status_code == httplib.OK:
                segments = json.loads(segments.text)

                for record, extra_ in zip(segments, extra):
                    record.update(**extra_)
                    response.append(record)
            else:
                self.response.status_code = segments.status_code

            self.response.payload = json.dumps(response)

        except Exception as err:
            self.logger.error(
                'Exception {} occurred against payload: {} segments: {}'.format(
                    err, data, segments))
            self.logger.error(
                'Traceback: {}'.format(traceback.format_exc()))
            self.logger.error(
                'Exec Info: {}'.format(sys.exc_info())[0])


class AsyncCategoryService(Service):
    """
    Service to get categories for a product synchronously
    @api {POST} /category/predict Request to get categories for a product
    @apiSampleRequest off
    @apiVersion 0.1.0
    @apiName RequestProductCategory
    @apiGroup Category
    @apiDescription This API allows a user to get the category and sub-category of a product based on the product name.

    @apiHeader  {String}    Authorization   Authorization Credentials
    @apiHeader  {String}    content-type    application/json
    @apiParam   {Object[]}  products        List of product objects
    @apiParam   {String}    products.product_name   Product Name String
    @apiParam   {Object}    [products.extra] Additional identifiers [wbn etc]

    @apiSuccess {String} cid            Unique identifier for the request

    @apiExample Example Usage:
        import json, requests
        payload = [{
            "product_name":"Samsung Galaxy s3 i9300"
            }, {
            "product_name":"Red SkullCandy Earphones"
            }, {
            "product_name":"Toshiba z4-a Ultrabook Laptop",
            'wbn':'1231212'
            }]

        headers = {'Content-type': 'application/json'}

        url = 'http://api.delhivery.io/category/predict'

        r = requests.post(url, data=json.dumps(payload), headers=headers)

    @apiSuccessExample Success-Response:
        HTTP/1.1 200 OK
        {
            'cid': 'K001006186845405187400962847840262893088'
        }

    @apiError (400 Bad Request) MissingProduct         Product Name either missing or None
    @apiError (400 Bad Request) MissingProductList     Product List either missing or None

    @apiErrorExample Error-Response:
        HTTP/1.1 400 Bad Request
        {[
            'error': 'MissingProductList'
        ]}

        HTTP/1.1 400 Bad Request
        {[
            'error': 'MissingProduct',
            'product_name': ''
        }]

    """

    @staticmethod
    def get_name():
        return 'async_category'

    def handle(self):
        try:
            payload = self.request.payload
            cid = self.cid
            status_code = httplib.OK

            valid, response = is_valid_product_payload(payload)
            if not valid:
                status_code = httplib.BAD_REQUEST
            else:
                msg = {
                    'service': CategoryService.get_name(),
                    'payload': payload,
                    'cid': cid
                }

                self.invoke_async(
                    'async_store', msg, to_json_string=True)

                response = {
                    'cid': cid
                }
                self.kvdb.conn.set(cid, QUEUED)
            self.response.status_code = status_code
            self.response.payload = json.dumps(response)

        except Exception as err:
            self.logger.error(
                'Exception {} occurred against payload: {}'.format(
                    err, payload))
            self.logger.error(
                'Traceback: {}'.format(traceback.format_exc()))
            self.logger.error(
                'Exec Info: {}'.format(sys.exc_info())[0])


