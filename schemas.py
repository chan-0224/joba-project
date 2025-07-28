from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class RecruitmentFieldEnum(str, Enum):
    FRONTEND = "프론트엔드"
    BACKEND = "백엔드"
    PLANNING = "기획"
    DESIGN = "디자인"
    DATA_ANALYSIS = "데이터 분석"

class RecruitmentHeadcountEnum(str, Enum):
    ONE_TO_TWO = "1~2인"
    THREE_TO_FIVE = "3~5인"
    SIX_TO_TEN = "6~10인"
    UNSPECIFIED = "인원미정"

class PostCreate(BaseModel):
    user_id: int
    title: str = Field(..., max_length=255)
    description: str
    recruitment_field: RecruitmentFieldEnum
    recruitment_headcount: RecruitmentHeadcountEnum
    school_specific: bool
    target_school_name: Optional[str] = Field(None, max_length=100)
    deadline: datetime
    external_link: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True
        use_enum_values = True

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

class PostOptionsResponse(BaseModel):
    recruitment_fields: List[str]
    recruitment_headcounts: List[str] 