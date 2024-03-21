from fastapi import Depends, APIRouter, HTTPException
from pymongo.database import Database

from app.db import database
from app.core import log, schema

status_router = r = APIRouter(
    prefix="/status",
)

logger = log.get_logger(__name__)


@r.get("/fraction_processed", response_model=schema.StatusResponse)
def get_fraction_processed(db: Database = Depends(database.get_db)):
    total_images = db.image_metadata.count_documents({})
    processed_images = db.bbox_model.count_documents({})
    fraction_processed = processed_images / total_images if total_images > 0 else 0
    return schema.StatusResponse(field_name="fraction_processed", value=fraction_processed)


@r.get("/fraction_correct_audits", response_model=schema.StatusResponse)
def get_fraction_correct_audits(db: Database = Depends(database.get_db)):
    total_audits = db.bbox_audit.count_documents({})
    correct_audits = db.bbox_audit.count_documents({"bbox_correct": True})
    fraction_correct = correct_audits / total_audits if total_audits > 0 else 0
    return schema.StatusResponse(field_name="fraction_correct_audits", value=fraction_correct)


@r.get("/count_unannotated_predictions", response_model=schema.StatusResponse)
def count_unannotated_predictions(db: Database = Depends(database.get_db)):
    if "model_failure_inspection" not in db.list_collection_names():
        raise HTTPException(status_code=404, detail="Collection 'model_failure_inspection' does not exist.")

    unannotated_count = db.model_failure_inspection.count_documents(
        {
            "$or": [
                {"annotated": None},
                {"annotated": {"$exists": False}},
            ],
        },
    )
    return schema.StatusResponse(field_name="unannotated_predictions_count", value=unannotated_count)
