from enum import Enum
from typing import Optional, List, Dict, Any
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

class SortEnum(str, Enum):
    LATEST = "최신순"
    POPULAR = "인기순"
    RANDOM = "랜덤순"

class ApplicationStatusEnum(str, Enum):
    SUBMITTED = "제출됨"
    REVIEWED = "열람됨"
    ACCEPTED = "합격"
    REJECTED = "불합격"

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

class ApplicationCreate(BaseModel):
    post_id: int
    applicant_id: int
    motivation: str
    most_memorable_project: str
    meeting_available_time: List[Dict[str, str]]  # [{"day": "월", "time": "14:00"}, ...]
    aspirations: str

    class Config:
        from_attributes = True

class ApplicationResponse(BaseModel):
    id: int
    post_id: int
    applicant_id: int
    motivation: str
    most_memorable_project: str
    portfolio_pdf_url: str
    meeting_available_time: List[Dict[str, str]]
    aspirations: str
    created_at: datetime
    status: str
    post_title: str  # 공고 제목도 함께 반환
    total_applications: int  # 해당 공고의 총 지원자 수

    class Config:
        from_attributes = True 