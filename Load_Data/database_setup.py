from pymongo import MongoClient, ASCENDING
import os.path
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
# print sys.path
from config_details import database, vendor_table, product_table, vendor_category_table, delhivery_category_table, \
    vendor_delhivery_mapping
# from category_dict import category_counts
import json
from collections import deque
from pymongo.errors import BulkWriteError
from get_products import get_categories

client = MongoClient()
db = client[database]

vendor_cat_table = db[vendor_category_table]
vendor_category_mapping_table = db[vendor_delhivery_mapping]

delhiveryCategories = {0: {'category': 'Software and E-learning'},
                       5: {'category': 'Musical Instruments'},
                       10: {'category': 'Books'},
                       15: {'category': 'Industrial and Scientific Goods'},
                       20: {'category': 'Computers and Laptops'},
                       25: {'category': 'Shoes and Footwear'},
                       30: {'category': 'Movies, Music and Video Games'},
                       35: {'category': 'Home and Kitchen'},
                       40: {'category': 'Grocery and Gourmet Food'},
                       45: {'category': 'Mobile Phone, Tablets and Accesories'},
                       50: {'category': 'Toys and Games'},
                       55: {'category': 'Health and Wellness'},
                       60: {'category': 'Electronics and Appliances'},
                       65: {'category': 'Handbags, Bags and Luggage'},
                       70: {'category': 'Sports and Outdoors'},
                       75: {'category': 'Apparel & Accessories'},
                       80: {'category': 'Tools and Hardware'},
                       85: {'category': 'Automotive'},
                       90: {'category': 'Watches, Eyewear and Jewellery'},
                       95: {'category': 'Beauty Products and Personal Care'},
                       100: {'category': 'Camera and Photos'},
                       105: {'category': 'Pet Supplies'},
                       110: {'category': 'Office Products'},
                       115: {'category': 'Baby Care'},
                       120: {'category': 'Gifts'},
                       125: {'category': 'KitchenWare'},
                       130: {'category': 'Uncategorized'},
                       201: {'category': 'Computers and Laptops',
                             'sub_category': 'Routers and Modems'},
                       202: {'category': 'Computers and Laptops', 'sub_category': 'Laptop'},
                       203: {'category': 'Computers and Laptops',
                             'sub_category': 'Computer Components'},
                       204: {'category': 'Computers and Laptops',
                             'sub_category': 'Computer Accessories'},
                       205: {'category': 'Computers and Laptops', 'sub_category': 'Desktops'},
                       206: {'category': 'Computers and Laptops',
                             'sub_category': 'Pen Drives and Data Card'},
                       207: {'category': 'Computers and Laptops',
                             'sub_category': 'External Hard Drives'},
                       208: {'category': 'Computers and Laptops', 'sub_category': 'Monitor'},
                       209: {'category': 'Computers and Laptops', 'sub_category': 'Speakers'},
                       210: {'category': 'Computers and Laptops',
                             'sub_category': 'Headphones & Mic'},
                       211: {'category': 'Computers and Laptops',
                             'sub_category': 'Printers and Scanners'},
                       251: {'category': 'Shoes and Footwear', 'sub_category': "Kids' Footwear"},
                       252: {'category': 'Shoes and Footwear', 'sub_category': "Women's Footwear"},
                       253: {'category': 'Shoes and Footwear', 'sub_category': "Men's Footwear"},
                       351: {'category': 'Home and Kitchen', 'sub_category': 'Furniture'},
                       352: {'category': 'Home and Kitchen', 'sub_category': 'Kitchenware'},
                       353: {'category': 'Home and Kitchen', 'sub_category': 'Home Decor'},
                       354: {'category': 'Home and Kitchen', 'sub_category': 'Home Furnishing'},
                       401: {'category': 'Grocery and Gourmet Food',
                             'sub_category': 'Frozen Food Items'},
                       451: {'category': 'Mobile Phone, Tablets and Accesories',
                             'sub_category': 'Powerbanks'},
                       452: {'category': 'Mobile Phone, Tablets and Accesories',
                             'sub_category': 'Tablets'},
                       453: {'category': 'Mobile Phone, Tablets and Accesories',
                             'sub_category': 'Mobiles'},
                       454: {'category': 'Mobile Phone, Tablets and Accesories',
                             'sub_category': 'Case, Cover and Screenguards'},
                       455: {'category': 'Mobile Phone, Tablets and Accesories',
                             'sub_category': 'Mobile Accessories'},
                       456: {'category': 'Mobile Phone, Tablets and Accesories',
                             'sub_category': 'Digital Goods'},
                       551: {'category': 'Health and Wellness', 'sub_category': 'Pharmacy Products'},
                       552: {'category': 'Health and Wellness',
                             'sub_category': 'E-Ciggarettes and E-Sheesha'},
                       553: {'category': 'Health and Wellness',
                             'sub_category': 'Massage and Pain Relief'},
                       554: {'category': 'Health and Wellness',
                             'sub_category': 'Hospital and Medical Equipment'},
                       555: {'category': 'Health and Wellness', 'sub_category': 'Diabetic Care'},
                       556: {'category': 'Health and Wellness', 'sub_category': 'Sexual Wellness'},
                       557: {'category': 'Health and Wellness',
                             'sub_category': 'Protein and Health Supplements'},
                       558: {'category': 'Health and Wellness',
                             'sub_category': 'Bp and Heart Rate Monitors'},
                       559: {'category': 'Health and Wellness', 'sub_category': 'Health Devices'},
                       560: {'category': 'Health and Wellness', 'sub_category': 'Homeopathy'},
                       561: {'category': 'Health and Wellness',
                             'sub_category': 'Woman Care and Motherhood'},
                       601: {'category': 'Electronics and Appliances', 'sub_category': 'Projectors'},
                       602: {'category': 'Electronics and Appliances',
                             'sub_category': 'Portable Audio Players'},
                       603: {'category': 'Electronics and Appliances',
                             'sub_category': 'Headphones and Earphones'},
                       604: {'category': 'Electronics and Appliances',
                             'sub_category': 'Home Appliances'},
                       605: {'category': 'Electronics and Appliances', 'sub_category': 'TV'},
                       606: {'category': 'Electronics and Appliances', 'sub_category': 'Speakers'},
                       607: {'category': 'Electronics and Appliances',
                             'sub_category': 'Audio and Video Accessories'},
                       608: {'category': 'Electronics and Appliances',
                             'sub_category': 'Washing Machine'},
                       701: {'category': 'Sports and Outdoors', 'sub_category': 'Sports Clothing'},
                       702: {'category': 'Sports and Outdoors', 'sub_category': 'Outdoor Gear'},
                       703: {'category': 'Sports and Outdoors', 'sub_category': 'Sports Equipment'},
                       704: {'category': 'Sports and Outdoors',
                             'sub_category': 'Exercise and Fitness'},
                       751: {'category': 'Apparel & Accessories',
                             'sub_category': "Women's Clothing"},
                       752: {'category': 'Apparel & Accessories', 'sub_category': "Men's Clothing"},
                       801: {'category': 'Tools and Hardware',
                             'sub_category': 'Bathroom Fittings and Accesories'},
                       802: {'category': 'Tools and Hardware', 'sub_category': 'Other Tools'},
                       803: {'category': 'Tools and Hardware',
                             'sub_category': 'Paint and Paint Tools'},
                       851: {'category': 'Automotive', 'sub_category': 'Bike Accessories'},
                       852: {'category': 'Automotive', 'sub_category': 'Automobiles'},
                       853: {'category': 'Automotive', 'sub_category': 'Tyres and Spares'},
                       854: {'category': 'Automotive', 'sub_category': 'Car Audio and GPS'},
                       855: {'category': 'Automotive', 'sub_category': 'Car Accesories'},
                       901: {'category': 'Watches, Eyewear and Jewellery',
                             'sub_category': 'Watches'},
                       902: {'category': 'Watches, Eyewear and Jewellery',
                             'sub_category': 'Jewellery'},
                       903: {'category': 'Watches, Eyewear and Jewellery',
                             'sub_category': 'Eyewear'},
                       951: {'category': 'Beauty Products and Personal Care',
                             'sub_category': 'Bath'},
                       952: {'category': 'Beauty Products and Personal Care',
                             'sub_category': 'Hair Care'},
                       953: {'category': 'Beauty Products and Personal Care',
                             'sub_category': 'Deodrants and Fragrances'},
                       954: {'category': 'Beauty Products and Personal Care',
                             'sub_category': 'Women Hygiene'},
                       955: {'category': 'Beauty Products and Personal Care',
                             'sub_category': 'Shaving and Grooming'},
                       956: {'category': 'Beauty Products and Personal Care',
                             'sub_category': 'Oral Care'},
                       957: {'category': 'Beauty Products and Personal Care',
                             'sub_category': 'Skin Care'},
                       958: {'category': 'Beauty Products and Personal Care',
                             'sub_category': 'Everyday Makeup'},
                       1001: {'category': 'Camera and Photos', 'sub_category': 'Camera Lens'},
                       1002: {'category': 'Camera and Photos', 'sub_category': 'Digital Camera'},
                       1003: {'category': 'Camera and Photos',
                              'sub_category': ' Binoculars and Telescopes'},
                       1004: {'category': 'Camera and Photos', 'sub_category': 'Camcoders'},
                       1005: {'category': 'Camera and Photos',
                              'sub_category': 'Digital Photo Frames'},
                       1006: {'category': 'Camera and Photos', 'sub_category': 'DSLR'},
                       1007: {'category': 'Camera and Photos', 'sub_category': 'Memory Cards'},
                       1008: {'category': 'Camera and Photos', 'sub_category': 'Camera Accesories'},
                       1101: {'category': 'Office Products', 'sub_category': 'Desk Accesories'},
                       1102: {'category': 'Office Products', 'sub_category': 'Office Stationary'},
                       1103: {'category': 'Office Products',
                              'sub_category': 'Ink Cartridges and Toners'}
}

