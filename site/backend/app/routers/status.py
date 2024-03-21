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


# @r.get("/model_failure_inspection/list_image_ids")
# def get_model_failure_inspection_image_ids(processed: bool = False, db: Database = Depends(database.get_db)):
#     logger.debug(f"processed = {str(processed)}")
#     if "model_failure_inspection" not in db.list_collection_names():
#         logger.error("Collection 'model_failure_inspection' does not exist.")
#         raise HTTPException(status_code=404, detail="Collection 'model_failure_inspection' does not exist.")

#     crud_class = crud.BaseCRUD(db, "model_failure_inspection")

#     if not processed:
#         logger.debug("list W/O annotated filter")
#         image_ids = crud_class.list(limit=100)
#     else:
#         logger.debug("list WITH annotated filter")
#         # image_ids = crud_class.list_annotated()
#         image_ids = crud_class.list_annotated(limit=100)

#     if not image_ids:
#         logger.error("No documents found.")
#         raise HTTPException(status_code=404, detail="No documents found.")

#     logger.debug(f"length image_ids: {str(len(image_ids))}")
#     return {"image_ids": [x.get("image_id") for x in image_ids]}


# @r.post("/model_failure_inspection/get_image_data")
# def get_model_failure_inspection_sample(request: schema.ImageDataRequest, db: Database = Depends(database.get_db)):
#     image_id = request.image_id
#     logger.debug(image_id)
#     if "model_failure_inspection" not in db.list_collection_names():
#         logger.error("Collection 'model_failure_inspection' does not exist.")
#         raise HTTPException(status_code=404, detail="Collection 'model_failure_inspection' does not exist.")

#     crud_class = crud.BaseCRUD(db, "model_failure_inspection")
#     documents = crud_class.find_by_image_id(image_id)

#     if not documents:
#         logger.error("No documents found.")
#         raise HTTPException(status_code=404, detail="No documents found.")

#     return documents
