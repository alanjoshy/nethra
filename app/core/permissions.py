from fastapi import Depends, HTTPException
from app.core.dependencies import get_current_user

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user
 

 