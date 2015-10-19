define({ api: [
  {
    "type": "POST",
    "url": "/category/results",
    "title": "Fetch queued request response",
    "version": "0.1.0",
    "name": "FetchAddFixSegment",
    "group": "Category",
    "header": {
      "fields": {
        "Header": [
          {
            "group": "Header",
            "type": "String",
            "field": "Authorization",
            "optional": false,
            "description": "<p>Authorization Credentials</p>"
          },
          {
            "group": "Header",
            "type": "String",
            "field": "content-type",
            "optional": false,
            "description": "<p>application/json</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "cid",
            "optional": false,
            "description": "<p>CID against a get_category request</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object[]",
            "field": "List",
            "optional": false,
            "description": "<p>of product             List of product objects</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "field": "product.category",
            "optional": false,
            "description": "<p>Category determined for the product</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "field": "product.subcategory",
            "optional": false,
            "description": "<p>Subcategory within the Category Determined Earlier</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success-Response:",
          "content": "Success-Response:\n      HTTP/1.1 200 OK\n      [{\n      u'category': u'Mobile Phone, Tablets and Accesories',\n      u'sub_category': u'Mobile Phone, Tablets and Accesories->Mobile Accessories'\n      },\n      {\n      u'category': u'Electronics and Appliances',\n      u'sub_category': u'Electronics and Appliances->Headphones and Earphones'\n      },\n      {\n      u'category': u'Computers and Laptops',\n      u'sub_category': u'Computers and Laptops->Laptop',\n      u'wbn': u'1231212'\n      }]\n",
          "type": "json"
        }
      ]
    },
    "examples": [
      {
        "title": "Example Usage:",
        "content": "Example Usage:\n      import json, requests\n      payload = {\n          \"cid\":\"K001006186845405187400962847840262893088\",\n      }\n       headers = {'Content-type': 'application/json'}\n       url = 'http://api.delhivery.io/category/results'\n       r = requests.post(url, data=json.dumps(payload), headers=headers)\n",
        "type": "json"
      }
    ],
    "error": {
      "fields": {
        "404 Not Found": [
          {
            "group": "404 Not Found",
            "field": "InvalidCID",
            "optional": false,
            "description": "<p>No request with CID found</p>"
          }
        ],
        "202 Processing": [
          {
            "group": "202 Processing",
            "field": "InProcess",
            "optional": false,
            "description": "<p>Request CID is still being processed</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Error-Response:",
          "content": "Error-Response:\n      HTTP/1.1 404 Not Found\n      {\n          'error': 'InvalidCID'\n      }\n       HTTP/1.1 202 Processing\n      {\n          'error': 'InProcess'\n      }\n",
          "type": "json"
        }
      ]
    },
    "filename": "./Predict_Category/esb/esb_service.py"
  },
  {
    "type": "POST",
    "url": "/category/predict",
    "title": "Request to get categories for a product",
    "version": "0.1.0",
    "name": "RequestProductCategory",
    "group": "Category",
    "description": "<p>This API allows a user to get the category and sub-category of a product based on the product name.</p>",
    "header": {
      "fields": {
        "Header": [
          {
            "group": "Header",
            "type": "String",
            "field": "Authorization",
            "optional": false,
            "description": "<p>Authorization Credentials</p>"
          },
          {
            "group": "Header",
            "type": "String",
            "field": "content-type",
            "optional": false,
            "description": "<p>application/json</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Object[]",
            "field": "products",
            "optional": false,
            "description": "<p>List of product objects</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "products.product_name",
            "optional": false,
            "description": "<p>Product Name String</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "field": "products.extra",
            "optional": true,
            "description": "<p>Additional identifiers [wbn etc]</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "String",
            "field": "cid",
            "optional": false,
            "description": "<p>Unique identifier for the request</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success-Response:",
          "content": "Success-Response:\n      HTTP/1.1 200 OK\n      {\n          'cid': 'K001006186845405187400962847840262893088'\n      }\n",
          "type": "json"
        }
      ]
    },
    "examples": [
      {
        "title": "Example Usage:",
        "content": "Example Usage:\n      import json, requests\n      payload = [{\n          \"product_name\":\"Samsung Galaxy s3 i9300\"\n          }, {\n          \"product_name\":\"Red SkullCandy Earphones\"\n          }, {\n          \"product_name\":\"Toshiba z4-a Ultrabook Laptop\",\n          'wbn':'1231212'\n          }]\n       headers = {'Content-type': 'application/json'}\n       url = 'http://api.delhivery.io/category/predict'\n       r = requests.post(url, data=json.dumps(payload), headers=headers)\n",
        "type": "json"
      }
    ],
    "error": {
      "fields": {
        "400 Bad Request": [
          {
            "group": "400 Bad Request",
            "field": "MissingProduct",
            "optional": false,
            "description": "<p>Product Name either missing or None</p>"
          },
          {
            "group": "400 Bad Request",
            "field": "MissingProductList",
            "optional": false,
            "description": "<p>Product List either missing or None</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Error-Response:",
          "content": "Error-Response:\n      HTTP/1.1 400 Bad Request\n      {[\n          'error': 'MissingProductList'\n      ]}\n       HTTP/1.1 400 Bad Request\n      {[\n          'error': 'MissingProduct',\n          'product_name': ''\n      }]\n",
          "type": "json"
        }
      ]
    },
    "filename": "./Predict_Category/esb/esb_service.py"
  }
] });