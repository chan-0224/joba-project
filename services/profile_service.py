from sqlalchemy.orm import Session
from database import User, ProfileCareer, Application, Post
import json
from fastapi import HTTPException


def update_profile(db: Session, user: User, name: str, field: str, university: str, portfolio: str, careers: str, avatar_url: str = None, banner_url: str = None):
    """
    사용자 프로필 정보를 업데이트합니다.
    - 닉네임, 트랙, 학교, 포트폴리오 링크, 프로필 사진/커버 이미지를 수정할 수 있습니다.
    - careers(JSON 문자열)를 전달하면 해당 유저의 기존 경력은 모두 삭제되고, 새로 전달된 데이터로 전체 교체됩니다.

    Args:
        db (Session): 데이터베이스 세션
        user (User): 업데이트 대상 사용자 객체
        name (str): 닉네임
        field (str): 트랙 정보
        university (str): 학교 정보
        portfolio (str): 포트폴리오 URL
        careers (str): JSON 문자열 형태의 경력 데이터 (dict 또는 list 허용)
        avatar_url (str, optional): 아바타 이미지 URL
        banner_url (str, optional): 배너 이미지 URL

    Returns:
        User: 업데이트된 사용자 객체

    Raises:
        HTTPException: careers JSON이 잘못된 경우 또는 DB 오류 발생 시
    """
    try:
        with db.begin():
            if name is not None:
                user.name = name
            if field is not None:
                user.field = field
            if university is not None:
                user.university = university
            if portfolio is not None:
                user.portfolio = portfolio
            if avatar_url is not None:
                user.avatar_url = avatar_url
            if banner_url is not None:
                user.banner_url = banner_url


            if careers:
                try:
                    careers_data = json.loads(careers)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid careers JSON")
                normalized = []

                # dict → list 변환 (프론트는 연도별 object 구조로 보냄)
                if isinstance(careers_data, dict):
                    for year, items in careers_data.items():
                        for item in items:
                            normalized.append({
                                "year": int(year),
                                "description": item.get("description")
                            })
                elif isinstance(careers_data, list):
                    normalized = careers_data
                else:
                    raise HTTPException(status_code=400, detail="Invalid careers format")
                db.query(ProfileCareer).filter(ProfileCareer.user_id == user.user_id).delete()

                for c in normalized:
                    new_career = ProfileCareer(
                        user_id=user.user_id,
                        year=c["year"],
                        description=c["description"]
                    )
                    db.add(new_career)

        # commit 이후 user 갱신
        db.refresh(user)
        return user

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

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
