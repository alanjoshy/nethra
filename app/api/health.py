from sys import prefix
from fastapi import APIRouter 


router = APIRouter(prefix="/health", tags=["Health"]) 

@router.get("/", status_code=200)
async def health_check() -> dict[str, str]:
    return {"status": "ok"} 

