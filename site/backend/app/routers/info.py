import os
from typing import Optional

from fastapi import Depends, APIRouter, HTTPException

from app.db import crud, database
from app.core import log, config

info_router = r = APIRouter(
    prefix="/info",
)

logger = log.get_logger(__name__)


@r.get("/data_details")
def get_data_details():
    return {
        "current working directory": os.getcwd(),
        "data files": os.listdir("app"),
        "data directory files": os.listdir(config.data_directory),
    }


@r.get("/mongodb_info")
def get_mongodb_info(db=Depends(database.get_db)):
    return {"mongodb_uri": config.mongodb_uri, "database": db.name, "collections": db.list_collection_names()}


@r.get("/sample/{collection_name}")
def get_sample(collection_name: str = "bbox_annotation", skip: Optional[int] = 0):
    """Get a sample document from the specified collection."""
    crud_class = crud.get_crud_class(collection_name)
    documents = crud_class.list(skip=skip, limit=1)
    if documents:
        return documents[0]
    else:
        raise HTTPException(status_code=404, detail="No documents found.")


@r.get("/count/{collection_name}")
def get_count(collection_name: str = "bbox_annotation"):
    """Get the number of documents in the specified collection."""
    crud_class = crud.get_crud_class(collection_name)
    count = crud_class.get_doc_count()
    return {"count": count}


@r.get("/image_ids")
def get_image_ids(db=Depends(database.get_db)):
    image_metadata_crud = crud.ImageMetadataCRUD(db)
    image_ids = image_metadata_crud.list_image_ids()
    return {"image_ids": image_ids}


@r.get("/image_ids_limit/{limit}")
def get_image_ids_limit(limit: int = 10, db=Depends(database.get_db)):
    image_metadata_crud = crud.ImageMetadataCRUD(db)
    image_ids = image_metadata_crud.list(limit=limit)
    return {"image_ids": [x.get("image_id") for x in image_ids]}
