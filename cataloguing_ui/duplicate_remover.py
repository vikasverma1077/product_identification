'''
- Removes duplicate product names from mongodb.
- Keeps those products which are already tagged or skipped.
  (In case of two or more such products, randomly keeps one of them which is encountered first)
'''

from pymongo import MongoClient

client = MongoClient()
db = client.products_db

dup_list = db.products.aggregate([
						{"$group":{"_id":"$product_name","count":{"$sum":1}}},
						{"$match":{"_id":{"$ne":None},"count":{"$gt":1}}},
						{"$project":{"product_name":"$_id","_id":0}}
						])
'''
This query returns cursor of a list of queries which contains names of all the repeated products.
$group operator aggregates documents by desired index key values.
In this case, it ignores aggregation of those product names which occur only once.
$match operator does the main work and creates dup_list for the product names which occur more than once.
$ne operator checks for the cases for which '_id' doesnot exists
$project operator is just to rename the generated queries as {'product_name':<name>}
'''
print('1', dup_list)
for query in dup_list:
	query_result_cursor = db.products.find(query)
	query_result_list = []
	for item in query_result_cursor:
		query_result_list.append(item)
	flag = 0
	for item in query_result_list:
		if ('tagged_by' in item) or ('verified' in item) or ('skip_count' in item):
			flag = 1
			myitem = item
			break
	if flag == 0:
		myitem = query_result_list[0]
	query_result_list.remove(myitem)
	for item in query_result_list:
		db.products.remove(item)