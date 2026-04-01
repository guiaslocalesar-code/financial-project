"""
Script de prueba directa contra AFIP Homologación.
Usa openssl de Git + zeep para SOAP.
"""
import os
import sys
import datetime
import base64
import subprocess
import tempfile
import warnings

warnings.filterwarnings("ignore")
sys.path.append(os.path.dirname(__file__))

from lxml import etree
from zeep import Client as ZeepClient

# === CONFIGURACIÓN ===
CERT_PATH = "C:/tmp_afip/cert.crt"
KEY_PATH = "C:/tmp_afip/cert.key"
CUIT_EMISOR = "20324947702"
CUIT_RECEPTOR = "20407404212"
PUNTO_VENTA = 1
MONTO = 10.00
OPENSSL = r"C:\Program Files\Git\usr\bin\openssl.exe"

WSAA_URL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL"
WSFE_URL = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"

def create_tra():
    now = datetime.datetime.now(datetime.timezone.utc)
    gen_time = (now - datetime.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S-00:00")
    exp_time = (now + datetime.timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%S-00:00")
    tra = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<loginTicketRequest version="1.0">'
        '<header>'
        f'<uniqueId>{int(now.timestamp())}</uniqueId>'
        f'<generationTime>{gen_time}</generationTime>'
        f'<expirationTime>{exp_time}</expirationTime>'
        '</header>'
        '<service>wsfe</service>'
        '</loginTicketRequest>'
    )
    return tra

def sign_tra_openssl(tra_xml: str) -> str:
    """Firma TRA con openssl smime (CMS/PKCS7)"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml', mode='w') as f:
        f.write(tra_xml)
        tra_path = f.name
    
    try:
        # Git openssl needs forward slashes
        cert_unix = CERT_PATH.replace("\\", "/")
        key_unix = KEY_PATH.replace("\\", "/")
        tra_unix = tra_path.replace("\\", "/")
        
        result = subprocess.run(
            [OPENSSL, "smime", "-sign",
             "-signer", cert_unix,
             "-inkey", key_unix,
             "-outform", "DER",
             "-nodetach",
             "-in", tra_unix],
            capture_output=True
        )
        if result.returncode != 0:
            raise Exception(f"openssl error: {result.stderr.decode()}")
        
        return base64.b64encode(result.stdout).decode('utf-8')
    finally:
        os.unlink(tra_path)

def main():
    print("=" * 60)
    print("  PRUEBA FACTURA AFIP — HOMOLOGACIÓN")
    print("=" * 60)
    
    # === PASO 1: Obtener Token ===
    print("\n[1/4] Autenticando con WSAA...")
    tra = create_tra()
    cms = sign_tra_openssl(tra)
    
    client_wsaa = ZeepClient(WSAA_URL)
    response = client_wsaa.service.loginCms(cms)
    
    root = etree.fromstring(response.encode('utf-8'))
    token = root.find('.//token').text
    sign = root.find('.//sign').text
    print("   ✅ Token obtenido exitosamente")
    
    # === PASO 2: Conectar WSFE ===
    print("\n[2/4] Conectando a WSFEv1...")
    wsfe = ZeepClient(WSFE_URL)
    auth = {'Token': token, 'Sign': sign, 'Cuit': int(CUIT_EMISOR)}
    
    # === PASO 3: Último comprobante ===
    print("\n[3/4] Consultando último comprobante...")
    cbte_tipo = 11  # Factura C
    
    last_resp = wsfe.service.FECompUltimoAutorizado(Auth=auth, PtoVta=PUNTO_VENTA, CbteTipo=cbte_tipo)
    ultimo = last_resp.CbteNro
    proximo = (ultimo or 0) + 1
    print(f"   Último autorizado: {ultimo}")
    print(f"   Próximo a emitir: {proximo}")
    
    # === PASO 4: Solicitar CAE ===
    print("\n[4/4] Solicitando CAE a AFIP...")
    
    hoy = datetime.date.today()
    fecha_cbte = hoy.strftime("%Y%m%d")
    primer_dia = hoy.replace(day=1).strftime("%Y%m%d")
    if hoy.month == 12:
        ultimo_dia_mes = hoy.replace(day=31)
    else:
        ultimo_dia_mes = hoy.replace(month=hoy.month + 1, day=1) - datetime.timedelta(days=1)
    fecha_hasta = ultimo_dia_mes.strftime("%Y%m%d")
    fecha_vto = (hoy + datetime.timedelta(days=30)).strftime("%Y%m%d")

    req = {
        'FeCabReq': {
            'CantReg': 1,
            'PtoVta': PUNTO_VENTA,
            'CbteTipo': cbte_tipo,
        },
        'FeDetReq': {
            'FECAEDetRequest': [{
                'Concepto': 2,
                'DocTipo': 80,
                'DocNro': int(CUIT_RECEPTOR),
                'CbteDesde': proximo,
                'CbteHasta': proximo,
                'CbteFch': fecha_cbte,
                'ImpTotal': MONTO,
                'ImpTotConc': 0.0,
                'ImpNeto': MONTO,
                'ImpOpEx': 0.0,
                'ImpIVA': 0.0,
                'ImpTrib': 0.0,
                'FchServDesde': primer_dia,
                'FchServHasta': fecha_hasta,
                'FchVtoPago': fecha_vto,
                'MonId': 'PES',
                'MonCotiz': 1.0,
            }]
        }
    }
    
    result = wsfe.service.FECAESolicitar(Auth=auth, **req)
    det = result.FeDetResp.FECAEDetResponse[0]
    
    print("\n" + "=" * 60)
    if det.Resultado == "A":
        nro = f"{PUNTO_VENTA:04d}-{proximo:08d}"
        print("  ✅ ¡FACTURA AUTORIZADA POR AFIP!")
        print(f"  Tipo:        Factura C (Monotributo)")
        print(f"  Número:      {nro}")
        print(f"  CAE:         {det.CAE}")
        print(f"  Vto CAE:     {det.CAEFchVto}")
        print(f"  Total:       ${MONTO}")
        print(f"  CUIT Emisor: {CUIT_EMISOR}")
        print(f"  CUIT Recep:  {CUIT_RECEPTOR}")
        print(f"  Fecha:       {hoy}")
    else:
        print("  ❌ FACTURA RECHAZADA POR AFIP")
        print(f"  Resultado: {det.Resultado}")
        if det.Observaciones:
            for obs in det.Observaciones.Obs:
                print(f"  Obs [{obs.Code}]: {obs.Msg}")
    
    if result.Errors:
        for err in result.Errors.Err:
            print(f"  Error [{err.Code}]: {err.Msg}")
    print("=" * 60)

if __name__ == "__main__":
    main()
