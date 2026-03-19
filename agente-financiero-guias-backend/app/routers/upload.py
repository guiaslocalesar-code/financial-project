from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from typing import List

from app.services.storage_service import storage_service

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

@router.post("", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")
    
    try:
        url = await storage_service.upload(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {str(e)}")
    
    return {"url": url}
