import os
from datetime import datetime, timedelta, timezone
import uuid
import tempfile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.company import Company
from afip_integration.models import AfipToken
from afip_integration.utils.certificate_manager import decrypt_credential

# Dependencias AFIP
from pyafipws.wsaa import WSAA

def get_wsaa_url() -> str:
    env = os.environ.get("AFIP_ENVIRONMENT", "homologacion").lower()
    if env == "produccion":
        return os.environ.get("AFIP_WSAA_URL_PROD", "https://wsaa.afip.gov.ar/ws/services/LoginCms")
    return os.environ.get("AFIP_WSAA_URL_HOMO", "https://wsaahomo.afip.gov.ar/ws/services/LoginCms")

async def get_access_ticket(company_id: uuid.UUID, db: AsyncSession) -> dict:
    # 1. Buscar en caché (DB afip_tokens)
    result = await db.execute(select(AfipToken).where(AfipToken.company_id == company_id))
    token_record = result.scalar_one_or_none()

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None) # Keep naive for DB simplicity or use timezone aware if postgres is setup so. We'll use naive UTC.
    
    # 2. Caché con expiración segura (marginado a 30 min)
    if token_record and token_record.expires_at > (now_utc + timedelta(minutes=30)):
        return {
            "token": token_record.token,
            "sign": token_record.sign,
            "cuit": token_record.cuit
        }

    # 3. Obtener company
    comp_result = await db.execute(select(Company).where(Company.id == company_id))
    company = comp_result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    if not company.afip_cert or not company.afip_key:
        raise HTTPException(status_code=400, detail="Configurar certificados AFIP primero")

    # b. Desencriptar certificados
    cert_content = decrypt_credential(company.afip_cert)
    key_content = decrypt_credential(company.afip_key)
    
    # c/d/e/f Usar pyafipws WSAA
    # pyafipws expects physical files for cert/key. We'll use NamedTemporaryFile
    wsaa = WSAA()
    
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.crt') as f_cert, \
         tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.key') as f_key:
        
        f_cert.write(cert_content)
        f_key.write(key_content)
        cert_path = f_cert.name
        key_path = f_key.name

    try:
        url_wsaa = get_wsaa_url()
        # Generar ticket
        tra = wsaa.CreateTRA("wsfe", ttl=43200) # 12 horas en segundos (43200)
        cms = wsaa.SignTRA(tra, cert_path, key_path)
        wsaa.Conectar(url=url_wsaa)
        wsaa.LoginCMS(cms)
        
        token = wsaa.Token
        sign = wsaa.Sign
        
        # g. Guardar en caché con TTL de 11.5hs (~ UTC now + 11.5)
        # Assuming the generated ticket lasts 12h, we save exact expiration
        expires_at = now_utc + timedelta(hours=11, minutes=30)
        
        if token_record:
            token_record.token = token
            token_record.sign = sign
            token_record.cuit = company.cuit
            token_record.expires_at = expires_at
        else:
            token_record = AfipToken(
                company_id=company_id,
                token=token,
                sign=sign,
                cuit=company.cuit,
                expires_at=expires_at
            )
            db.add(token_record)
            
        await db.commit()
        return {
            "token": token,
            "sign": sign,
            "cuit": company.cuit
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error conectando a AFIP (WSAA): {str(e)}")
    finally:
        # Prevent leak of temp files with sensible data
        if os.path.exists(cert_path): os.remove(cert_path)
        if os.path.exists(key_path): os.remove(key_path)