category_list = []


def hierarchy(d):
    for key, value in d.iteritems():
        # print key
        if key != 'count':
            # print key
            category_list.append((key, value.get('count',0)))
            hierarchy(value)


def insert_vendor_category(vendor_detail):
    # vendor_cat_id | vendor_id | parent_vendor_cat_id | leaf_product_id_list
    # vendor_category_table  = db[vendor_category_table]
    vendorTable = db[vendor_table]
    # 1 for Amazon
    vendor_name = vendor_detail
    vendor_id = vendorTable.find({"_id": vendor_name})[0]['_id']
    # vendor_cat_id = 0
    with open('/home/delhivery/Documents/workspace/cataloguing/main/Load_Data/snapdeal.json') as data_file:
        category_counts = json.load(data_file)
    hierarchy(category_counts)
    # print len(set(category_list))
    # print len(category_list)
    for categories in category_list:
        # a.append(categories[0])
        c = categories[0].rsplit('->', 1)
        parent = c[0]
        # parent  = "-1"
        if len(c) > 1:
            current = c[1]
        else:
            current = c[0]
            parent = "-1"
        if parent != "-1":
            vendor_cat_table.insert({"vendor_id": vendor_id, "_id": vendor_name + '_' + categories[0],
                                     'parent_vendor_cat_id': vendor_name + '_' + parent})
        else:
            vendor_cat_table.insert(
                {"vendor_id": vendor_id, "_id": vendor_name + '_' + categories[0], 'parent_vendor_cat_id': parent})


