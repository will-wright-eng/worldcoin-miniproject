import datetime
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import Depends, APIRouter, HTTPException
from pymongo.database import Database

from app.db import database
from app.core import log

analytics_router = r = APIRouter(
    prefix="/analytics",
)

logger = log.get_logger(__name__)


def serialize_document(document):
    if document:
        # Convert ObjectId to str and ensure the document is a dict
        return {k: str(v) if isinstance(v, ObjectId) else v for k, v in document.items()}
    return document


def serialize_documents(documents: List[Dict]):
    return [serialize_document(doc) for doc in documents]


@r.get("/annotations/{image_id}")
def get_image_analytics(image_id: str, db: Database = Depends(database.get_db)):
    metadata_check = db.image_metadata.find_one({"image_id": image_id})

    if not metadata_check:
        raise HTTPException(status_code=404, detail="No data found for the provided image_id.")

    metadata = serialize_document(metadata_check)
    bbox_models = serialize_documents(db.bbox_model.find({"image_id": image_id}))
    bbox_human_audit = serialize_document(db.bbox_audit.find_one({"image_id": image_id}))
    bbox_human_annotations = serialize_documents(db.bbox_annotation.find({"image_id": image_id}))

    logger.debug(f"metadata length: {len(metadata)}")
    logger.debug(f"bbox_models length: {len(bbox_models) if bbox_models else 0}")
    logger.debug(f"bbox_human_audit length: {len(bbox_human_audit) if bbox_human_audit else 0}")
    logger.debug(f"bbox_human_annotations length: {len(bbox_human_annotations) if bbox_human_annotations else 0}")

    combined_data: Dict[str, Any] = {
        "image_id": image_id,
        "metadata": metadata,
        "bbox_models": bbox_models,
        "bbox_human_audit": bbox_human_audit,
        "bbox_human_annotations": bbox_human_annotations,
    }

    return combined_data


@r.get("/audits/outcomes_over_time")
def audit_outcomes_endpoint(db: Database = Depends(database.get_db)):
    metadata_cursor = db.image_metadata.find({}, {"image_id": 1, "capture_timestamp": 1})
    # Directly convert cursor to a list
    metadata_list = list(metadata_cursor)
    logger.debug(f"metadata_list len: {len(metadata_list)}")
    metadata_dict = {doc["image_id"]: doc for doc in metadata_list}
    logger.debug(f"metadata_dict len: {len(metadata_dict)}")

    audits_cursor = db.bbox_audit.find({}, {"image_id": 1, "bbox_correct": 1})
    # Directly convert cursor to a list
    audits_list = list(audits_cursor)
    logger.debug(f"audits_list len: {len(audits_list)}")

    # Combine Data
    combined_data = {}
    for audit in audits_list:
        image_id = audit["image_id"]
        meta = metadata_dict.get(image_id)
        if meta:
            timestamp = datetime.datetime.fromtimestamp(meta["capture_timestamp"])
            year = timestamp.year
            month = timestamp.month
            key = f"{year}-{month}"
            if key not in combined_data:
                combined_data[key] = {"correct_count": 0, "incorrect_count": 0}
            if audit.get("bbox_correct"):
                combined_data[key]["correct_count"] += 1
            else:
                combined_data[key]["incorrect_count"] += 1

    result = [{"year_month": key, **values} for key, values in combined_data.items()]
    return {"data": result}
