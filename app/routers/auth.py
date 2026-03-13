from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.auth import login_or_create_user
from app.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Autenticación"])

class GoogleLogin(BaseModel):
    google_token: str

@router.post("/google")
async def google_login(data: GoogleLogin, db: AsyncSession = Depends(get_db)):
    result = await login_or_create_user(data.google_token, db)
    if not result:
        raise HTTPException(status_code=401, detail="Token de Google inválido")
    return result

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "avatar_url": current_user.avatar_url
    }

@router.post("/logout")
async def logout():
    # En JWT el logout usualmente se maneja en el cliente (borrando el token)
    return {"message": "Sesión cerrada correctamente"}
