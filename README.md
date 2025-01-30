# Modeled Homes

**AI-powered automation for MEP subcontractors.**

Modeled Homes is a software platform that converts **2D building plans into interactive 3D and AR models**, streamlining project design and bid creation for MEP subcontractors. By leveraging **AI-driven automation**, we help contractors reduce manual work, generate accurate bids faster, and enhance project execution through AR visualization.

---

## 🚀 How It Works
Modeled Homes automates the conversion of **PDF-based floor plans** into **structured, interactive data** through the following pipeline:

1. **OCR & Text Recognition** – Extracts structured text from building plans using **PDFPlumber for embedded text extraction** and **MMOCR for OCR-based recognition**.
2. **Line Detection** – Identifies architectural elements using **Canny edge detection & Hough Transform**.
3. **Data Structuring** – Links detected lines with extracted dimensions and categorizes text.
4. **Vector Search & Storage** – Stores structured data in **MongoDB** for efficient retrieval.
5. **3D Model Foundation** – Lays the groundwork for **3D rendering & AR visualization**.

---

## 🔧 Tech Stack
- **Programming Language:** Python  
- **AI & OCR:** MMOCR, CLIP (SentenceTransformers)  
- **Computer Vision:** OpenCV, NumPy  
- **Database:** MongoDB (Vector Search Enabled)  
- **Data Processing:** PDFPlumber  

---

## 📌 Current Progress & Roadmap

### ✅ **Current Features:**
✔ PDFPlumber & OCR pipeline successfully extracts text from 2D plans.  
✔ Line detection identifies structural elements with high accuracy.  
✔ Initial data linking & categorization complete.  
✔ Vector-based search implemented for structured retrieval.  

### 🔜 **Next Steps:**
➡ Improve text alignment & category precision.  
➡ Generate structured 3D models from extracted data.  
➡ Develop and refine the **HVAC Design Suite** to ensure full functionality for users.  
➡ Integrate AR for on-site project visualization.  
➡ Automate MEP design calculations and bid generation (HVAC load, energy, materials, etc.).  

---

## 📂 Repository Structure

```
modeled-homes/
│── backend/               # Node.js backend for API & data processing
│   ├── controllers/              # API controllers
│   ├── middleware/               # Express middleware
│   ├── models/                   # Database models
│   ├── routes/                   # API routes
│   ├── tests/                    # Backend unit tests
│   ├── utils/                    # Utility functions
│   ├── package.json              # Backend dependencies
│   ├── server.js                 # Main server file
│── frontend/              # React frontend
│   ├── public/                   # Static assets
│   ├── src/                      # React components & logic
│   ├── .babel.rc                 # Babel configuration
│   ├── package.json              # Frontend dependencies
│   ├── webpack.config.js         # Webpack configuration
│── data/                  # Input & output data
│   ├── input/                    # Raw building plan data
│   ├── output/                   # Processed data
│── scripts/               # Python AI & processing scripts
│   ├── config.py                 # Stores global pipeline and database settings
│   ├── label_keywords.txt        # Keyword list used for text categorization
│   ├── my_domain_dictionary.txt  # Custom dictionary for domain-specific text processing
│   ├── extract_embedded_text.py  # Extracts embedded text from PDFs
│   ├── pdf_to_tiles.py           # Converts full PDF pages into smaller tiled images for processing
│   ├── ocr_tiles.py              # Runs OCR on extracted tiles
│   ├── merge_text.py             # Merges extracted text with structured data
│   ├── categorize_text.py        # Classifies extracted text for classification
│   ├── line_detection.py         # Detects walls & structures
│   ├── link_dimensions.py        # Links extracted dimensions to detected elements
│   ├── assemble_overlay.py       # Combines extracted data into structured format
│   ├── batch_embed_overlays.py   # Embeds overlay data for AI processing
│   ├── clip_embedding.py         # Embeds images & text for vector search
│   ├── pdf_model_conv.py         # Orchestrates the full pipeline execution
│   ├── visualize_links.py        # Generates visual renderings of processed plans (test script, run after pipeline completion)
│── tools/                 # AI training & inference scripts
│   ├── infer.py                  # AI inference logic
│   ├── train.py                  # AI training script
│── .gitignore             # Ignore unnecessary files
│── README.md              # Project overview & documentation
│── requirements.txt       # Dependencies for easy installation
```

---

## 🛠 Installation & Setup (Optional)

1. **Clone the repository:**
```bash
git clone https://github.com/Shikamaken/Modeled-Homes.git
cd Modeled-Homes
```
2. **Install dependencies:**
```bash
pip install -r requirements.txt
```
3. **Run the pipeline:**
```bash
python scripts/pdf_model_conv.py
```

---

## 📞 Contact

📧 **Email:** [kenny@modeledhomes.com](mailto:kenny@modeledhomes.com)