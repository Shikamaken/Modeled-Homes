import json
import matplotlib.pyplot as plt
import numpy as np
import os
import importlib.util

# Dynamically load config.py
config_path = os.path.join(os.path.dirname(__file__), "config.py")
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

# Retrieve required paths from config.py
DATA_OUTPUT = getattr(config, "DATA_OUTPUT", "output")

def infer_plan_id():
    """ Infers the most recent plan_id dynamically from the DATA_OUTPUT/results directory. """
    results_path = os.path.join(DATA_OUTPUT, "results")
    if not os.path.isdir(results_path):
        return "default_plan"
    
    plan_dirs = [d for d in os.listdir(results_path) if os.path.isdir(os.path.join(results_path, d))]
    
    if not plan_dirs:
        return "default_plan"
    
    # Sort directories by modification time (most recent first)
    plan_dirs.sort(key=lambda d: os.path.getmtime(os.path.join(results_path, d)), reverse=True)
    return plan_dirs[0]

def get_paths():
    """ Infers classified walls input path and output image path based on inferred plan_id. """
    plan_id = infer_plan_id()
    classified_walls_path = os.path.join(DATA_OUTPUT, "results", plan_id, "classified_walls.json")
    output_image_path = os.path.join(DATA_OUTPUT, "visualizations", plan_id, "wall_visualization.png")
    return classified_walls_path, output_image_path

def visualize_walls():
    """ Visualizes classified wall segments from JSON data. """
    classified_walls_path, output_image_path = get_paths()
    
    with open(classified_walls_path, 'r', encoding='utf-8') as f:
        classified_walls = json.load(f)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Colors for wall types
    color_map = {
        "exterior": "green",
        "interior": "blue",
        "unclassified": "red"
    }
    
    # Ensure the structure format is correctly parsed
    for category in ["exterior", "interior"]:
        if category in classified_walls and isinstance(classified_walls[category], list):
            for wall in classified_walls[category]:
                if isinstance(wall, list) and len(wall) == 2:
                    x_values = [wall[0][0], wall[1][0]]
                    y_values = [wall[0][1], wall[1][1]]
                    
                    ax.plot(x_values, y_values, color=color_map[category], linewidth=2)
                else:
                    print(f"Skipping malformed wall entry in {category}: {wall}")
    
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Visualized Walls")
    
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    plt.savefig(output_image_path)
    plt.show()
    
    print(f"Wall visualization saved to {output_image_path}")

if __name__ == "__main__":
    visualize_walls()