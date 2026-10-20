from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=30)
    password: constr(min_length=6)
