__author__ = 'delhivery'


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

second_level_cat_names_nb=\
    ["Beauty Products and Personal Care",
                  "Camera and Photos",
                  "Apparel & Accessories",
                  "Watches, Eyewear and Jewellery",
                  "Electronics and Appliances",
                  "Home and Kitchen",
                  "Computers and Laptops",
                  "Sports and Outdoors",
                  "Health and Wellness",
                  "Shoes and Footwear"
    ]


second_level_cat_names_rf=\
    [ "Mobile Phone, Tablets and Accesories"]


"""
This file includes the database,collection names to be used in the scripts.
"""
database='cat_identification'
vendor_table='vendors'
product_table='products_new'
delhivery_category_table = 'delhivery_categories'
vendor_category_table='vendor_categories'
vendor_delhivery_mapping='vendor_delhivery_mapping'

machine_name='rohan-local'
json_dir_prefix=""
if machine_name=='rohan-local':
    json_dir_prefix="/home/delhivery/pc_data/pc_data"
elif machine_name=='vidya-local':
    json_dir_prefix="/home/delhivery/Documents/workspace/cataloguing/pc_data"


"""
Specify the files/folder to import here
"""
folder_to_import='xyz'
delhivery_category_file=''
vendor_category_file=''

#Load_Settings Folder

#Train_Test_Settings

#Predict_Paths


