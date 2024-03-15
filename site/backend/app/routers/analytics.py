from fastapi import Depends, APIRouter, HTTPException
from pymongo.database import Database

from app.db import database
from app.core import log

analytics_router = r = APIRouter(
    prefix="/analytics",
)

logger = log.get_logger(__name__)


@r.get("/analytics/{image_id}")
async def get_image_analytics(image_id: str, db: Database = Depends(database.get_db)):
    pipeline = [
        {
            "$match": {"image_id": image_id},
        },
        {
            "$lookup": {
                "from": "bbox_audit",
                "localField": "image_id",
                "foreignField": "image_id",
                "as": "audit_info",
            },
        },
        {
            "$lookup": {
                "from": "bbox_model",
                "localField": "image_id",
                "foreignField": "image_id",
                "as": "model_info",
            },
        },
        {
            "$lookup": {
                "from": "metadata",
                "localField": "image_id",
                "foreignField": "image_id",
                "as": "metadata_info",
            },
        },
    ]
    data = list(db.bbox_annotation.aggregate(pipeline))
    if not data:
        raise HTTPException(status_code=404, detail="No data found for the provided image_id.")
    return data


@r.get("/analytics/annotations/summary")
async def get_annotations_summary(db: Database = Depends(database.get_db)):
    pipeline = [
        {
            "$project": {
                "bbox_size": {
                    "$subtract": [
                        {"$subtract": ["$bbox.right", "$bbox.left"]},
                        {"$subtract": ["$bbox.bottom", "$bbox.top"]},
                    ],
                },
            },
        },
        {
            "$group": {
                "_id": None,
                "average_bbox_size": {"$avg": "$bbox_size"},
                "total_annotations": {"$sum": 1},
            },
        },
    ]
    summary = list(db.bbox_annotation.aggregate(pipeline))
    if not summary:
        return {"average_bbox_size": 0, "total_annotations": 0}
    return summary[0]


@r.get("/analytics/audits/outcomes_over_time")
async def get_audit_outcomes_over_time(db: Database = Depends(database.get_db)):
    pipeline = [
        {
            "$addFields": {
                "month": {"$month": {"$toDate": "$timestamp"}},
                "year": {"$year": {"$toDate": "$timestamp"}},
            },
        },
        {
            "$group": {
                "_id": {"year": "$year", "month": "$month"},
                "correct_count": {"$sum": {"$cond": ["$bbox_correct", 1, 0]}},
                "incorrect_count": {"$sum": {"$cond": ["$bbox_correct", 0, 1]}},
            },
        },
        {
            "$sort": {"_id.year": 1, "_id.month": 1},
        },
    ]
    results = list(db.bbox_audit.aggregate(pipeline))
    return {"data": results}
