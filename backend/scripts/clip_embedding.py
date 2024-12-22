from PIL import Image
from sentence_transformers import SentenceTransformer
import json

# Load the CLIP model
model = SentenceTransformer('clip-ViT-B-32')

def embed_image(img_path: str, tile_size: int = 2000):
    # Open the image
    image = Image.open(img_path).convert('RGB')
    width, height = image.size

    # Tile the image and encode each tile
    embeddings = []
    tile_index = 0
    for x in range(0, width, tile_size):
        for y in range(0, height, tile_size):
            # Define the bounding box for the tile
            box = (x, y, min(x + tile_size, width), min(y + tile_size, height))
            tile = image.crop(box)

            # Encode the tile and store the result with its index
            tile_embedding = model.encode([tile], convert_to_tensor=True)
            embeddings.append({
                "tileIndex": tile_index,
                "embedding": tile_embedding.squeeze().tolist()
            })
            tile_index += 1

    return embeddings

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 clip_embedding.py <path_to_image>", file=sys.stderr)
        sys.exit(1)

    img_path = sys.argv[1]

    # Optional: Suppress the decompression bomb warning for testing
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None

    embeddings = embed_image(img_path)

    # Output the embeddings as JSON
    print(json.dumps(embeddings))