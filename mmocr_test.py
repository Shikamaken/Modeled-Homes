from mmocr.apis import MMOCRInferencer
import os
import json

# Define directories and paths
save_dir = "C:/Users/shika/modeled-homes-hvac/visualizations"
os.makedirs(save_dir, exist_ok=True)  # Ensure the save directory exists
test_image_path = "C:/Users/shika/OneDrive/Desktop/MH/Building Plans/PNG Stitch/LSP Thumbnails/Page 3/LSP_page3_sec19.png"
output_path = "C:/Users/shika/modeled-homes-hvac/ocr_results.json"

# Initialize the MMOCRInferencer
mmocr = MMOCRInferencer(
    det='DBNet',
    rec='SAR',
    device='cpu',  # Explicitly set to CPU
    vis_backend=dict(type='LocalVisBackend', save_dir=save_dir)
)

# Perform OCR with exception handling
try:
    results = mmocr(test_image_path, save_vis=True)

    # Save results to JSON
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"OCR results saved to {output_path}")
except Exception as e:
    print(f"An error occurred during OCR processing: {e}")
