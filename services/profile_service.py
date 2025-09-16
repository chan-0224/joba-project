from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import User, ProfileCareer, Application, Post
import json


def update_profile(db: Session, user: User, track: str, school: str, portfolio_url: str, careers: str, avatar_url: str = None, cover_url: str = None):
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