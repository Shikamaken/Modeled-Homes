import os
import sys
import torch
import json
from PIL import Image
from sentence_transformers import SentenceTransformer
from config import DATA_INPUT, DATA_OUTPUT

# Load the CLIP model (both image and text encoders)
model = SentenceTransformer('clip-ViT-B-32', device='cpu')
model.eval()

def embed_image(img_path: str):
    """
    Generates an embedding for a given image using the CLIP model.
    
    :param img_path: Path to the input image file.
    :return: Embedding vector as a list (float).
    """
    try:
        print(f"Embedding image: {img_path}")
        # Load image using PIL
        image = Image.open(img_path).convert('RGB')
        print(f"Image size: {image.size}")
        
        # Generate embedding
        with torch.no_grad():
            embedding_batch = model.encode(
                [image],  # A list containing the PIL image
                convert_to_tensor=True
            )
        embedding = embedding_batch[0].tolist()  # Convert to Python list
        print(f"Generated image embedding length: {len(embedding)}")
        return embedding
    except Exception as e:
        print(f"Error embedding image {img_path}: {e}")
        raise

def embed_text(text: str):
    """
    Generates an embedding for a piece of text using the CLIP text encoder.
    
    :param text: The text to embed.
    :return: Embedding vector as a list (float).
    """
    try:
        print(f"Embedding text: {text[:60]}...")  # Show first 60 chars
        with torch.no_grad():
            embedding_batch = model.encode(
                [text],  # A list containing the text
                convert_to_tensor=True
            )
        embedding = embedding_batch[0].tolist()
        print(f"Generated text embedding length: {len(embedding)}")
        return embedding
    except Exception as e:
        print(f"Error embedding text: {text}: {e}")
        raise

if __name__ == "__main__":
    """
    Example usage for stand-alone embedding calls.
    The pipeline typically uses embed_image() or embed_text() programmatically.
    """
    if len(sys.argv) < 3:
        print("Usage: python clip_embedding.py <mode> <input>", file=sys.stderr)
        print("mode can be 'image' or 'text'")
        sys.exit(1)

    mode = sys.argv[1]
    input_item = sys.argv[2]

    try:
        if mode.lower() == 'image':
            # For demonstration, assume the image is relative to DATA_INPUT
            img_path = os.path.join(DATA_INPUT, "tiles", input_item)
            emb = embed_image(img_path)
            output_path = os.path.join(DATA_OUTPUT, "results", f"{os.path.splitext(input_item)[0]}_image_embedding.json")
        elif mode.lower() == 'text':
            emb = embed_text(input_item)
            output_path = os.path.join(DATA_OUTPUT, "results", f"text_embedding.json")
        else:
            raise ValueError("Mode must be 'image' or 'text'")

        # Save the embedding
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(emb, f, indent=4)
        print(f"Embedding saved to {output_path}")

    except Exception as e:
        print(f"Error generating embedding: {e}", file=sys.stderr)
        sys.exit(1)