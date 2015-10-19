__author__ = 'rohan'

import sys
import os.path

PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname('__file__')))
print PARENT_DIR
sys.path.append(PARENT_DIR)

import re
from removeColor import removeColor
from Load_Data.get_products import get_categories, get_delhivery_products, get_vendor_category_products, get_delhivery_vendor_products
from config_details import second_level_cat_names, second_level_cat_names_nb, second_level_cat_names_rf

import csv
import json
import numpy as np
from pymongo import MongoClient

from sklearn import feature_extraction
from sklearn import naive_bayes
from sklearn import metrics
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_selection import SelectPercentile, chi2, f_classif, SelectFpr
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib


plural_dict = {}
with open('Train_Model/word_list_verified.csv','rb') as f:
    reader = csv.reader(f)
    for row in reader:
        type(row[2])
        if row[2]!='0':
            plural_dict[row[0]] = row[1]

client = MongoClient()
db = client['cat_identification']
product_table = db['products_new']

def mypluralremover(word):
    """

    :param word:  the word to remove plural from
    :return: the singular verson of the word
    """
    # if word == "men's" or word == "men":
    #     return "man"
    # elif word == "women's" or word == "women":
    #     return "woman"
    # elif word.endswith == "'s":
    #     return word[:-2]
    # elif word.endswith('ies') and len(word) >= 5:
    #     return word[:-3] + "y"
    # elif word.endswith('ves') and len(word) >= 5:
    #     return word[:-3] + "f"
    # elif (word.endswith('ches') or word.endswith('sses') or word.endswith('shes') or word.endswith('xes')) and len(word) >=5:
    #     return word[:-2]
    # elif word.endswith('ss'):
    #     return word
    # elif word.endswith('s') and len(word) >= 4:
    #     return word[:-1]
    # else:
    #     return word
    # if word.endswith('ves'):
    #     return word[:-1]
    # else:
    #     return singularize(word)
    if word.endswith('s') or word.endswith('S'):
        if word in plural_dict:
            return plural_dict[word]
        else:
            return word
    else:
        return word


def ngrams(desc, MIN_N=2, MAX_N=5):
    """
    :param desc: word to find ngrams from
    :param MIN_N: the minimum n gram
    :param MAX_N: the maximum n gram
    :return: list of all ngrams
    """

    ngram_list = []
    # desc = remove_text_inside_brackets(desc)
    desc = removeColor(desc)
    tokens = re.findall(r"[\w'-]+", desc)
    tokens = [mypluralremover(x) for x in tokens]
    try:
        if tokens != []:
            if len(tokens) < 2:
                ngram_list.append(" ".join(tokens))
            else:
                n_tokens = len(tokens)
                for i in xrange(n_tokens):
                    for j in xrange(i + MIN_N, min(n_tokens, i + MAX_N) + 1):
                        ngram_list.append(" ".join(tokens[i:j]))
    except:
        print desc
    return ngram_list


