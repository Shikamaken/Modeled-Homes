import json
import numpy as np

def classify_walls(lines_list):
    """
    Classifies detected lines into interior or exterior walls.
    """
    exterior_walls = []
    interior_walls = []
    
    for i, line_a in enumerate(lines_list):
        for j, line_b in enumerate(lines_list):
            if i >= j:
                continue
            
            # Calculate midpoint distance
            dist = np.linalg.norm(
                np.array(line_a["pdf_line"][0]) - np.array(line_b["pdf_line"][0])
            )
            
            # Adjusted thresholds to be less strict
            if 10 <= dist <= 22:
                exterior_walls.append(line_a)
                exterior_walls.append(line_b)
            elif 5 <= dist <= 12:
                interior_walls.append(line_a)
                interior_walls.append(line_b)

    exterior_set = {(tuple(w["pdf_line"][0]), tuple(w["pdf_line"][1])) for w in exterior_walls if len(w["pdf_line"]) >= 2}
    interior_set = {(tuple(w["pdf_line"][0]), tuple(w["pdf_line"][1])) for w in interior_walls if len(w["pdf_line"]) >= 2}

    return {
        "exterior": [ [list(pt1), list(pt2)] for pt1, pt2 in exterior_set ],
        "interior": [ [list(pt1), list(pt2)] for pt1, pt2 in interior_set ]
    }

def process_classification(input_path, output_path):
    """
    Processes detected lines and classifies walls.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        lines_list = json.load(f)
    
    classified_walls = classify_walls(lines_list)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(classified_walls, f, indent=4)
    
    print(f"Wall classification results saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Classify detected walls into interior and exterior.")
    parser.add_argument("input_path", help="Path to the line detection results JSON.")
    parser.add_argument("output_path", help="Path to save classified structures JSON.")
    args = parser.parse_args()
    
    process_classification(args.input_path, args.output_path)