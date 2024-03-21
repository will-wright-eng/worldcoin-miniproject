from typing import Dict, List

from fastapi import HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import CollectionInvalid
from pymongo.collection import Collection

from app.db import database

collections = {
    "bbox_annotation": "bbox.annotation.json",
    "bbox_audit": "bbox.audit.json",
    "bbox_model": "bbox.model.json",
    "image_metadata": "metadata.json",
}


class BaseCRUD:
    def __init__(self, db: MongoClient, collection_name: str):
        self.db = db
        self.collection_name = collection_name
        self.collection: Collection = self.db[collection_name]

    def create_collection(self) -> bool:
        """Create a new collection if it doesn't exist."""
        try:
            self.db.create_collection(self.collection_name)
            self.collection = self.db[self.collection_name]
            return True
        except CollectionInvalid:
            return False

    def create(self, data: Dict) -> str:
        """Create a new document in the collection."""
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def read(self, document_id: str) -> Dict:
        """Read a document from the collection."""
        document = self.collection.find_one({"_id": ObjectId(document_id)})
        if document:
            document["_id"] = str(document["_id"])
        return document

    def update(self, document_id: str, data: Dict) -> bool:
        """Update a document in the collection."""
        result = self.collection.update_one({"_id": ObjectId(document_id)}, {"$set": data})
        return result.modified_count > 0

    def delete(self, document_id: str) -> bool:
        """Delete a document from the collection."""
        result = self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0

    def list(self, skip: int = 0, limit: int = 10) -> List[Dict]:
        """List documents in the collection."""
        documents = self.collection.find().skip(skip).limit(limit)
        return [{**document, "_id": str(document["_id"])} for document in documents]

    def list_annotated(self, skip: int = 0, limit: int = 10) -> List[Dict]:
        documents = self.collection.find({"annotated": {"$ne": "null"}}).skip(skip).limit(limit)
        # documents = self.collection.find({"annotated": {"$ne": None}}).skip(skip).limit(limit)
        return [{**document, "_id": str(document["_id"])} for document in documents]

    def list_image_ids(self) -> List[str]:
        """List unique image_ids in the collection."""
        documents = self.collection.find({}, {"image_id": 1, "_id": 0})
        return [doc["image_id"] for doc in documents]

    def find_by_image_id(self, image_id: str) -> List[Dict]:
        """Find documents matching a specific image_id."""
        documents = self.collection.find({"image_id": image_id})
        return [{**document, "_id": str(document["_id"])} for document in documents]

    def get_doc_count(self) -> int:
        """Get the number of documents in the collection."""
        return self.collection.count_documents({})


class BBoxAnnotationCRUD(BaseCRUD):
    def __init__(self, db: MongoClient):
        super().__init__(db, "bbox_annotation")


class BBoxAuditCRUD(BaseCRUD):
    def __init__(self, db: MongoClient):
        super().__init__(db, "bbox_audit")


class BBoxModelCRUD(BaseCRUD):
    def __init__(self, db: MongoClient):
        super().__init__(db, "bbox_model")


class ImageMetadataCRUD(BaseCRUD):
    def __init__(self, db: MongoClient):
        super().__init__(db, "image_metadata")


crud_classes = {
    "bbox_annotation": BBoxAnnotationCRUD,
    "bbox_audit": BBoxAuditCRUD,
    "bbox_model": BBoxModelCRUD,
    "image_metadata": ImageMetadataCRUD,
}


def get_crud_class(collection_name: str):
    crud_class = crud_classes.get(collection_name)
    if not crud_class:
        raise HTTPException(status_code=400, detail=f"Collection '{collection_name}' is not supported.")
    db = database.get_db()
    return crud_class(db)
