from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db, Post, PostQuestion, User
from schemas import PostQuestionsRequest, PostQuestionResponse, PostQuestionCreate
from routers.auth import get_current_user
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
    공고에 대한 커스터마이징 질문들을 생성합니다. (공고 작성자만 가능)
    """
    # 공고가 존재하는지 확인
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공고를 찾을 수 없습니다."
        )
    
    # 공고 작성자인지 확인
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="공고 작성자만 질문을 설정할 수 있습니다."
        )
    
    # 기존 질문들 삭제 (덮어쓰기 방식)
    db.query(PostQuestion).filter(PostQuestion.post_id == post_id).delete()
    
    # 새로운 질문들 생성
    created_questions = []
    for question_data in questions_request.questions:
        # CHOICES 타입일 때 choices 필드 검증
        if question_data.question_type == "CHOICES":
            if not question_data.choices or len(question_data.choices) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CHOICES 타입 질문에는 선택지가 필요합니다."
                )
        
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
    
    # 생성된 질문들의 ID를 설정
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
    """
    # 공고가 존재하는지 확인
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공고를 찾을 수 없습니다."
        )
    
    # 질문 목록 조회 (생성 순서대로)
    questions = db.query(PostQuestion).filter(
        PostQuestion.post_id == post_id
    ).order_by(PostQuestion.created_at).all()
    
    return questions 