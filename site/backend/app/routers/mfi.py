import json

from bson import json_util
from fastapi import Depends, APIRouter, HTTPException
from pymongo import ReplaceOne
from pymongo.database import Database

from app.db import crud, database
from app.core import log, schema

mfi_router = r = APIRouter(
    prefix="/model_failure_inspection",
)

logger = log.get_logger(__name__)


def parse_json(data):
    return json.loads(json_util.dumps(data))


@r.get("/sample")
def get_sample(db: Database = Depends(database.get_db)):
    if "model_failure_inspection" not in db.list_collection_names():
        raise HTTPException(status_code=404, detail="Collection 'model_failure_inspection' does not exist.")

    crud_class = crud.BaseCRUD(db, "model_failure_inspection")
    documents = crud_class.list()

    if documents:
        return documents[0]
    else:
        raise HTTPException(status_code=404, detail="No documents found.")


@r.get("/list_image_ids")
def get_image_id_list(processed: bool = False, db: Database = Depends(database.get_db)):
    logger.debug(f"processed = {str(processed)}")
    if "model_failure_inspection" not in db.list_collection_names():
        logger.error("Collection 'model_failure_inspection' does not exist.")
        raise HTTPException(status_code=404, detail="Collection 'model_failure_inspection' does not exist.")

    crud_class = crud.BaseCRUD(db, "model_failure_inspection")

    if not processed:
        logger.debug("list W/O annotated filter")
        image_ids = crud_class.list(limit=100)
    else:
        logger.debug("list WITH annotated filter")
        image_ids = crud_class.list_annotated(limit=100)

    if not image_ids:
        logger.error("No documents found.")
        raise HTTPException(status_code=404, detail="No documents found.")

    logger.debug(f"length image_ids: {str(len(image_ids))}")
    return {"image_ids": [x.get("image_id") for x in image_ids]}


@r.get("/count")
def get_count(db: Database = Depends(database.get_db)):
    if "model_failure_inspection" not in db.list_collection_names():
        logger.error("Collection 'model_failure_inspection' does not exist.")
        raise HTTPException(status_code=404, detail="Collection 'model_failure_inspection' does not exist.")

    crud_class = crud.BaseCRUD(db, "model_failure_inspection")
    count = crud_class.get_doc_count()
    return {"count": count}


@r.post("/get_image_data")
def get_image_data(request: schema.ImageDataRequest, db: Database = Depends(database.get_db)):
    image_id = request.image_id
    logger.debug(image_id)
    if "model_failure_inspection" not in db.list_collection_names():
        logger.error("Collection 'model_failure_inspection' does not exist.")
        raise HTTPException(status_code=404, detail="Collection 'model_failure_inspection' does not exist.")

    crud_class = crud.BaseCRUD(db, "model_failure_inspection")
    documents = crud_class.find_by_image_id(image_id)

    if not documents:
        logger.error("No documents found.")
        raise HTTPException(status_code=404, detail="No documents found.")

    return documents


def reshape_box(box):
    if box:
        return {
            "top": box["center_y"] + (box["height"] / 2),
            "bottom": box["center_y"] - (box["height"] / 2),
            "left": box["center_x"] - (box["width"] / 2),
            "right": box["center_x"] + (box["width"] / 2),
        }
    else:
        return None


def get_delta(annotated, predicted):
    if annotated and predicted:
        return {
            "top": annotated["top"] - predicted["top"],
            "left": annotated["left"] - predicted["left"],
            "bottom": annotated["bottom"] - predicted["bottom"],
            "right": annotated["right"] - predicted["right"],
        }
    else:
        return None


@r.post("/refresh_collection")
def refresh_model_failure_inspection(db: Database = Depends(database.get_db)):
    """
    assume that there is only one annotation per image
    find_one() returns a dict
    multiple models per image, use the most recent model_version
    find() returns a cursor that can be iterated through
    list() constructor loads the entire collection into memory
    """
    bbox_models = db.bbox_model.find({})
    operations = []

    counter = 0
    for model_document in bbox_models:
        image_id = model_document.get("image_id")

        annotations = list(db.bbox_annotation.find({"image_id": image_id}))
        if len(annotations) > 1:
            logger.debug(f"annotation count: {str(len(annotations))}")
            annotation = max(annotations, key=lambda x: x["task_version"])
        elif len(annotations) == 1:
            annotation = annotations[0]
        else:
            annotation = None

        models = list(db.bbox_model.find({"image_id": image_id}))
        if len(models) > 1:
            model = max(models, key=lambda x: x["model_version"])
        else:
            model = models[0]

        annotated = None
        predicted = None

        # CASE 1
        if annotation and model:
            # prioritize human bounding box annotations over model predictions.
            # calculate the delta between 'predicted' and 'annotated'
            model_version = model.get("model_version")
            predicted = []
            if model_version == "2.0.0":
                for box in model.get("bboxes"):
                    predicted.append(reshape_box(box))
            else:
                predicted = model.get("bboxes")

            task_version = annotation.get("task_version")
            if task_version == "2.0.0":
                annotated = reshape_box(box.get("bbox"))
            else:
                annotated = annotation.get("bboxes")

        # CASE 2
        elif annotation and not model:
            logger.error(
                "only human annotations - should not happen since we are using image_ids from models collection",
            )

        # CASE 3
        elif not annotation and model:
            # only model predictions
            model_version = model.get("model_version")
            predicted = []
            if model_version == "2.0.0":
                for box in model.get("bboxes"):
                    predicted.append(reshape_box(box))
            else:
                predicted = model.get("bboxes")
            # implement audit check
            audit = db.audit.find_one({"image_id": image_id})
            if audit:
                # should this be an exclusion criteria?
                audit_bool = audit.get("bbox_correct")

        # CASE 1
        # if annotation and model:
        if annotated and predicted:
            # there is no join key between model and annotation
            # assumes that the bbox models and annotations correspond in their order
            logger.debug(f"annotation vs predicted: {str(len(annotated))} vs {str(len(predicted))}")
            for abox, pbox in zip(annotated, predicted):
                doc = {
                    "image_id": image_id,
                    "predicted": pbox,
                    "annotated": abox,
                    "delta": get_delta(abox, pbox),
                }
                operations.append(ReplaceOne({"image_id": image_id}, doc, upsert=True))

        # CASE 3
        elif not annotated and predicted:
            for pbox in predicted:
                doc = {
                    "image_id": image_id,
                    "predicted": pbox,
                    "annotated": None,
                    "delta": None,
                }
                operations.append(ReplaceOne({"image_id": image_id}, doc, upsert=True))

    if operations:
        db.model_failure_inspection.bulk_write(operations)
        logger.debug(f"length operations: {len(operations)}")
        logger.debug(f"annotation and model counter: {str(counter)}")

    return {"message": "Model failure inspection collection refreshed."}


@r.get("/log_annotations")
def log_annotations(db: Database = Depends(database.get_db)):
    """write endpoint to log debug all annotations to determine task versions and bbox shape"""
    documents = db.bbox_annotation.find({})
    for document in documents:
        tmp = parse_json(document)
        logger.debug(f"document: {json.dumps(tmp, indent=2)}")

    return {"message": "logging complete"}
