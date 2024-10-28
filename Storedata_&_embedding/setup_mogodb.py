import os
import pandas as pd
from pymongo import MongoClient
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModel
import torch
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

client = MongoClient("mongodb://localhost:27017/")
db = client["recommender_db"]
collection = db["products"]

dataset = load_dataset("pgurazada1/amazon_india_products")

df = pd.DataFrame(dataset['train']) 
collection.insert_many(df.to_dict(orient="records"))
print("Data successfully uploaded to MongoDB.")