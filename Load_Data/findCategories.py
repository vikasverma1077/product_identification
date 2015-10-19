__author__ = 'delhivery'
import json
import re

def clean_name(s,client=None):
    """
    Function to clean category names client wise
    """
    if len(s) > 300:
        return ""
    if client=='amazon':
        s=s.replace('\t',' ').replace('\r',"")
        s=re.sub(r'\n\s+-\n\s+(?=[\w])','---',s)
    elif client=="snapdeal":
        s=s.replace('\t',' ').replace('\r',"")
        s=re.sub(r'\n\s+-\n\s+(?=[\w])','---',s)
    elif client =="flipkart":
        s=s.replace('\t',' ').replace('\r',"")
        s=re.sub(r'\n\s+-\n\s+(?=[\w])','---',s)
    else:
        pass

    return s



def get_category_tuple(category_name,subcat_name):
    if category_name and subcat_name:
        category_list=category_name.split('---')
        category_list=[x.strip() for x in category_list]
        category_set=set()
        new_category_list=[]
        for x in category_list:
            if x not in category_set:
                category_set.add(x)
                new_category_list.append(x)
        if subcat_name not in category_set:
            new_category_list.extend([subcat_name])
        return new_category_list


def update_category_counts(x,category_list,cat_dict):
    """

    :param x: record
    :param category_list:
    :param cat_dict:
    :return:
    """
    if category_list:
        update_dict=cat_dict
        current_cat=""
        while category_list:
            if not current_cat:
                current_cat=category_list[0]
            else:
                current_cat+='->'+category_list[0]
            present = update_dict.get(current_cat,0)
            if not present:
                update_dict[current_cat]={}
            update_dict = update_dict[current_cat]
            count = update_dict.get('count',0)
            update_dict['count']=count+1
            category_list=category_list[1:]

def validate_record (record):
    keys_to_check=['product_name','product_category','product_sub_category']
    for x in keys_to_check:
        if x not in record:
            return False
    return True

def begin_category_extraction(data, client, category_counts):
    """

    :param data:
    :param client:
    :return:
    """
    """
    Sample Record
    {
	"_id" : ObjectId("554b41f7656e41dc79a5529a"),
	"pageurl" : "http://www.amazon.in/BLOODY-PSYCHO-CONNECTION-Womenss-Legging-Purple/dp/B00U8HTYBG",
	"record" : {
		"uniq_id" : "4652cb55d350af68c3daefea53e7924f",
		"product_name" : "BLOODY PSYCHO CONNECTION Womens's Cotton Legging-Purple",
		"product_url" : "http://www.amazon.in/BLOODY-PSYCHO-CONNECTION-Womenss-Legging-Purple/dp/B00U8HTYBG",
		"product_category" : "Clothing & Accessories\n            -\n                Women",
		"product_sub_category" : "Leggings",
		"upc" : "B00U8HTYBG",
		"brand" : "BLOODY PSYCHO CONNECTION",
		"image" : "http://ecx.images-amazon.com/images/I/61KKIpI%2BliL._UL1500_.jpg",
		"product_specifications" : {
			"product_specification" : [
				{	"key" : "Color",
					"value" : "Cotton"
				},
				{
					"key" : "Leg Style",
					"value" : "Slim"
				}
			]
		}
	}
}
"""
    if 'root' in data:
        data = data['root']['page']

    for x in data:
        # print x
        product_data=x.get('record',{})
        if validate_record(product_data):
            category_name=product_data.get('product_category',None)
            # print repr(category_name)
            category_name=clean_name(category_name,client)
            # print repr(category_name)
            # import pdb;pdb.set_trace()
            subcat_name=product_data.get('product_sub_category',None)
            # print repr(subcat_name)
            subcat_name=clean_name(subcat_name,client)
            # print repr(subcat_name)
            # import pdb;pdb.set_trace()
            category_list=get_category_tuple(category_name,subcat_name)
            update_category_counts(x,category_list,category_counts)
        else:
            pass
    # return category_counts
