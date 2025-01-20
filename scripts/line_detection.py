import os
import json
import cv2
import numpy as np
import argparse

def detect_lines_in_image(image_path):
    """
    Detect lines in an image using Hough Transform.
    :param image_path: Path to the input image file.
    :return: List of detected lines with their rho and theta values.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Failed to load image: {image_path}")

    edges = cv2.Canny(image, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    lines_list = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * a))
            pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * a))
            lines_list.append({
                "line": [pt1, pt2],
                "rho": rho,
                "theta": theta
            })

    return lines_list

def process_line_detection(input_dir, tile_meta_path, output_path):
    """
    Processes all images in a directory for line detection and includes page_index.
    :param input_dir: Path to the directory containing images.
    :param tile_meta_path: Path to the tile metadata JSON file.
    :param output_path: Path to save the line detection results.
    """
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"Input directory not found: {input_dir}")

    if not os.path.isfile(tile_meta_path):
        raise FileNotFoundError(f"Tile metadata file not found: {tile_meta_path}")

    with open(tile_meta_path, 'r', encoding='utf-8') as f:
        tile_metadata = json.load(f)

    results = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".png"):
                image_path = os.path.join(root, file)
                try:
                    detected_lines = detect_lines_in_image(image_path)

                    # Retrieve metadata for the current tile
                    tile_filename = os.path.basename(image_path)
                    tile_meta = next((meta for meta in tile_metadata if meta["tile_filename"] == tile_filename), None)
                    if not tile_meta:
                        print(f"Metadata not found for tile: {tile_filename}. Skipping.")
                        continue

                    page_index = tile_meta["page_index"]

                    # Include page_index in the results
                    results.extend([{
                        "image_path": image_path,
                        "page_index": page_index,
                        "line": [[float(coord) for coord in pt] for pt in line["line"]],
                        "rho": float(line["rho"]),
                        "theta": float(line["theta"])
                    } for line in detected_lines])

                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)

    print(f"Line detection results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect lines in tile images and include page_index.")
    parser.add_argument("input_dir", help="Directory containing tile images.")
    parser.add_argument("tile_meta_path", help="Path to the tile metadata JSON file.")
    parser.add_argument("output_path", help="Path to save the line detection results.")
    args = parser.parse_args()

    try:
        process_line_detection(args.input_dir, args.tile_meta_path, args.output_path)
    except Exception as e:
        print(f"Error during line detection: {e}")