import os
import sys
import json
import math
import argparse

def point_to_line_distance(point, line):
    """
    Calculates the perpendicular distance from a point to a line segment.
    """
    x0, y0 = point
    x1, y1, x2, y2 = line
    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    return numerator / denominator if denominator != 0 else float('inf')

def link_dimensions(categorized_path, lines_path, output_path):
    """
    Links dimension text to the nearest detected lines.
    
    :param categorized_path: Path to the categorized text JSON file.
    :param lines_path: Path to the line detection results JSON file.
    :param output_path: Path to save the linked dimensions JSON file.
    """
    if not os.path.isfile(categorized_path) or not os.path.isfile(lines_path):
        raise FileNotFoundError("Categorized or line detection results file missing.")

    with open(categorized_path, 'r', encoding='utf-8') as f:
        categorized_data = json.load(f)

    try:
        with open(lines_path, 'r', encoding='utf-8') as f:
            line_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in line detection results: {lines_path}") from e

    linked_results = []
    MAX_DISTANCE = 1000  # Set an appropriate threshold based on document scale

    for text_entry in categorized_data:
        if text_entry["category"] != "dimension":
            continue

        bbox = text_entry["bbox"]
        center_x = sum(bbox[::2]) / len(bbox[::2])
        center_y = sum(bbox[1::2]) / len(bbox[1::2])
        center = (center_x, center_y)

        nearest_line = None
        min_distance = float('inf')

        for line_entry in line_data:
            line = line_entry.get("line", [])
            if len(line) == 2 and all(isinstance(pt, list) for pt in line):
                flat_line = [coord for pt in line for coord in pt]
                distance = point_to_line_distance(center, flat_line)

                if distance < min_distance:
                    min_distance = distance
                    nearest_line = line

        # Apply the threshold
        if nearest_line and min_distance <= MAX_DISTANCE:
            linked_results.append({
                **text_entry,
                "nearest_line": nearest_line,
                "distance": min_distance
            })
        else:
            print(f"Dimension '{text_entry['text']}' at {center} has no nearby lines (min_distance={min_distance}).")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(linked_results, f, indent=4)

    print(f"Linked dimensions saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Link dimensions to detected lines.")
    parser.add_argument("categorized_path", help="Path to the categorized text JSON file.")
    parser.add_argument("lines_path", help="Path to the line detection results JSON file.")
    parser.add_argument("output_path", help="Path to save the linked dimensions JSON file.")
    args = parser.parse_args()

    try:
        link_dimensions(args.categorized_path, args.lines_path, args.output_path)
    except Exception as e:
        print(f"Error linking dimensions: {e}")