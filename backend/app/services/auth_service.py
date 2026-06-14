from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserLogin, UserRegister


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def register(self, payload: UserRegister):
        if self.users.get_by_username(payload.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        return self.users.create(
            username=payload.username,
            email=str(payload.email) if payload.email else None,
            password_hash=get_password_hash(payload.password),
        )

    def login(self, payload: UserLogin) -> str:
        user = self.users.get_by_username(payload.username)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        return create_access_token(user.id)
