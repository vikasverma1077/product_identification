import os
import re

CLEAN_PRODUCT_NAME_REGEX = re.compile('[0-9.]+(?=[a-zA-Z]{1}[0-9]+)|[0-9.]+[a-zA-Z}{1}|[0-9.]+|[a-zA-Z]+')

VOLUME_ML_REGEX = re.compile('[0-9]+[\s]*ml')

# Alpha-num. Remove all punctuation, spaces etc
ALPHA_NUM_REGEX = re.compile('[\W_]+')

# Redis cache expiry 7 days (in sec)
CACHE_EXPIRY = 604800

# logging file path
LOGGING_PATH = '/var/log/cat_subcat_logs/cat_subcat.log'

# GET Parent path
PARENT_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

#CAT Disque Path
CATFIGHT_LOGGING_PATH = '/var/log/cat_subcat_logs/cat_subcat_disque.log'

