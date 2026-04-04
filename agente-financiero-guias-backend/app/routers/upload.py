from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.storage_service import storage_service

router = APIRouter(
    prefix="/upload",
    tags=["Uploads"]
)

@router.post("", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    # Validate file type (allowing more than just images for invoices/receipts)
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no permitido: {file.content_type}. Solo se permiten imágenes y PDFs."
        )
    
    try:
        url = await storage_service.upload(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {str(e)}")
    
    return {"url": url}
