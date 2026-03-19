import os
import uuid
from typing import Optional, Protocol
from fastapi import UploadFile
from app.config import settings

# Conditional import to avoid error if supabase is not installed yet
try:
    from supabase import create_client, Client
except ImportError:
    Client = None

class StorageProvider(Protocol):
    async def upload_file(self, file: UploadFile, folder: str = "uploads") -> str:
        ...

class LocalStorageProvider:
    def __init__(self, base_dir: str = "static"):
        self.base_dir = base_dir
        os.makedirs(os.path.join(self.base_dir, "uploads"), exist_ok=True)

    async def upload_file(self, file: UploadFile, folder: str = "uploads") -> str:
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        relative_path = os.path.join(folder, filename)
        full_path = os.path.join(self.base_dir, relative_path)
        
        # Ensure subdirectory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Read content
        content = await file.read()
        with open(full_path, "wb") as buffer:
            buffer.write(content)
            
        return f"/static/{relative_path.replace(os.sep, '/')}"

class SupabaseStorageProvider:
    def __init__(self, url: str, key: str, bucket: str):
        if Client is None:
            raise ImportError("supabase library is not installed")
        self.client: Client = create_client(url, key)
        self.bucket = bucket

    async def upload_file(self, file: UploadFile, folder: str = "uploads") -> str:
        ext = os.path.splitext(file.filename)[1]
        filename = f"{folder}/{uuid.uuid4()}{ext}"
        
        content = await file.read()
        
        # Upload to Supabase Storage
        self.client.storage.from_(self.bucket).upload(
            path=filename,
            file=content,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        url = self.client.storage.from_(self.bucket).get_public_url(filename)
        return url

class StorageService:
    def __init__(self):
        if settings.STORAGE_BACKEND == "supabase" and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            self.provider: StorageProvider = SupabaseStorageProvider(
                settings.SUPABASE_URL, 
                settings.SUPABASE_KEY, 
                settings.SUPABASE_BUCKET
            )
        else:
            self.provider: StorageProvider = LocalStorageProvider()

    async def upload(self, file: UploadFile, folder: str = "uploads") -> str:
        return await self.provider.upload_file(file, folder)

storage_service = StorageService()
