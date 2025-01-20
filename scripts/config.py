from dotenv import load_dotenv
import os

# Project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Local file paths
DATA_INPUT = os.path.join(PROJECT_ROOT, "data", "input")
DATA_OUTPUT = os.path.join(PROJECT_ROOT, "data", "output")
DATA_TILES = os.path.join(PROJECT_ROOT, "data", "tiles")

# Tiling parameters
DEFAULT_DPI = 300
DEFAULT_TILE_SIZE = 3000

# Load the .env file from the root directory
load_dotenv(dotenv_path='../.env')

# Access the environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
PORT = os.getenv('PORT')