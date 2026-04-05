from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID, uuid4
from pathlib import Path
from app.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["Companies"])


# ── List all companies ───────────────────────────────────────────────────────
@router.get("", response_model=list[CompanyResponse])
async def list_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company))
    companies = result.scalars().all()
    return companies


# ── Create a company ─────────────────────────────────────────────────────────
@router.post("", response_model=CompanyResponse)
async def create_company(
    company_in: CompanyCreate,
    db: AsyncSession = Depends(get_db),
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


# ── Get a single company ─────────────────────────────────────────────────────
@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


# ── Update a company ─────────────────────────────────────────────────────────
@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_in: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
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


# ── Upload company logo ──────────────────────────────────────────────────────
@router.patch("/{company_id}/imagen")
async def upload_company_imagen(
    company_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
    MAX_SIZE_MB = 2

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Formato no permitido. Usar JPG, PNG o WEBP")

    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Imagen demasiado grande. Máximo {MAX_SIZE_MB}MB")

    # Try GCS upload, fallback to local static
    filename = f"companies/{company_id}/logo_{uuid4().hex}{Path(file.filename).suffix}"

    try:
        from google.cloud import storage as gcs
        from app.config import settings as cfg
        client = gcs.Client()
        blob = client.bucket(cfg.GCS_BUCKET_NAME).blob(filename)
        blob.upload_from_string(contents, content_type=file.content_type)
        blob.make_public()
        public_url = blob.public_url
    except Exception:
        # Fallback: save locally in /static/uploads/
        local_dir = Path("static/uploads/companies") / str(company_id)
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = local_dir / f"logo{Path(file.filename).suffix}"
        local_path.write_bytes(contents)
        public_url = f"/static/uploads/companies/{company_id}/{local_path.name}"

    # Save URL in DB
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company no encontrada")

    company.imagen = public_url
    await db.commit()

    return {"imagen": public_url}
