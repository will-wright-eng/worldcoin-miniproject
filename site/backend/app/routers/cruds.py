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
