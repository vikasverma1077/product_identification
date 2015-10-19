__author__ = 'rohan'
import csv
import os

def get_color_set():
    x=set()
    f=open(os.path.dirname(__file__)+'/colors.csv')
    reader=csv.reader(f)
    for row in reader:
        x.add(row[0].lower().strip())
    return x

COLOR_SET=get_color_set()
print
