from  tinydb import TinyDB, Query
import os
from datetime import datetime

class DataBase:
    def __init__(self,db_file="data.json"):
        dirname=os.path.dirname(db_file)
        if dirname:
            os.makedirs(dirname,exist_ok=True)
        self.db = TinyDB(db_file)
        self.products = self.db.table('products')
    def insert_product(self,product):
        product["date"]=datetime.today().strftime("%Y-%m-%d")
        self.products.insert(product)
    def get_products(self,asin):
        product=Query()
        return self.products.get(product.asin==asin)
    def get_all_products(self):
        return self.products.all()
    def search_criteria(self,criteria):
        product=Query()
        q=None
        for key,value in criteria.items():
            if q == None:
                q=(product[key]==value)
            else:
                q &=(product[key]==value)
        return self.products.search(q) if q else []

