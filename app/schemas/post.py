from pydantic import BaseModel, EmailStr, constr


class PostCreateRequest(BaseModel):
    title: str
    slug: str
    content: int


class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: int
    created_at: str
    updated_at: str
