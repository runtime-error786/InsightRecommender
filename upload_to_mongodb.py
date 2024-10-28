import pandas as pd
from pymongo import MongoClient

df = pd.read_excel("./dataset/sample_products_dataset.xlsx")

client = MongoClient("mongodb://localhost:27017/")
db = client["recommender_db"]
collection = db["products"]

collection.insert_many(df.to_dict(orient="records"))
print("Data successfully uploaded to MongoDB.")
