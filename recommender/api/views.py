import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient
import redis
from pinecone import Pinecone
from transformers import AutoTokenizer, AutoModel
import torch
from rest_framework.response import Response
from rest_framework.decorators import api_view

load_dotenv()

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["recommender_db"]
mongo_collection = mongo_db["products"]

pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east-1")
index_name = "content-recommender"
index = pinecone_client.Index(index_name)

redis_client = redis.Redis(
    host='redis-13833.c256.us-east-1-2.ec2.redns.redis-cloud.com',
    port=13833,
    password='XjelHVPcSPrv74vX7mIVQsoE8MQfzHe7',
    decode_responses=True  
)

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def generate_embedding(text):
    """Generate embedding for the input text."""
    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        embedding = model(**tokens).last_hidden_state.mean(dim=1).squeeze()
    return embedding.numpy()

def query_pinecone(input_text, top_k=5):
    """Query Pinecone for the most relevant results based on input text."""
    input_embedding = generate_embedding(input_text)
    result = index.query(
        vector=input_embedding.tolist(),
        top_k=top_k,
        include_metadata=True
    )
    return result

def get_products_from_mongodb(product_ids):
    """Retrieve product details from MongoDB."""
    products = mongo_collection.find({"Uniq Id": {"$in": product_ids}})
    print(products)
    return [
        {**product, "_id": str(product["_id"])}  
        for product in products
    ]



def cache_query(query, result):
    """Cache the query result in Redis with a TTL of 1 hour."""
    redis_client.set(query, json.dumps(result), ex=3600)  

def get_cached_result(query):
    """Retrieve cached result from Redis."""
    cached = redis_client.get(query)
    if cached:
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            return None  
    return None  

@api_view(['GET'])
def recommend(request):
    """API endpoint to get product recommendations based on a query."""
    query = request.GET.get("query")
    if not query:
        return Response({"error": "Query parameter is required"}, status=400)

    cached_result = get_cached_result(query)
    if cached_result:
        return Response({"result": cached_result})

    query_result = query_pinecone(query)
    if not query_result.get("matches"):
        return Response({"result": []})  
    print(query_result)
    product_ids = [match["id"] for match in query_result["matches"]]
    print(product_ids)
    matching_products = get_products_from_mongodb(product_ids)

    cache_query(query, matching_products)
    return Response({"result": matching_products})
