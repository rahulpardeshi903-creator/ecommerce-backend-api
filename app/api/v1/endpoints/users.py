from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_active_user, require_admin
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get the logged-in user's profile."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update the logged-in user's profile."""
    for field, value in update_data.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

# Admin only routes
@router.get("/", response_model=list[UserResponse])
def list_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 50
):
    """[Admin] List all users."""
    return db.query(User).offset(skip).limit(limit).all()

@router.delete("/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """[Admin] Deactivate a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} deactivated"}
