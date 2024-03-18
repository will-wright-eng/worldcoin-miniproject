from fastapi import Depends, APIRouter, HTTPException
from pymongo import ReplaceOne
from pymongo.database import Database

from app.db import crud, database

status_router = r = APIRouter(
    prefix="/status",
)


@r.get("/fraction_processed")
def get_fraction_processed(db: Database = Depends(database.get_db)):
    total_images = db.image_metadata.count_documents({})
    processed_images = db.bbox_model.count_documents({})
    fraction_processed = processed_images / total_images if total_images > 0 else 0
    return {"fraction_processed": fraction_processed}


@r.get("/fraction_correct_audits")
def get_fraction_correct_audits(db: Database = Depends(database.get_db)):
    total_audits = db.bbox_audit.count_documents({})
    correct_audits = db.bbox_audit.count_documents({"bbox_correct": True})
    fraction_correct = correct_audits / total_audits if total_audits > 0 else 0
    return {"fraction_correct_audits": fraction_correct}


@r.get("/count_unannotated_predictions")
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
    return {"unannotated_predictions_count": unannotated_count}


@r.post("/refresh_model_failure_inspection")
def refresh_model_failure_inspection(db: Database = Depends(database.get_db)):
    bbox_models = list(db.bbox_model.find({}))
    operations = []

    for model in bbox_models:
        image_id = model["image_id"]
        annotation = db.bbox_human_annotation.find_one({"image_id": image_id})

        for bbox in model.get("bboxes", []):
            predicted = bbox
            annotated = None
            delta = None

            if annotation:
                # calculate the delta between 'predicted' and 'annotated'
                annotated = annotation.get("bbox")
                delta = {
                    "top": annotated["top"] - predicted["top"],
                    "left": annotated["left"] - predicted["left"],
                    "bottom": annotated["bottom"] - predicted["bottom"],
                    "right": annotated["right"] - predicted["right"],
                }

            doc = {
                "image_id": image_id,
                "predicted": predicted,
                "annotated": annotated,
                "delta": delta,
            }
            operations.append(ReplaceOne({"image_id": image_id}, doc, upsert=True))

    if operations:
        db.model_failure_inspection.bulk_write(operations)

    return {"message": "Model failure inspection collection refreshed."}


@r.get("/model_failure_inspection/sample")
def get_model_failure_inspection_sample(db: Database = Depends(database.get_db)):
    if "model_failure_inspection" not in db.list_collection_names():
        raise HTTPException(status_code=404, detail="Collection 'model_failure_inspection' does not exist.")

    crud_class = crud.BaseCRUD(db, "model_failure_inspection")
    documents = crud_class.list()

    if documents:
        return documents[0]
    else:
        raise HTTPException(status_code=404, detail="No documents found.")
