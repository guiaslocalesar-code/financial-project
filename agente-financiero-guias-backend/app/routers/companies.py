from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_company, require_role
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from fastapi import File, UploadFile
from sqlalchemy.orm import Session
from uuid import uuid4
from pathlib import Path
from google.cloud import storage
from app.config import settings

# Initialize GCS client
storage_client = storage.Client()

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_in: CompanyCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Check if CUIT already exists
    result = await db.execute(select(Company).where(Company.cuit == company_in.cuit))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Company with this CUIT already exists")
    
    company = Company(**company_in.model_dump())
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID, 
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_company)
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID, 
    company_in: CompanyUpdate, 
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner", "admin"]))
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = company_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    await db.commit()
    await db.refresh(company)
    return company

@router.patch("/{company_id}/imagen")
async def upload_company_imagen(
    company_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_role(["owner", "admin"]))
):
    # Validaciones
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
    MAX_SIZE_MB = 2
    
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Formato no permitido. Usar JPG, PNG o WEBP")
    
    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Imagen demasiado grande. Máximo {MAX_SIZE_MB}MB")
    
    # Guardar en Google Cloud Storage (GCS)
    filename = f"companies/{company_id}/logo_{uuid4().hex}{Path(file.filename).suffix}"
    
    try:
        blob = storage_client.bucket(settings.GCS_BUCKET_NAME).blob(filename)
        blob.upload_from_string(contents, content_type=file.content_type)
        blob.make_public()
        public_url = blob.public_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir a GCS: {str(e)}")
    
    # Guardar URL en DB
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company no encontrada")
    
    company.imagen = public_url
    await db.commit()
    
    return { "imagen": public_url }
