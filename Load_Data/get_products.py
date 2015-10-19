import os.path
import random
import sys
import json
from bson import json_util
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config_details import database, vendor_table, product_table, vendor_category_table, vendor_delhivery_mapping, delhivery_category_table
from pymongo import MongoClient

client = MongoClient()
db = client[database]
productTable = db[product_table]
vendorDelhiveryMappingTable = db[vendor_delhivery_mapping]
vendorTable = db[vendor_table]
delhiveryCategoryTable = db[delhivery_category_table]
vendorCategoryTable = db[vendor_category_table]


def productJSON(categorySet,randomInt):
	"""
		Input: 
			categorySet: List of tuple containing vendor category id and count of products
			randomInt: List of random integers
		Output:
			JSON containing information about products
	"""

	finalList = {}
	for document in randomInt:
		temp = document
		for key,value in categorySet:
			if value >= temp: 
				if key not in finalList:
					finalList[key] = set()
				finalList[key].add(temp)
				break
			else:
				temp = temp - value

	json_results = []
	for key in finalList:
		values = list(finalList[key])
		docs = productTable.find({"vendor_category_id":key,"seq":{"$in":values}})
		for doc in docs:
			json_results.append(doc)
	if json_results:
		return json.dumps(json_results, default=json_util.default, indent = 4)
	else:
		return json.dumps({})


def genRandom(productsAvail,userLimit):

	"""
	Input: Products available for the delhivery category in Database(productsAvail) (int),
		   Number of products requested by user(userLimit) (int)
	Process: Generate random numbers in the range 1 to number of products available 
	for the category. If number requested by user is less/equal to half of available products 
	then generate (userLimit) number of random numbers between 1 to productsAvail. Otherwise 
	generate (productsAvail - userLimit) number of random numbers from same range and reject 
	the numbers generated. 
	Output: List of random numbers
	"""
	if userLimit <= productsAvail/2:
		randomDocuments = random.sample(range(1,productsAvail+1),userLimit)
	else:
		randomList = random.sample(range(1,productsAvail+1),productsAvail - userLimit)
		randomDocuments = [val for val in range(1,productsAvail+1) if val not in randomList]
	return randomDocuments


# Get x random products for a delhivery_id y
def get_delhivery_products(delhivery_id,count_products):
	"""
	Input:
		delhivery_id, count_products: number of products to be fetched
	Output:
		list of (count_products) number of products randomly selected 
		basis the delhivery_id.
	"""

	category_children_list = []
	category_children_list.append(delhivery_id)
	if delhiveryCategoryTable.find({"_id":delhivery_id}).count() > 0:
		category_children = delhiveryCategoryTable.find({"parent_delhivery_cat_id":delhivery_id})
		if category_children.count() > 0:
			category_children_list.extend([child['_id'] for child in category_children])
		
		# print category_children_list
		vendor_category = vendorDelhiveryMappingTable.find({"delhivery_cat_id":{"$in":category_children_list}})

		vendor_category_list = []
		for vc in vendor_category:
			# print vc['_id']
			vendor_category_list.extend(vc["vendor_cat_id_list"])

		# print vendor_category_list

		productCount = 0
		count_vendor_category_products = {}
		for category in vendor_category_list:
			count = productTable.find({"vendor_category_id":category}).count()
			count_vendor_category_products[category] = count
			productCount += count

		count_vendor_products = [(a,count_vendor_category_products[a]) for a in count_vendor_category_products]
		
		# productCount = productTable.find({"vendor_category_id":{"$in":vendor_category_list}}).count()
		if count_products > productCount:
			## Limit exceeded count of products available
			count_products = productCount

		documentList  = genRandom(productCount,count_products)

		return productJSON(count_vendor_products,documentList)
	else:
		print("Delhivery Category ID %s does not exist" % (delhivery_id))
		return json.dumps({})

