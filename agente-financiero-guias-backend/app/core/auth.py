import httpx
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from app.models.user import User, UserCompany
from app.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import select

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

async def get_google_user_info(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            return None
        return response.json()

def create_jwt_token(user_id: str, companies: list) -> str:
    payload = {
        "sub": user_id,
        "companies": companies,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def login_or_create_user(google_token: str, db) -> Optional[dict]:
    # 1. Obtener info de Google
    google_user = await get_google_user_info(google_token)
    if not google_user:
        return None

    # 2. Buscar o crear user
    # Note: Using select() for async session compatibility if needed, but the original request used db.query
    # Given the project uses AsyncSession, I should use select().
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == google_user["email"]))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            permissions={"google_id": google_user["id"]},
            email=google_user["email"],
            name=google_user.get("name"),
            avatar_url=google_user.get("picture")
        )
        db.add(user)
    else:
        user.last_login = datetime.utcnow()
        user.avatar_url = google_user.get("picture")
    
    await db.commit()
    await db.refresh(user)

    # 3. Obtener empresas del usuario
    res_companies = await db.execute(
        select(UserCompany).where(
            UserCompany.user_id == user.id,
            UserCompany.is_active == True
        )
    )
    user_companies = res_companies.scalars().all()

    companies_payload = [
        {
            "company_id": str(uc.company_id),
            "role": uc.role,
            "quotaparte": float(uc.quotaparte)
        }
        for uc in user_companies
    ]

    # 4. Generar JWT propio
    token = create_jwt_token(str(user.id), companies_payload)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "companies": companies_payload
        }
    }
