from app.api.deps import get_current_user

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return user