def getParent(categoryName):
    """
    Input: Category Name (String)
    Return parent of the category from delhiveryCategories declared above.
    """
    for key, value in delhiveryCategories.iteritems():
        if delhiveryCategories[key]['category'] == categoryName and 'sub_category' not in delhiveryCategories[key]:
            return key


def create_delhivery_table():
    # delhivery_cat_id | delhivery_cat_name | parent_delhivery_cat_id
    catTable = db[delhivery_category_table]
    category_table = {}
    for key, value in delhiveryCategories.iteritems():
        if 'sub_category' in delhiveryCategories[key]:
            new_category = delhiveryCategories[key]['category'] + '->' + delhiveryCategories[key]['sub_category']
            category_table[delhiveryCategories[key]['sub_category']] = {"_id": new_category, "parent_delhivery_cat_id":
                delhiveryCategories[key]['category']}
        else:
            category_table[delhiveryCategories[key]['category']] = {"_id": delhiveryCategories[key]['category'],
                                                                    "parent_delhivery_cat_id": "-1"}

    bulk = catTable.initialize_ordered_bulk_op()
    for key, items in category_table.iteritems():
        # print(items)
        bulk.insert(items)
    try:
        bulk.execute()
    except BulkWriteError as bwe:
        print bwe.details()

    # print(category_table)


def mapper(v_cat_id, d_id, map_child):
    # vendor_category_table = db[vendor_category_table]
    vendor_categories = vendor_cat_table.find_one(
        {
        '_id': v_cat_id
        }
    )


    print vendor_categories  # print(vendor_categories)
    stack = []
    descendants = []
    descendants.append(vendor_categories['_id'])
    stack.append(vendor_categories)
    if map_child:
        while (len(stack) > 0):
            currentnode = stack.pop()
            # print('currentnode is',currentnode)
            children = vendor_cat_table.find(
                {
                'parent_vendor_cat_id': currentnode['_id']
                }
            )
            # print('children are',children)
            for child in children:
                # print('child is',child)
                descendants.append(child['_id'])
                stack.append(child)

    print(descendants)
    check_vendor_cat_list_exists = vendor_category_mapping_table.find(
        {
        "$and":
            [
                {"vendor_cat_id_list":
                     {"$exists": True}
                },
                {"vendor_id":v_cat_id.split('_')[0]
                },
                {"delhivery_cat_id": d_id}
            ]
        }
    )
    if check_vendor_cat_list_exists.count() == 0:
        # print('does not exists')
        vendor_category_mapping_table.update(
            {'vendor_id': v_cat_id.split('_')[0], 'delhivery_cat_id': d_id},
            {
            "$set":
                {"vendor_cat_id_list": descendants}
            },
            upsert=True
        )
    else:
        vendor_category_mapping_table.update(
            {'vendor_id': v_cat_id.split('_')[0], 'delhivery_cat_id': d_id},
            {
            "$addToSet":
                {
                'vendor_cat_id_list':
                    {
                    "$each": descendants
                    }
                }
            }
        )

    # return descendants,d_id


