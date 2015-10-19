import re
from constants import ALPHA_NUM_REGEX, CACHE_EXPIRY, CLEAN_PRODUCT_NAME_REGEX
from settings import r, sentry_client
import json
import numpy as np
import copy
from check_dg import predict_dangerous

def predict_category(product_name, wbn, cat_model, dang_model, logger):
    try:
        l_product_name = product_name.lower()
        product_words = re.findall(CLEAN_PRODUCT_NAME_REGEX, l_product_name)
        clean_product_name = " ".join(product_words)
        
        vectorizer = cat_model.vectorizer
        clf_bayes = cat_model.clf_bayes
        clf_chi = cat_model.clf_chi
        clf_rf = cat_model.clf_rf

        second_level_vectorizer = cat_model.second_level_vectorizer
        second_level_clf_bayes = cat_model.second_level_clf_bayes
        second_level_clf_fpr = cat_model.second_level_clf_fpr
        second_level_clf_rf = cat_model.second_level_clf_rf

        class1 = clf_bayes.predict(vectorizer.transform([l_product_name]))[0]
        class2_prob_vector = clf_chi.predict_proba(vectorizer.transform([l_product_name]))[0]
        class3_prob_vector = clf_rf.predict_proba(vectorizer.transform([l_product_name]))[0]

        if len(np.unique(class2_prob_vector)) == 1:
            class2 = "Delhivery_Others"
        else:
            class2 = clf_bayes.classes_[np.argmax(class2_prob_vector)]
        if len(np.unique(class3_prob_vector)) == 1:
            class3 = "Delhivery_Others"
        else:
            class3 = clf_bayes.classes_[np.argmax(class3_prob_vector)]

        if class3 == "Delhivery_Others":
            if class1 == class2:
                first_level = class1
            elif class1 == "Delhivery_Others":
                first_level = class2
            elif class2 == "Delhivery_Others":
                first_level = class1
            else:
                first_level = class2
        else:
            first_level = class3

        second_level = ""

        if first_level in cat_model.second_level_cat_names_set_nb:
            prob_vector = second_level_clf_fpr[first_level].predict_proba(
                second_level_vectorizer[first_level].transform([l_product_name]))[0]
            if len(np.unique(prob_vector)) == 1:
                second_level = second_level_clf_bayes[first_level].predict(
                    second_level_vectorizer[first_level].transform([l_product_name]))[0]
            else:
                second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]
        
        elif first_level in cat_model.second_level_cat_names_set_rf:
            prob_vector = second_level_clf_rf[first_level].predict_proba(
                second_level_vectorizer[first_level].transform([l_product_name]))[0]
            if len(np.unique(prob_vector)) == 1:
                second_level = second_level_clf_bayes[first_level].predict(
                    second_level_vectorizer[first_level].transform([l_product_name]))[0]
            else:
                second_level = second_level_clf_bayes[first_level].classes_[np.argmax(prob_vector)]
            
            
        dg_report = predict_dangerous(clean_product_name, wbn, first_level,
                                      dang_model.dg_keywords, logger)
        
        result = {}
        result['cat'] = first_level
        result['scat'] = second_level
        result['dg'] = dg_report['dangerous']
        return result

    except Exception as err:
        logger.error(
            'Exception {} occurred against product: {}'.format(
                err, product_name))
        sentry_client.captureException(
            message = "predict.py: Exception occured",
            extra = {"error" : err, "product_name" : product_name})
        
def process_product(product_name_dict, cat_model, dang_model, logger):
    results = {}
    results_cache = ''
    
    product_name = product_name_dict.get('prd', "")
    if product_name:
        final_result = {}
        original_dict = copy.deepcopy(product_name_dict)

        product_name_clean = (re.sub(ALPHA_NUM_REGEX, '', product_name)).lower()
        product_name_key = 'catfight:' +':' + product_name_clean
        results_cache = r.get(product_name_key)
        wbn = product_name_dict.get('wbn', "")
        if not results_cache:
            results = predict_category(product_name.encode('ascii','ignore'),
                                       wbn, cat_model, dang_model, logger)
            if results:
                r.setex(product_name_key, json.dumps(results), CACHE_EXPIRY)
                results['cached'] = False
        else:
            results = json.loads(results_cache)
            l_product_name = product_name.lower()
            product_words = re.findall(CLEAN_PRODUCT_NAME_REGEX, l_product_name)
            clean_product_name = " ".join(product_words)
            first_level = results['cat']
            dg_report = predict_dangerous(clean_product_name, wbn, first_level,
                                      dang_model.dg_keywords, logger)

            results['dg'] = dg_report['dangerous']
            results['cached'] = True
    else:
        results['invalid_product_name'] = True
    
    final_result = original_dict
    final_result['result'] = results
    return final_result