# Get x random products for a delhivery_id y and vendor_id z
def get_delhivery_vendor_products(delhivery_id,vendor_id, count_products):
	"""
	Input:
		delhivery_id, vendor_id, count_products: number of products to
		be fetched
	Output:
		list of (count_products) number of products randomly selected 
		basis the delhivery_id and vendor_id.
	"""
	category_children_list = []
	category_children_list.append(delhivery_id)
	if delhiveryCategoryTable.find({"_id":delhivery_id}).count() > 0:
		category_children = delhiveryCategoryTable.find({"parent_delhivery_cat_id":delhivery_id})
		if category_children.count() > 0:
			category_children_list.extend([child['_id'] for child in category_children])
		
			# print category_children_list
		vendor_category = vendorDelhiveryMappingTable.find({"vendor_id":vendor_id,"delhivery_cat_id":{"$in":category_children_list}})

		vendor_category_list = []
		for vc in vendor_category:
			# print vc['_id']
			vendor_category_list.extend(vc["vendor_cat_id_list"])

		# print vendor_category_list

		productCount = 0
		count_vendor_category_products = {}
		for category in vendor_category_list:
			count = productTable.find({"vendor_id":vendor_id,"vendor_category_id":category}).count()
			count_vendor_category_products[category] = count
			productCount += count

		count_vendor_products = [(a,count_vendor_category_products[a]) for a in count_vendor_category_products]
		
		# productCount = productTable.find({"vendor_category_id":{"$in":vendor_category_list}}).count()
		if count_products > productCount:
			## Limit exceeded count of products available
			count_products = productCount

		documentList  = genRandom(productCount,count_products)

		return productJSON(count_vendor_products,documentList)
	else:
		print("Either Delhivery Category ID %s does not exist or it does not have any children" % (delhivery_id))
		return json.dumps({})


# Get x random products for a vendor_cat_id y and vendor_id z
def get_vendor_category_products(vendor_id, vendor_cat_id, count_products):
	"""
	Input:
		vendor_id, vendor_cat_id: category id belonging to vendor,
		count_products: number of products to be fetched
	Output:
		list of (count_products) number of products randomly selected
		basis the vendor_id and vendor_cat_id.
	"""	

	stack = []
	count_vendor_category_products = {}
	productCount = 0

	current_vendor_category_ids = vendorCategoryTable.find({"_id":vendor_cat_id})
	if current_vendor_category_ids.count() > 0:
		for category_id in current_vendor_category_ids:
			stack.append(category_id)

			if 'leaf_product_id_list' in category_id:
				productCount += len(category_id['leaf_product_id_list'])

				count_vendor_category_products[category_id['_id']] = len(category_id['leaf_product_id_list'])

	
		while(len(stack) > 0):
			currentnode = stack.pop()
			children = vendorCategoryTable.find(
													{
														'parent_vendor_cat_id':currentnode['_id']
													}
												)

			for child in children:
				# descendants.append(child['_id'])
				if 'leaf_product_id_list' in child:
					count_vendor_category_products[child['_id']] = len(child['leaf_product_id_list'])
					productCount += len(child['leaf_product_id_list'])
				else:
					count_vendor_category_products[child['_id']] = 0
				stack.append(child)

		count_vendor_products = [(a,count_vendor_category_products[a]) for a in count_vendor_category_products]

		if count_products > productCount:
			## Limit exceeded count of products available
			count_products = productCount

		documentList  = genRandom(productCount,count_products)


		return productJSON(count_vendor_products,documentList)
	else:
		print("Category %s does not exist" % (vendor_cat_id))
		return json.dumps({})

# Get x random products for a vendor_id z
def get_vendor_products(vendor_id, count_products):
	"""
	Input:
		vendor_id, count_products: number of products to be fetched
	Output:
		list of (count_products) number of products randomly selected
		basis the vendor_id.
	"""

	stack = []
	count_vendor_category_products = {}
	productCount = 0
	current_vendor_category_ids = vendorCategoryTable.find({"vendor_id":vendor_id})
	if current_vendor_category_ids.count() > 0:
		for category_id in current_vendor_category_ids:
			stack.append(category_id)

			if 'leaf_product_id_list' in category_id:
				productCount += len(category_id['leaf_product_id_list'])

				count_vendor_category_products[category_id['_id']] = len(category_id['leaf_product_id_list'])


		count_vendor_products = [(a,count_vendor_category_products[a]) for a in count_vendor_category_products]

		if count_products > productCount:
			## Limit exceeded count of products available
			count_products = productCount

		documentList  = genRandom(productCount,count_products)


		return productJSON(count_vendor_products,documentList)
	else:
		print("Vendor ID %s does not exists" %(vendor_id))
		return json.dumps({})


def get_categories():
	delhivery_categories_parent = delhiveryCategoryTable.find({"parent_delhivery_cat_id":"-1"})
	delhivery_categories = {}
	# delhivery_categories["-1"] = {}
	for category in delhivery_categories_parent:
		# print category['_id']
		if category['_id'] not in delhivery_categories:
			delhivery_categories[category['_id']] = {}
		for children in delhiveryCategoryTable.find({"parent_delhivery_cat_id":category['_id']}):
			delhivery_categories[category['_id']][children['_id']] = ""

	return json.dumps(delhivery_categories)

if __name__ == '__main__':
# 	get_categories()
	print get_delhivery_products("Baby Care",100)
	# get_delhivery_vendor_products("Watches, Eyewear and Jewellery","Amazon",1)
	# get_vendor_products("Shopclues",20)
	# get_vendor_category_products("Amazon","Accessories",1)