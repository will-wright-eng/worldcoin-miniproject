# dead code

## additional endpoints

### analytics

`main.py`

```python
from app.routers.analytics import analytics_router

app.include_router(
    analytics_router,
    prefix="/v1",
    tags=["analytics"],
)
```

`analytics.py`

```python
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
```

### crud endpoints

`main.py`

```python
from app.routers.cruds import crud_router

app.include_router(
    crud_router,
    prefix="/v1",
    tags=["crud"],
)
```

`cruds.py`

```python
from fastapi import Depends, APIRouter, HTTPException

from app.db import crud, database
from app.core import log, schema

crud_router = r = APIRouter(
    prefix="/crud",
)

logger = log.get_logger(__name__)


@r.post("/{collection_name}", response_model=schema.DocumentInDB, status_code=201)
def create_document(
    collection_name: str,
    document: schema.DocumentCreate,
    crud_class=Depends(crud.get_crud_class),
    db=Depends(database.get_db),
):
    document_id = crud_class(db).create(document.dict())
    return {"id": document_id, **document.dict()}


@r.get("/{collection_name}/{document_id}", response_model=schema.DocumentInDB)
def read_document(
    collection_name: str,
    document_id: str,
    crud_class=Depends(crud.get_crud_class),
    db=Depends(database.get_db),
):
    document = crud_class(db).read(document_id)
    if document:
        return schema.DocumentInDB(**document)
    else:
        raise HTTPException(status_code=404, detail="Document not found.")


@r.put("/{collection_name}/{document_id}", response_model=schema.DocumentInDB)
def update_document(
    collection_name: str,
    document_id: str,
    document: schema.DocumentUpdate,
    crud_class=Depends(crud.get_crud_class),
    db=Depends(database.get_db),
):
    success = crud_class(db).update(document_id, document.dict())
    if success:
        return {**document.dict(), "id": document_id}
    else:
        raise HTTPException(status_code=404, detail="Document not found or update failed.")


@r.delete("/{collection_name}/{document_id}", status_code=204)
def delete_document(
    collection_name: str,
    document_id: str,
    crud_class=Depends(crud.get_crud_class),
    db=Depends(database.get_db),
):
    success = crud_class(db).delete(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")

```

## additional image ops

`image.js`

```js
document.getElementById('saveAnnotation').addEventListener('click', function() {
    // Assuming you have a function to gather annotation data from the canvas
    const annotationData = getAnnotationData(); // Implement this function based on your app's logic

    // Example of calling a backend service to save annotation data
    fetch('/api/annotations/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(annotationData),
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to save annotation');
    })
    .then(data => {
        console.log('Annotation saved:', data);
        // Update status message or UI accordingly
    })
    .catch(error => console.error('Error saving annotation:', error));
});

document.getElementById('loadImage').addEventListener('click', function() {
    // Example of calling a backend service to get an image URL or image data
    fetch('/api/images/random')
    .then(response => response.json())
    .then(data => {
        // Use fabric.js or another method to load the image onto the canvas
        console.log('Image data:', data);
    })
    .catch(error => console.error('Error loading image:', error));
});
```
