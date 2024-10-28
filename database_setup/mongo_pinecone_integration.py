from transformers import AutoTokenizer, AutoModel
import torch
from setup_mogodb import collection
from setup_pinecone import index

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def generate_embedding(text):
    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        embedding = model(**tokens).last_hidden_state.mean(dim=1).squeeze()
    return embedding.numpy()

for product in collection.find():
    embedding = generate_embedding(product["Description"])
    index.upsert([(str(product["Product_ID"]), embedding)])
    
print("Embeddings uploaded to Pinecone.")
