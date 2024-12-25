import sys
import json
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer

# Load the CLIP model
model = SentenceTransformer('clip-ViT-B-32')
model.eval()

def embed_image(img_path: str):
    try:
        print(f"Embedding image: {img_path}")
        # Load as PIL
        image = Image.open(img_path).convert('RGB')
        print(f"Image size: {image.size}")
        
        # Let the model handle any resizing / normalization
        with torch.no_grad():
            # Pass a list of PIL images
            embedding_batch = model.encode(
                [image],              # a list with one PIL image
                convert_to_tensor=True
            )
        # embedding_batch is of shape (1, 512) for CLIP
        embedding = embedding_batch[0].tolist()  # convert to python list
        print(f"Generated embedding length: {len(embedding)}")
        return embedding

    except Exception as e:
        print(f"Error embedding image {img_path}: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clip_embedding.py <image_path>", file=sys.stderr)
        sys.exit(1)

    img_path = sys.argv[1]

    try:
        embedding = embed_image(img_path)
        print(json.dumps(embedding))
    except Exception as e:
        print(f"Error generating embedding: {e}", file=sys.stderr)
        sys.exit(1)