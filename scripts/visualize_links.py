import json
import matplotlib.pyplot as plt

# Enable or disable logging for debugging
LOGGING_ENABLED = True

# Minimum line length for filtering
MIN_LINE_LENGTH = 50

def visualize_links(categorized_path, lines_path):
    """
    Visualizes dimension bounding boxes and detected lines per page.
    
    :param categorized_path: Path to categorized_results.json.
    :param lines_path: Path to line_detection_results.json.
    """
    with open(categorized_path, 'r', encoding='utf-8') as f:
        categorized_data = json.load(f)
    with open(lines_path, 'r', encoding='utf-8') as f:
        line_data = json.load(f)

    # Filter lines based on minimum length
    filtered_lines = []
    for line_entry in line_data:
        line = line_entry["line"]
        line_length = ((line[1][0] - line[0][0])**2 + (line[1][1] - line[0][1])**2)**0.5
        if line_length >= MIN_LINE_LENGTH:
            filtered_lines.append(line_entry)
    if LOGGING_ENABLED:
        print(f"Filtered lines count: {len(filtered_lines)}")

    # Get all unique page indices
    page_indices = sorted(set(entry["page_index"] for entry in categorized_data))

    for page_index in page_indices:
        fig, ax = plt.subplots()
        ax.set_title(f'Page {page_index}')
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')

        # Plot dimensions for the current page
        for text_entry in categorized_data:
            if text_entry["page_index"] == page_index and text_entry["category"] == "dimension":
                bbox = text_entry["bbox"]
                center_x = sum(bbox[::2]) / 2
                center_y = sum(bbox[1::2]) / 2
                ax.scatter(center_x, center_y, color='blue', label='Dimension' if 'Dimension' not in ax.get_legend_handles_labels()[1] else None)
                if LOGGING_ENABLED:
                    print(f"Page {page_index}: Plotted dimension at ({center_x}, {center_y})")

        # Plot lines for the current page
        for line_entry in filtered_lines:
            if line_entry.get("page_index", -1) == page_index:
                line = line_entry["line"]
                x_coords, y_coords = zip(*line)
                ax.plot(x_coords, y_coords, color='red', label='Line' if 'Line' not in ax.get_legend_handles_labels()[1] else None)
                if LOGGING_ENABLED:
                    print(f"Page {page_index}: Plotted line {line}")

        # Add legend, grid, and show
        ax.legend()
        ax.grid(True)
        ax.set_aspect('equal', adjustable='box')
        plt.show()

if __name__ == "__main__":
    # Define file paths
    categorized_path = "C:\\Users\\shika\\modeled-homes-hvac\\data\\output\\results\\716 Baxter Ave S\\categorized_results.json"
    lines_path = "C:\\Users\\shika\\modeled-homes-hvac\\data\\output\\results\\716 Baxter Ave S\\line_detection_results.json"

    # Visualize links
    visualize_links(categorized_path, lines_path)