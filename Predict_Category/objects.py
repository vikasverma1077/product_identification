import sys
import csv
from sklearn.externals import joblib
from constants import PARENT_DIR_PATH
from config_details import second_level_cat_names, second_level_cat_names_nb, second_level_cat_names_rf

sys.path.append(PARENT_DIR_PATH)

class categoryModel(object):
    def __init__(self):
        self.second_level_cat_names_set = set(second_level_cat_names)
        self.second_level_cat_names_set_nb = set(second_level_cat_names_nb)
        self.second_level_cat_names_set_rf = set(second_level_cat_names_rf)
        self.vectorizer = joblib.load(PARENT_DIR_PATH + '/Models/vectorizer.pkl')
        self.clf_bayes = joblib.load(PARENT_DIR_PATH + '/Models/clf_bayes.pkl')
        self.clf_chi = joblib.load(PARENT_DIR_PATH + '/Models/clf_chi.pkl')
        self.clf_rf = joblib.load(PARENT_DIR_PATH + '/Models/clf_l1_rf.pkl')

        self.second_level_vectorizer = {}
        self.second_level_clf_bayes = {}
        self.second_level_clf_fpr = {}
        self.second_level_clf_rf = {}
        for cat_name in self.second_level_cat_names_set:
            self.second_level_vectorizer[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                            '/Models/SubModels/Vectorizer_' + cat_name)
            self.second_level_clf_bayes[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                        '/Models/SubModels/clf_bayes_' + cat_name)
            if cat_name in self.second_level_cat_names_set_nb:
                self.second_level_clf_fpr[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                        '/Models/SubModels/clf_fpr_' + cat_name)
            elif cat_name in self.second_level_cat_names_set_rf:
                self.second_level_clf_rf[cat_name] = joblib.load(PARENT_DIR_PATH +
                                                        '/Models/SubModels/clf_rf_' + cat_name)
class dangerousModel(object):
    def __init__(self):
        file_dg_csv = open(PARENT_DIR_PATH + "/DG_keywords.csv")
        reader = csv.reader(file_dg_csv)
        # Skip keys
        reader.next()
        self.dg_keywords = []
        for row in reader:
            tmp = []
            tmp.append(row[0].lower()) #store dangerous/ Non dangerous
            tmp.append(row[1].lower()) #store keyword
            tmp.append(row[2].lower()) #store CONTAIN list
            tmp.append(row[3].lower()) #store CONTAIN category
            tmp.append(row[4].lower()) #store EXCEPT list
            tmp.append(row[5].lower()) #store EXCEPT category
            tup = tuple(tmp)
            self.dg_keywords.append(tup)
        file_dg_csv.close()

