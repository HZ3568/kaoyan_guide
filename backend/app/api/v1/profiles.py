from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.goal import Goal
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.profile import OnboardingRequest, OnboardingResponse, UserProfileOut, UserProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=UserProfileOut)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise NotFoundError("User profile not found")
    return profile


@router.put("/me", response_model=UserProfileOut)
def upsert_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/onboarding", response_model=OnboardingResponse)
def onboarding(
    payload: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    for key, value in payload.profile.model_dump().items():
        setattr(profile, key, value)
    goal = None
    if payload.goal:
        goal = Goal(user_id=current_user.id, **payload.goal.model_dump())
        db.add(goal)
    db.commit()
    db.refresh(profile)
    if goal:
        db.refresh(goal)
    return OnboardingResponse(profile=profile, goal=goal)
