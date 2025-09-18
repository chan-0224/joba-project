"""
커스터마이징 질문 관리 API 엔드포인트

이 모듈은 공고별 커스터마이징 질문 생성 및 조회 기능을 제공합니다.
공고 작성자만 질문을 설정할 수 있습니다.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db, Post, PostQuestion, User
from schemas import PostQuestionsRequest, PostQuestionResponse, PostQuestionCreate
from routers.auth import get_current_user
from services.user_service import get_user_id_from_user
from sqlalchemy import and_

router = APIRouter()


@router.post("/posts/{post_id}/questions", status_code=201)
async def create_post_questions(
    post_id: int,
    questions_request: PostQuestionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    공고에 대한 커스터마이징 질문들을 생성합니다.
    
    **JWT 인증 필요** - 공고 작성자만 질문 설정 가능
    
    Args:
        post_id: 질문을 설정할 공고 ID
        questions_request: 생성할 질문 목록 (PostQuestionsRequest)
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션
        
    Returns:
        dict: 생성된 질문 개수
        - message: 성공 메시지
        - questions_count: 생성된 질문 개수
        
    Raises:
        HTTPException: 
            - 404: 공고를 찾을 수 없음
            - 403: 권한 없음 (공고 작성자가 아님)
            - 400: CHOICES 타입 질문에 선택지 없음
    
    Note:
        - **덮어쓰기 방식**: 기존 질문 모두 삭제 후 새로 생성
        - 권한 검증: post.user_id == get_user_id_from_user(current_user)
        - CHOICES 타입 질문은 반드시 choices 필드 필요
        - 질문 타입: TEXT, TEXTAREA, CHOICES, ATTACHMENT 지원
    """
    # 1. 공고 존재 여부 확인
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공고를 찾을 수 없습니다."
        )
    
    # 2. 권한 검증 - 공고 작성자만 질문 설정 가능
    if post.user_id != get_user_id_from_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="공고 작성자만 질문을 설정할 수 있습니다."
        )
    
    # 3. 기존 질문들 삭제 (덮어쓰기 방식)
    db.query(PostQuestion).filter(PostQuestion.post_id == post_id).delete()
    
    # 4. 새로운 질문들 생성
    created_questions = []
    for question_data in questions_request.questions:
        # CHOICES 타입일 때 choices 필드 검증
        if question_data.question_type == "CHOICES":
            if not question_data.choices or len(question_data.choices) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CHOICES 타입 질문에는 선택지가 필요합니다."
                )
        
        # 질문 생성
        question = PostQuestion(
            post_id=post_id,
            question_type=question_data.question_type,
            question_content=question_data.question_content,
            is_required=question_data.is_required,
            choices=question_data.choices
        )
        db.add(question)
        created_questions.append(question)
    
    db.commit()
    
    # 5. 생성된 질문들의 ID를 설정
    for question in created_questions:
        db.refresh(question)
    
    return {"message": f"{len(created_questions)}개의 질문이 성공적으로 생성되었습니다."}


@router.get("/posts/{post_id}/questions", response_model=List[PostQuestionResponse])
async def get_post_questions(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    공고의 질문 목록을 조회합니다.
    
    **인증 불필요** - 모든 사용자가 공고의 질문 목록을 조회할 수 있음
    
    Args:
        post_id: 조회할 공고 ID
        db: 데이터베이스 세션
        
    Returns:
        List[PostQuestionResponse]: 질문 목록
        - 질문 ID, 타입, 내용, 필수 여부, 선택지 등 포함
        - 생성 순서대로 정렬 (created_at 기준)
        
    Raises:
        HTTPException: 
            - 404: 공고를 찾을 수 없음
    
    Note:
        - 지원서 작성 시 필요한 질문 정보 제공
        - 공고 존재 여부만 확인, 권한 검증 없음
        - CHOICES 타입 질문의 경우 choices 필드 포함
    """
    # 1. 공고 존재 여부 확인
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공고를 찾을 수 없습니다."
        )
    
    # 2. 질문 목록 조회 (생성 순서대로)
    questions = db.query(PostQuestion).filter(
        PostQuestion.post_id == post_id
    ).order_by(PostQuestion.created_at).all()
    
    return questions 