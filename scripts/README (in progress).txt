Introduction


This README provides a detailed description of the scripts included in the Modeled Homes HVAC project pipeline. Each script serves a specific purpose, contributing to the automation and processing pipeline from PDF input to actionable 3D modeling data.



Scripts


1. pdf_to_tiles.py

Purpose: Converts a PDF into high-resolution, tiled PNG images.

- Input: A PDF file.

- Output: Tiled PNG images saved in the data/tiles directory.

- Key Features:

  • Supports variable DPI settings for rendering.

  • Automatically divides large pages into manageable tiles for downstream processing.


2. clip_embedding.py

Purpose: Generates embeddings for images using a CLIP model.

Input: A single image (PNG) from data/tiles.

Output: Embedding vector for the image.

Key Features:

Outputs embeddings for similarity searches and further analysis.


3. batch_embed_tiles.py

Purpose: Processes all tiles in a directory to generate embeddings and store them in MongoDB.

- Input:

  • Directory of tiled images.

  • MongoDB connection details.

- Output: Stores embeddings in the plan_embeddings collection.

- Key Features:

  • Automates batch processing for embedding generation.


4. process_pdf.py

Purpose: Automates the pipeline from PDF tiling to embedding generation.

- Input:

  • PDF file.

  • Plan ID.

  • Output directory.

- Output:

  • Tiled images in data/tiles.

  • Stored embeddings in MongoDB.

- Key Features:

  • Integrates pdf_to_tiles.py and batch_embed_tiles.py into a single workflow.


5. process_tiles_ocr.py

Purpose: Performs OCR (Optical Character Recognition) on multiple images to extract text and bounding boxes.

- Input: All PNG images from the data/tiles directory recursively.

- Output:

  • JSON file containing OCR results saved in data/output/results.

  • Visualizations are saved in the visualizations subfolder.

- Key Features:

  • Utilizes MMOCR for text detection and recognition.

  • Designed for batch processing in the future.


6. line_detection.py

Purpose: Detects lines from an image using the Hough Transform.

- Input: A single PNG image from data/tiles.

- Output: JSON file of detected lines saved in data/output/results.

- Key Features:

  • Outputs line coordinates for use in dimension mapping.


7. categorize_ocr.py

Purpose: Categorizes text from OCR results into dimensions, labels, and miscellaneous categories.

- Input: OCR results JSON file from mmocr_test.py.

- Output: Categorized JSON file saved in data/output/results.

- Key Features:

  • Regex-based categorization for efficient text parsing.


8. link_dimensions.py

Purpose: Links dimension text to the nearest detected lines for wall association.

- Input:

  • Categorized OCR results JSON file from categorize_ocr.py.

  • Line detection results JSON file from line_detection.py.

- Output: JSON file of linked dimensions saved in data/output/results.

- Key Features:

  • Associates dimension text with the closest lines.

  • Computes the distance between points and lines to find matches.



Directory Structure


- Input Files: data/input

  • All uploaded PDFs are stored here.

- Tile Outputs: data/tiles

  • Contains tiled PNG images from pdf_to_tiles.py.

- Results: data/output/results

  • Contains JSON results for OCR, line detection, and linked dimensions.

- Scripts: scripts

  • Contains all pipeline scripts.



Next Steps


1. Complete automation of batch processing for OCR and embedding.

2. Expand functionality to refine and build the 3D model pipeline.

3. Develop documentation for user and developer workflows.

4. Conduct performance testing for scalability with larger datasets.