def remove_text_inside_brackets(text, brackets="()[]"):
    #TODO Optimize this function

    """

    :param text:
    :param brackets:
    :return:
    """
    count = [0] * (len(brackets) // 2)  # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b:  # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1) ** is_close  # `+1`: open, `-1`: close
                if count[kind] < 0:  # unbalanced bracket
                    count[kind] = 0
                break
        else:  # character is not a bracket
            if not any(count):  # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)



def get_products(cat_id, count):

    return get_delhivery_products(cat_id,count)


def root_training_prcoess():
    count=1000
    category_tree=json.loads(get_categories())
    category_list=category_tree.keys()
    product_list=[]
    category_count_dict={}
    second_level_categories=set()
    train_x=[]
    train_y=[]
    # # print category_list
    # # import pdb;pdb.set_trace()
    ## For vendor based model
    """
    total=0
    for category_id in category_list:
        current_prod_list=json.loads(get_products(category_id,count=count))
        print category_id
        total=total+ len(current_prod_list)
        print total
        # print current_prod_list
        current_prod_count=len(current_prod_list)
        category_count_dict[category_id]=current_prod_count
        # print category_count_dict
        current_category_name="Delhivery_Others"
        if current_prod_count>=800:
            current_category_name=category_id
            second_level_categories.add(category_id)
        for products in current_prod_list:
            # print products
            train_x.append(products.get('product_name',"").encode('ascii','ignore').lower())
            train_y.append(current_category_name)
            product_list.append((products,current_category_name))
    """
    hq = product_table.find({"vendor_id":"HQ"})
    print "----------------"
    print "root training"
    print hq.count()
    for products in hq:
        train_x.append(products['product_name'].encode('ascii','ignore').lower())
        if products['vendor_category_id'] == 'NA':
            current_category_name = 'Delhivery_Others'
        else:
            current_category_name =  products['vendor_category_id'].split('->')[0]
        train_y.append(current_category_name)
        product_list.append((products,current_category_name))




    print "Training Set Constructed"
    print "Training Set Stats"
    print category_count_dict
    print len(train_x), len(train_y)
    # train_x_tokenized=[]

    # for records in train_x:
    #     tokens=ngrams(records.lower(),1,3)
    #     if tokens:
    #         train_x_tokenized.append(tokens)
    #     else:
    # #         print records
    #         train_x_tokenized.append([""])
    # print "Tokenized Training Set"

    vocabulary=set()
    print "Constructing Vocab"
    for i,records in enumerate(train_x):
        print i
        try:
            for word in ngrams(records.lower(),1,3):
                if not re.match('^[0-9]+$',word):
                    vocabulary.add(word.lower())
        except:
            print records
            continue
    print "Vocab Done"

    vectorizer=feature_extraction.text.CountVectorizer(vocabulary=set(vocabulary),ngram_range=(1,3),stop_words='english')
    train_x_vectorized=vectorizer.transform(train_x)

    clf_bayes=naive_bayes.MultinomialNB(fit_prior=False)
    clf_bayes.fit(train_x_vectorized,train_y)

    print "model 1 done"

    clf_chi = Pipeline([
        ('feature_selection',SelectPercentile(chi2,20)),
  ('classification', naive_bayes.MultinomialNB(fit_prior=False))])
    clf_chi.fit(train_x_vectorized, train_y)

    print "model 2 done"
    
    clf_rf = Pipeline([
        ('feature_selection', LinearSVC(C=2, penalty="l1", dual=False)),
  ('classification', RandomForestClassifier(n_estimators=100, max_depth=1000))])
    clf_rf.fit(train_x_vectorized, train_y)
   
    print "model 3 done"
    
    print os.path.dirname(os.path.realpath('__file__'))+'/../Models/clf_bayes.pkl'
    joblib.dump(clf_bayes, os.path.dirname(os.path.realpath('__file__'))+'/Models/clf_bayes.pkl')
    joblib.dump(clf_chi, os.path.dirname(os.path.realpath('__file__'))+'/Models/clf_chi.pkl')
    joblib.dump(clf_rf, os.path.dirname(os.path.realpath('__file__'))+'/Models/clf_l1_rf.pkl')
    joblib.dump(vectorizer,os.path.dirname(os.path.realpath('__file__'))+'/Models/vectorizer.pkl')
  


    # joblib.dump(second_level_cats,'../Models')




def second_training_process():
    count=10000
    category_tree=json.loads(get_categories())
    for parent_category in second_level_cat_names:
        train_x=[]
        train_y=[]
        total=0
        category_count_dict={}
        for category_id in category_tree[parent_category].keys():
            ## For vendor based model
            """
            print get_products(category_id,count)
            current_prod_list=json.loads(get_products(category_id,count=count))
            print category_id
            total=total+ len(current_prod_list)
            print total
            # print current_prod_list
            current_prod_count=len(current_prod_list)
            category_count_dict[category_id]=current_prod_count
            # print category_count_dict
            current_category_name="Delhivery_Others"
            if current_prod_count>=500:
                current_category_name=category_id
            for products in current_prod_list:
                # print products
                train_x.append(products.get('product_name',"").encode('ascii','ignore').lower())
                train_y.append(current_category_name)
            """
            try:
                hq = product_table.find({"vendor_id":"HQ","vendor_category_id":category_id})
                print "---------------------"
                print category_id,hq.count()
                print "---------------------"
                for products in hq:
                    train_x.append(products['product_name'].encode('ascii','ignore').lower())
                    current_category_name =  category_id
                    train_y.append(current_category_name)
                    # product_list.append((products,current_category_name))
            except:
                pass
        print "Training Set Constructed for %s "%(parent_category)
        print "Training Set Stats"
        print len(train_x), len(train_y)
        vocabulary=set()
        print "Constructing Vocab"
        for i,records in enumerate(train_x):
            print i
            # print records
            try:
                for word in ngrams(records.lower(),1,3):
                    if not re.match('^[0-9]+$',word):
                        vocabulary.add(word.lower())
            except:
                print records
                continue
        print "Vocab Done"

        vectorizer=feature_extraction.text.CountVectorizer(vocabulary=set(vocabulary),ngram_range=(1,3),stop_words='english')
        train_x_vectorized=vectorizer.transform(train_x)

        clf_bayes=naive_bayes.MultinomialNB(fit_prior=False)
        clf_bayes.fit(train_x_vectorized,train_y)

        joblib.dump(vectorizer,PARENT_DIR+"/Models/SubModels/Vectorizer_"+parent_category)
        joblib.dump(clf_bayes,PARENT_DIR+"/Models/SubModels/clf_bayes_"+parent_category)
        
        if parent_category in second_level_cat_names_nb:
            clf_fpr = Pipeline([
            ('feature_selection',SelectFpr(f_classif,0.05)),
            ('classification', naive_bayes.MultinomialNB(fit_prior=False))])
            clf_fpr.fit(train_x_vectorized, train_y)
            
            joblib.dump(clf_fpr,PARENT_DIR+"/Models/SubModels/clf_fpr_"+parent_category)
            
        elif parent_category in second_level_cat_names_rf:
            clf_rf = Pipeline([
            ('feature_selection', LinearSVC(C=2, penalty="l1", dual=False)),
            ('classification', RandomForestClassifier(n_estimators=100, max_depth=5000))])
            clf_rf.fit(train_x_vectorized, train_y)
            
            joblib.dump(clf_rf,PARENT_DIR+"/Models/SubModels/clf_rf_"+parent_category)

        






if __name__=='__main__':
    root_training_prcoess()
    second_training_process()
    # categories=json.loads(get_categories())
    # for cat in categories:
    #     print cat
    #     for subcats in categories[cat]:
    #         print '\t'+subcats



