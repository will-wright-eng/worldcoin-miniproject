import os
from pathlib import Path

PROJECT_NAME = "worldcoin-miniproject"
mongodb_uri = os.environ.get("MONGODB_URI")
data_directory = Path(__file__).parent / "data"
