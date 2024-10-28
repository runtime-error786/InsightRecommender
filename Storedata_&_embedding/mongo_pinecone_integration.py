from transformers import AutoTokenizer, AutoModel
import torch
from setup_mogodb import collection
from setup_pinecone import index
from concurrent.futures import ThreadPoolExecutor, as_completed

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def generate_embedding(product):
    """Generate embedding for product details (Name, Description, Tags)."""
    combined_text = f"{product['Product Title']} {product['Product Description']} {product['Brand']} {product['Site Name']} {product['Category']}"
    tokens = tokenizer(combined_text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        embedding = model(**tokens).last_hidden_state.mean(dim=1).squeeze()
    return str(product["Uniq Id"]), embedding.numpy()

def upload_to_pinecone(product_embedding):
    """Upload the embedding to Pinecone."""
    uniq_id, embedding = product_embedding
    index.upsert([(uniq_id, embedding)])

def main():
    futures = []
    
    with ThreadPoolExecutor(max_workers=100) as executor:  
        for product in collection.find():
            futures.append(executor.submit(generate_embedding, product))
        
        for future in as_completed(futures):
            try:
                product_embedding = future.result()
                upload_to_pinecone(product_embedding)
            except Exception as e:
                print(f"Error processing product: {e}")

    print("Embeddings uploaded to Pinecone.")

if __name__ == "__main__":
    main()
