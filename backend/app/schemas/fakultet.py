from pydantic import BaseModel

class FakultetBase(BaseModel):
    naziv: str

class FakultetResponse(FakultetBase):
    id: int

    class Config:
        from_attributes = True