def unmapped(level, vendor=None):
    queue = deque([])
    marker = "False"
    current_level = 1
    unmapped = deque([])
    if not vendor:

        root = vendor_cat_table.find(
            {
                "parent_vendor_cat_id": "-1",

            }
        )
    else:
        root = vendor_cat_table.find(
            {
                "parent_vendor_cat_id": "-1",
                "vendor_id": vendor
            }
        )
    # print(root)
    for category in root:
        queue.append(category)
        # unmapped.append(category['_id'])
    # queue.append(root)
    queue.append(marker)

    while len(queue) > 0:
        current_node = queue.popleft()
        # unmapped.popleft()

        # print(current_node)
        if current_node == "False":
            current_level += 1

            if len(queue) == 0:
                break

            queue.append(marker)
            continue

        if level == current_level:
            level_node = vendor_category_mapping_table.find(
                {
                    'vendor_cat_id_list': current_node['_id']
                }
            );
            if level_node.count() == 0:
                unmapped.append(current_node['_id'])
                # print(current_node)

        try:
            categories = vendor_cat_table.find(
                {
                    'parent_vendor_cat_id': current_node['_id']
                }
            )
            for category in categories:
                # print category
                queue.append(category)
        except:
            pass

    return list(unmapped)


def updateSequenceProdTable():
    """
    Input: Product Table Name (String)
    Process: Update product table to include a new field "seq" to have
    sequence number in eah category. 
    """
    products = db[product_table]
    # categories = products.distinct("vendor_category_id")
    categories = vendor_cat_table.find()
    count = 1

    for category in categories:
        bulk = products.initialize_ordered_bulk_op()
        # print(category)
        if 'leaf_product_id_list' in category:
            print category['_id'], count
            for index, product in enumerate(category['leaf_product_id_list']):
                # print product,index,index+1
                bulk.find({"_id": product}).update({"$set": {"seq": index + 1}})
            count += 1

            try:
                bulk.execute()
            except BulkWriteError as bwe:
                print bwe.details()


def update_product_list():
    count = 0
    productTable = db[product_table]
    product_categories = productTable.find()
    bulk = vendor_cat_table.initialize_unordered_bulk_op()
    vendor_category = {}
    for product_category in product_categories:
        # print product_category['vendor_category_id'], product_category['_id']
        if product_category['vendor_category_id'] not in vendor_category:
            vendor_category[product_category['vendor_category_id']] = []

        vendor_category[product_category['vendor_category_id']].append(product_category['_id'])

    for key, value in vendor_category.iteritems():
        bulk.find({"_id": key}).update({"$set": {"leaf_product_id_list": value}})

    try:
        bulk.execute()
    except BulkWriteError as bwe:
        print bwe.details()



    # def main():
    # print("Database")
    #   unmapped(1)
    # insert_vendor_category()
    # create_delhivery_table()
    # update_product_list()
    # updateSequenceProdTable()
    # mapper('Amazon_Jewellery->Accessories->Boxes & Organisers','Watches, Eyewear and Jewellery->Jewellery',True)


# if __name__ == '__main__':
    # import csv
    # unmapped_cats = unmapped(2, 'Amazon')
    # with open('../unmapped_amazon.csv','w') as f:
    #     writer=csv.writer(f)
    #     for cat in unmapped_cats:
    #         try:
    #             writer.writerow([repr(cat)])
    #         except:
    #             print cat.encode('ascii','ignore')
    # # delhivery_categories= json.loads(get_categories())
    # # with open('../delhivery_cats.csv','w') as f2:
    # #     writer=csv.writer(f2)
    # #     for delhivery_cat_id in delhivery_categories:
    # #         writer.writerow([delhivery_cat_id])
    # #         for x in delhivery_categories[delhivery_cat_id]:
    # #             writer.writerow([x])
    #
    #
    #
    #
    # print len(unmapped_cats)
    # # print unmapped_cats
    # import ipdb;ipdb.set_trace()
    # mapper("Flipkart_Baby Care", "Baby Care", True)
    # import csv
    # with open('../unmapped_amazon.csv') as f:
    #     print 'here'
    #     reader=csv.reader(f)
    #     for row in reader:
    #
    #         print row[0], row[1]
    #         mapper(eval(row[0]),row[1],True)


