import os
import sys
import torch
import json
from PIL import Image
from sentence_transformers import SentenceTransformer
from config import get_user_project_path

# Load the CLIP model (both image and text encoders)
model = SentenceTransformer('clip-ViT-B-32', device='cpu')
model.eval()

# We’ll define a chunk size that’s safely under the model’s max token limit
# so we don’t get shape mismatch or indexing errors for large text.
MAX_TOKENS_PER_CHUNK = 65

def get_results_dir(uuid, plan_id):
    """Returns the correct results directory for the given user project."""
    return os.path.join(get_user_project_path(uuid, plan_id), "results")

def embed_image(img_path: str):
    """
    Generates an embedding for a given image using the CLIP model.
    
    :param img_path: Path to the input image file.
    :return: Embedding vector as a list of floats.
    """
    try:
        print(f"Embedding image: {img_path}")
        image = Image.open(img_path).convert('RGB')
        print(f"Image size: {image.size}")
        
        with torch.no_grad():
            embedding_batch = model.encode([image], convert_to_tensor=True)
        embedding = embedding_batch[0].tolist()
        print(f"Generated image embedding length: {len(embedding)}")
        return embedding

    except Exception as e:
        print(f"Error embedding image {img_path}: {e}")
        raise

def embed_text(text: str):
    """
    Generates an embedding for a piece of text using the CLIP text encoder,
    chunking the input if it exceeds MAX_TOKENS_PER_CHUNK.
    
    :param text: The full text to embed (may be very long).
    :return: A single embedding vector (list of floats) representing the entire text.
    """
    try:
        # 1) Naive tokenization: just split on whitespace. 
        #    (CLIP uses subword tokenization internally, but we do this 
        #     to avoid passing huge text in one call.)
        tokens = text.split()

        if len(tokens) <= MAX_TOKENS_PER_CHUNK:
            # Just embed once
            print(f"Embedding text (single chunk): {text[:60]}...")
            with torch.no_grad():
                embedding_batch = model.encode([text], convert_to_tensor=True)
            embedding = embedding_batch[0].tolist()
            print(f"Generated text embedding length: {len(embedding)}")
            return embedding
        else:
            # 2) Multiple chunks
            print(f"Embedding text in multiple chunks (total tokens={len(tokens)})")
            chunk_embeddings = []
            start_idx = 0

            while start_idx < len(tokens):
                end_idx = min(start_idx + MAX_TOKENS_PER_CHUNK, len(tokens))
                chunk_tokens = tokens[start_idx:end_idx]
                chunk_str = " ".join(chunk_tokens)

                with torch.no_grad():
                    embedding_batch = model.encode([chunk_str], convert_to_tensor=True)
                emb_vec = embedding_batch[0]
                chunk_embeddings.append(emb_vec)
                
                start_idx = end_idx

            # 3) Average the chunk embeddings to form a single vector
            #    (Alternatively, you could sum or keep them separate.)
            stacked = torch.stack(chunk_embeddings, dim=0)
            mean_emb = torch.mean(stacked, dim=0)
            final_embedding = mean_emb.tolist()

            print(f"Multi-chunk text => final embedding length: {len(final_embedding)}")
            return final_embedding

    except Exception as e:
        print(f"Error embedding text (len={len(text)}): {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python clip_embedding.py <mode> <input> <uuid> <plan_id>", file=sys.stderr)
        print("  mode can be 'image' or 'text'")
        sys.exit(1)

    mode = sys.argv[1]
    input_item = sys.argv[2]
    uuid = sys.argv[3]
    plan_id = sys.argv[4]

    try:
        if mode.lower() == 'image':
            # `uuid` and `plan_id` must be set correctly before this block
            results_dir = get_results_dir(uuid, plan_id)
            output_path = os.path.join(results_dir, f"{os.path.splitext(os.path.basename(input_item))[0]}_img_emb.json") 
        
            emb = embed_image(input_item)  # Embed the image
        elif mode.lower() == 'text':
            results_dir = get_results_dir(uuid, plan_id)
            output_path = os.path.join(results_dir, "text_embedding.json")

            emb = embed_text(input_item)  # Embed the text
        else:
            raise ValueError("Mode must be 'image' or 'text'")

        # Save embedding
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(emb, f, indent=4)
        print(f"Embedding saved to {output_path}")

    except Exception as e:
        print(f"Error generating embedding: {e}", file=sys.stderr)
        sys.exit(1)