from typing import Any, List, Optional

from pydantic import Field, BaseModel


class DocumentBase(BaseModel):
    name: Optional[str] = None
    data: Optional[Any] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(DocumentBase):
    pass


class DocumentInDB(DocumentBase):
    id: str = Field(..., alias="_id")

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    field_name: str
    value: float


class DataResponse(BaseModel):
    field_name: str
    data: List[str]


class ImageDataRequest(BaseModel):
    image_id: str
