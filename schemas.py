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

class QuestionTypeEnum(str, Enum):
    TEXT_BOX = "TEXT_BOX"
    LINK = "LINK"
    ATTACHMENT = "ATTACHMENT"
    CHOICES = "CHOICES"

class MeetingTime(BaseModel):
    day: str = Field(..., description="요일 (월, 화, 수, 목, 금, 토, 일)")
    time: str = Field(..., description="시간 (HH:MM 형식, 예: 14:00)")

    class Config:
        json_schema_extra = {
            "example": {
                "day": "월",
                "time": "14:00"
            }
        }

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

# 새로운 스키마들
class PostQuestionCreate(BaseModel):
    question_type: QuestionTypeEnum
    question_content: str
    is_required: bool = False
    choices: Optional[List[str]] = None  # CHOICES 타입일 때만 사용

    class Config:
        json_schema_extra = {
            "example": {
                "question_type": "TEXT_BOX",
                "question_content": "가장 기억에 남는 프로젝트는 무엇인가요?",
                "is_required": True
            }
        }

class PostQuestionsRequest(BaseModel):
    questions: List[PostQuestionCreate]

class PostQuestionResponse(BaseModel):
    id: int
    post_id: int
    question_type: str
    question_content: str
    is_required: bool
    choices: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ApplicationAnswerCreate(BaseModel):
    post_question_id: int
    answer_content: str

class ApplicationCreate(BaseModel):
    post_id: int
    applicant_id: int
    answers: List[ApplicationAnswerCreate]

    class Config:
        json_schema_extra = {
            "example": {
                "post_id": 1,
                "applicant_id": 123,
                "answers": [
                    {
                        "post_question_id": 1,
                        "answer_content": "쇼핑몰 프로젝트입니다."
                    }
                ]
            }
        }

class ApplicationResponse(BaseModel):
    id: int
    post_id: int
    applicant_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApplicationAnswerResponse(BaseModel):
    id: int
    application_id: int
    post_question_id: int
    answer_content: str
    created_at: datetime

    class Config:
        from_attributes = True 