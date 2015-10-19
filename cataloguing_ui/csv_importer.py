'''
Imports the data in HQSUBCAT.csv (located in data folder) into MongoDb
'''

import csv
from pymongo import MongoClient
client = MongoClient()
db = client.products_db

data = []
bulk = db.products.initialize_ordered_bulk_op()
with open('data/outsource_data/hq-data/wbn_prd_3month.csv','rt') as f:
	tempreader = csv.reader(f, delimiter=',')
	next(tempreader, None)
	for row in tempreader:
		if row[2] not in data:
				data.append(row[2])
				bulk.insert({'product_name':row[2], 'vendor':'HQ-Data',
									'category':row[2], 'sub_category': None, 'product_url': None})

bulk.execute()
print(len(data))