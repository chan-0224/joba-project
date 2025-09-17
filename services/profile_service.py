from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import User, ProfileCareer, Application, Post
import json


def update_profile(db: Session, user: User, track: str, school: str, portfolio_url: str, careers: str, avatar_url: str = None, cover_url: str = None):
    """
    사용자 프로필 정보를 업데이트합니다.
    
    - 트랙, 학교, 포트폴리오 링크, 프로필 사진/커버 이미지를 수정할 수 있습니다.
    - careers(JSON 문자열)를 전달하면 기존 경력을 수정/추가/삭제 처리합니다.

    Args:
        db (Session): 데이터베이스 세션
        user (User): 업데이트 대상 사용자 객체
        track (str): 트랙 정보
        school (str): 학교 정보
        portfolio_url (str): 포트폴리오 URL
        careers (str): JSON 문자열 형태의 경력 데이터
        avatar_url (str, optional): 아바타 이미지 URL
        cover_url (str, optional): 커버 이미지 URL

    Returns:
        User: 업데이트된 사용자 객체

    Raises:
        HTTPException: careers JSON이 잘못된 경우 (ValueError 발생 시 상위에서 처리 필요)
    """
    if track is not None:
        user.track = track
    if school is not None:
        user.school = school
    if portfolio_url is not None:
        user.portfolio_url = portfolio_url
    if avatar_url is not None:
        user.avatar_url = avatar_url
    if cover_url is not None:
        user.cover_url = cover_url


    if careers:
        careers_data = json.loads(careers)
        existing_careers = {c.id: c for c in user.careers}
        incoming_ids = {c.get("id") for c in careers_data if c.get("id")}


        for c in careers_data:
            if c.get("id") and c.get("id") in existing_careers:
                career = existing_careers[c["id"]]
                career.year = c["year"]
                career.description = c["description"]
            else:
                new_career = ProfileCareer(user_id=user.id, year=c["year"], description=c["description"])
                db.add(new_career)


        for career_id, career in existing_careers.items():
            if career_id not in incoming_ids:
                db.delete(career)


    db.commit()
    db.refresh(user)
    return user


def get_recent_projects(db: Session, social_user_id: str):
    """
    사용자가 '합격' 처리된 최근 프로젝트 2개를 조회합니다.
    
    Application 테이블에서 해당 user_id가 '합격' 상태인 지원 내역을 조회하여, 연결된 Post 정보를 반환합니다.

    Args:
        db (Session): 데이터베이스 세션
        social_user_id (str): 소셜 기반 user_id (예: kakao_12345)

    Returns:
        list[dict]: 최근 프로젝트 목록
            - id: 프로젝트 ID
            - title: 프로젝트 제목
            - image_url: 대표 이미지 URL
    """
    results = (
        db.query(Post)
        .join(Application, Application.post_id == Post.id)
        .filter(
            Application.user_id == social_user_id,
            Application.status == "합격"
        )
        .order_by(Application.__table__.c.created_at.desc())
        .limit(2)
        .all()
    )


    return [
        {"id": post.id, "title": post.title, "image_url": post.image_url}
        for post in results
    ]