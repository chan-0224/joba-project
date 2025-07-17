from pydantic import BaseModel

class UserBase(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    password: str
    name: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    name: str
    class Config:
        orm_mode = True 