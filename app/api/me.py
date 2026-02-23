from fastapi import APIRouter, Depends
from app.schemas.auth import UserOut
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["me"])

@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
