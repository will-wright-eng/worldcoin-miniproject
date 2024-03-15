from typing import Any, Optional

from pydantic import Field, BaseModel


class DocumentBase(BaseModel):
    # Example fields; adjust according to your actual data schema
    name: Optional[str] = None
    data: Optional[Any] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(DocumentBase):
    pass


class DocumentInDB(DocumentBase):
    id: str = Field(..., alias="_id")

    class Config:
        orm_mode = True
