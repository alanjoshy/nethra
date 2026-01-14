@router.post("/login")
async def login(data: LoginRequest, db: Session):
    user = await get_user_by_email(db, data.email)

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id, user.role)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


