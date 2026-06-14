from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, username: str, password_hash: str, email: str | None = None) -> User:
        user = User(username=username, password_hash=password_hash, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
