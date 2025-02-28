from dotenv import load_dotenv
import os

# Project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Local file paths
DATA_USER = os.path.join(PROJECT_ROOT, "data", "user")
DATA_OUTPUT = os.path.join(PROJECT_ROOT, "data", "output")
DATA_TILES = os.path.join(PROJECT_ROOT, "data", "tiles")

# Tiling parameters
DEFAULT_DPI = 300
DEFAULT_TILE_SIZE = 3000

# Load the .env file from the root directory
load_dotenv(dotenv_path='../.env')

def get_user_project_path(uuid, plan_id):
    """
    Returns the full input path for a user's project.

    Args:
        uuid (str): The UUID of the user/organization.
        plan_id (str): The plan ID (derived from the PDF filename).

    Returns:
        str: Full path to the project's input directory.
    """
    return os.path.join(DATA_USER, uuid, "projects", plan_id)

# Access the environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
PORT = os.getenv('PORT')