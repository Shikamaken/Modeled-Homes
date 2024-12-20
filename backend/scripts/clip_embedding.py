import sys
import json
from PIL import Image
import torch
from torchvision import transforms
from sentence_transformers import SentenceTransformer

# Load a CLIP model via sentence-transformers
# This model name can be changed if needed, ensure to pick a CLIP model
model = SentenceTransformer('clip-ViT-B-32')

def embed_image(img_path: str):
    image = Image.open(img_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.48145466, 0.4578275, 0.40821073],
            std=[0.26862954, 0.26130258, 0.27577711]
        )
    ])
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        embedding = model.encode({"image": tensor}, convert_to_tensor=True)
    return embedding.squeeze().tolist()  # converts to Python list

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 clip_embedding.py <path_to_image>", file=sys.stderr)
        sys.exit(1)

    img_path = sys.argv[1]
    emb = embed_image(img_path)
    # Print JSON embedding so Node.js can read it
    print(json.dumps(emb))