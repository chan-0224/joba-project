from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class PostCreate(BaseModel):
    user_id: int
    title: str = Field(..., max_length=255)
    description: str
    recruitment_field: str = Field(..., max_length=50)
    recruitment_headcount: str = Field(..., max_length=50)
    school_specific: bool
    target_school_name: Optional[str] = Field(None, max_length=100)
    deadline: datetime
    external_link: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: int
    user_id: int
    image_url: str
    title: str
    description: str
    recruitment_field: str
    recruitment_headcount: str
    school_specific: bool
    target_school_name: Optional[str]
    deadline: datetime
    external_link: Optional[str]
    created_at: datetime
    updated_at: datetime
    views: int

    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    total_count: int
    posts: List[PostResponse] 