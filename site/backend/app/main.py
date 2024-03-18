import json

from fastapi import Depends, FastAPI, Request, HTTPException

from app.db import crud, database
from app.core import log, config
from app.routers.info import info_router
from app.routers.cruds import crud_router
from app.routers.status import status_router
from app.routers.analytics import analytics_router

logger = log.get_logger(__name__)
app = FastAPI(title=config.PROJECT_NAME, docs_url="/api/docs", openapi_url="/api")


def check_existing_data(db, collection_name):
    collection = db[collection_name]
    if collection.estimated_document_count() > 0:
        return True
    return False


def load_json_data(filename):
    with open(config.data_directory / filename, "r") as file:
        return json.load(file)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


@app.on_event("shutdown")
def shutdown_event():
    db = database.get_db()
    db.client.close()


@app.on_event("startup")
def startup_event():
    db = database.get_db()
    for collection_name, file_name in crud.collections.items():
        if not check_existing_data(db, collection_name):
            try:
                data = load_json_data(file_name)
                db[collection_name].insert_many(data)
                logger.info(f"Inserted data into {collection_name} collection.")
            except FileNotFoundError:
                logger.info(f"File {file_name} not found. Skipping {collection_name} collection.")
            except Exception as e:
                logger.info(f"An error occurred: {e}")


@app.get("/")
def root(db=Depends(database.get_db)):
    # Use the db instance directly.
    return {"message": "Hello World"}


@app.get("/populate_database")
def populate_database(db=Depends(database.get_db)):
    for collection_name, file_name in crud.collections.items():
        if not check_existing_data(db, collection_name):
            try:
                data = load_json_data(file_name)
                db[collection_name].insert_many(data)

                logger.info(f"Inserted data into {collection_name} collection.")
            except FileNotFoundError:
                error_str = f"File {file_name} not found."
                logger.error(error_str)
                raise HTTPException(status_code=404, detail=error_str)
            except Exception as e:
                logger.error(str(e))
                raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Data inserted successfully", "collections": db.list_collection_names()}


# Routers
app.include_router(
    crud_router,
    prefix="/v1",
    tags=["crud"],
)
app.include_router(
    info_router,
    prefix="/v1",
    tags=["info"],
)
app.include_router(
    analytics_router,
    prefix="/v1",
    tags=["analytics"],
)
app.include_router(
    status_router,
    prefix="/v1",
    tags=["status"],
)
