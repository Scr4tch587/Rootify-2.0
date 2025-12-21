from pydantic import BaseModel

class ArtistCreate(BaseModel):
    name: str

class ArtistOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}