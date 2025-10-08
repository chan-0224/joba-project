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
    ACCEPTED = "합격"
    REJECTED = "불합격"
    CANCELLED = "취소됨"

class ApplicationSortEnum(str, Enum):
    CREATED_AT_DESC = "최신순"
    CREATED_AT_ASC = "오래된순"
    STATUS = "상태순"

class QuestionTypeEnum(str, Enum):
    TEXT = "TEXT"
    TEXTAREA = "TEXTAREA"
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
    user_id: str
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
    application_count: int = 0  # 지원자 수
    recruited_count: int = 0  # 모집된 인원 수 (합격자)
    recruitment_status: str = "모집중"  # 모집 상태

    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    total_count: int
    posts: List[PostResponse]


# 새로운 스키마들
class PostQuestionCreate(BaseModel):
    question_type: QuestionTypeEnum
    question_content: str
    is_required: bool = False
    choices: Optional[List[str]] = None  # CHOICES 타입일 때만 사용

    class Config:
        json_schema_extra = {
            "example": {
                "question_type": "TEXT",
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
    answers: List[ApplicationAnswerCreate]

    class Config:
        json_schema_extra = {
            "example": {
                "post_id": 1,
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
    user_id: str
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

# 지원자 관리 기능을 위한 새로운 스키마들
class ApplicationListItem(BaseModel):
    application_id: int
    user_id: str
    applicant_name: str
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True

class ApplicationListResponse(BaseModel):
    total_count: int
    applications: List[ApplicationListItem]
    page: int
    size: int

class ApplicationDetailResponse(BaseModel):
    application_id: int
    user_id: str
    applicant_name: str
    status: str
    submitted_at: datetime
    questions: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class ApplicationStatusUpdate(BaseModel):
    new_status: ApplicationStatusEnum

    class Config:
        json_schema_extra = {
            "example": {
                "new_status": "합격"
            }
        }

class ApplicationStatusResponse(BaseModel):
    application_id: int
    status: str
    updated_at: datetime

    class Config:
        from_attributes = True

# ----- Profile 관련 스키마 -----
class RecentProjectResponse(BaseModel):  # 최근 프로젝트
    id: int
    title: str
    image_url: str

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):  # 프로필 조회 응답
    user_id: str
    email: str
    name: Optional[str] = None
    field: Optional[str] = None
    university: Optional[str] = None
    portfolio: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    timetable_url: Optional[str] = None
    careers: Dict[str, List[dict]]
    recent_projects: List[RecentProjectResponse]

    class Config:
        from_attributes = True

    
# 공지 목록에서 사용할 간단 응답
class NoticeListItem(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True

# 공지 상세 응답
class NoticeDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: str  # "YYYY-MM-DD" 형식의 문자열

    class Config:
        orm_mode = True


# ----- 내가 작성한 공고 목록 (/my/posts) -----

class MyPostItem(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    recruitment_headcount: str
    deadline: str
    application_count: int

    class Config:
        from_attributes = True


class MyPostFieldGroup(BaseModel):
    field: str
    posts: List[MyPostItem]


class MyPostSummary(BaseModel):
    ongoing_count: int
    closed_count: int


class PostListMyResponse(BaseModel):
    summary: MyPostSummary
    ongoing: List[MyPostFieldGroup]
    closed: List[MyPostFieldGroup]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "summary": {
                    "ongoing_count": 2,
                    "closed_count": 1
                },
                "ongoing": [
                    {
                        "field": "프론트엔드",
                        "posts": [
                            {
                                "id": 1,
                                "title": "AI 웹 서비스 팀원 모집",
                                "description": "프론트엔드와 백엔드 협업 가능한 분을 찾습니다.",
                                "image_url": "https://storage.googleapis.com/posts/ai_front.png",
                                "recruitment_headcount": "3~5인",
                                "deadline": "2025-10-30",
                                "application_count": 4
                            }
                        ]
                    },
                    {
                        "field": "백엔드",
                        "posts": [
                            {
                                "id": 2,
                                "title": "클라우드 백엔드 팀원 모집",
                                "description": "FastAPI 및 PostgreSQL 기반 서비스 개발",
                                "image_url": "https://storage.googleapis.com/posts/backend_team.png",
                                "recruitment_headcount": "1~2인",
                                "deadline": "2025-11-02",
                                "application_count": 3
                            }
                        ]
                    }
                ],
                "closed": [
                    {
                        "field": "디자인",
                        "posts": [
                            {
                                "id": 3,
                                "title": "UX/UI 디자인 공모전 팀원 모집",
                                "description": "Figma 사용 가능자, 협업 경험 우대",
                                "image_url": "https://storage.googleapis.com/posts/design_team.png",
                                "recruitment_headcount": "1~2인",
                                "deadline": "2025-09-10",
                                "application_count": 7
                            }
                        ]
                    }
                ]
            }
        }

# ----- 내가 지원한 공고 목록 (/my/applications) -----
class MyApplicationPost(BaseModel):
    post_id: int
    title: str
    description: str
    image_url: str
    recruitment_field: str
    recruitment_headcount: str
    deadline: str
    recruitment_status: str
    application_count: int

class MyApplicationItem(BaseModel):
    application_id: int
    status: str
    submitted_at: str
    post: MyApplicationPost

class MyApplicationListResponse(BaseModel):
    applications: List[MyApplicationItem]