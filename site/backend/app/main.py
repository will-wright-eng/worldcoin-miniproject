import os
import json
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from pymongo import MongoClient
from app.core import log, config

logger = log.get_logger(__name__)
app = FastAPI(title=config.PROJECT_NAME, docs_url="/api/docs", openapi_url="/api")

# MongoDB URI and client setup
# mongodb_uri = 'mongodb_uri'  # Replace with your actual MongoDB URI
mongodb_uri = os.environ.get("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client["machine_learning_pipeline"]

collections = {
    "bbox_annotation": "bbox.annotation.json",
    "bbox_audit": "bbox.audit.json",
    "bbox_model": "bbox.model.json",
    "image_metadata": "metadata.json",
}

# data_directory = Path(__file__).parent / 'data'  # Adjust this if your script is located elsewhere
data_directory = Path(__file__).parent / "data"


# Function to check if the collection already exists and has data
def check_existing_data(collection_name):
    collection = db[collection_name]
    if collection.estimated_document_count() > 0:
        return True
    return False


# Function to load JSON data from a file
def load_json_data(filename):
    with open(data_directory / filename, "r") as file:
        return json.load(file)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


@app.get("/")
def read_root():
    return {"Hello": "world"}


# @app.on_event("startup")
async def startup_event():
    for collection_name, file_name in collections.items():
        if not check_existing_data(collection_name):
            try:
                data = load_json_data(file_name)
                db[collection_name].insert_many(data)
                print(f"Inserted data into {collection_name} collection.")
            except FileNotFoundError:
                print(f"File {file_name} not found. Skipping {collection_name} collection.")
            except Exception as e:
                print(f"An error occurred: {e}")


@app.get("/populate_database")
async def populate_database():
    for collection_name, file_name in collections.items():
        if not check_existing_data(collection_name):
            try:
                data = load_json_data(file_name)
                db[collection_name].insert_many(data)
                return {collection_name: "Data inserted successfully"}
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=f"File {file_name} not found.")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    return {"detail": "Data already exists in the database"}


@app.get("/data_details")
def get_data_details():
    # return the current working directory and files in it
    return {
        "current working directory": os.getcwd(),
        "data files": os.listdir("app"),
        "data directory files": os.listdir(data_directory),
    }
