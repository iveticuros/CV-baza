from pydantic import BaseModel

class StudentBase(BaseModel):
    ime: str
    prezime: str

class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True
