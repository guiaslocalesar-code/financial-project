import os
from datetime import datetime, date
from pyafipws.wsfev1 import WSFEv1
from fastapi import HTTPException
from app.utils.enums import FiscalCondition

def get_wsfe_url() -> str:
    env = os.environ.get("AFIP_ENVIRONMENT", "homologacion").lower()
    if env == "produccion":
        return os.environ.get("AFIP_WSFE_URL_PROD", "https://servicios1.afip.gov.ar/wsfev1/service.asmx")
    return os.environ.get("AFIP_WSFE_URL_HOMO", "https://wswhomo.afip.gov.ar/wsfev1/service.asmx")

def _init_wsfe(ta: dict) -> WSFEv1:
    wsfe = WSFEv1()
    wsfe.Token = ta["token"]
    wsfe.Sign = ta["sign"]
    wsfe.Cuit = ta["cuit"]
    wsfe.Conectar(url=get_wsfe_url())
    return wsfe

def get_last_invoice_number(ta: dict, point_of_sale: int, cbte_tipo: int) -> int:
    try:
        wsfe = _init_wsfe(ta)
        last_number = wsfe.CompUltimoAutorizado(cbte_tipo, point_of_sale)
        if last_number == "" or last_number is None:
            # First ever invoice
            return 1
        return int(last_number) + 1
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AFIP (UltimoAutorizado) no disponible, intente nuevamente. Error: {str(e)}")

def authorize_invoice(ta: dict, invoice_data: dict) -> dict:
    """
    invoice_data contiene:
      - cbte_tipo
      - point_of_sale
      - client_doc_tipo (80 o 96)
      - client_doc_nro
      - cbte_desde (próximo numero calculado)
      - issue_date, due_date
      - total, subtotal, iva_amount
      - iva_aplica, iva_rate
      - exchange_rate
    """
    try:
        wsfe = _init_wsfe(ta)
        
        cbte_tipo = invoice_data["cbte_tipo"]
        pto_vta = invoice_data["point_of_sale"]
        proximo_numero = invoice_data["cbte_desde"]
        
        fecha_cbte = invoice_data["issue_date"].strftime("%Y%m%d")
        
        # Format concept dates representing whole month (as per requirement: Concept=2 services)
        fch_serv_desde = invoice_data["issue_date"].replace(day=1).strftime("%Y%m%d")
        
        # Find last day of the month by going to day 1 next month, subtracting 1 day
        next_month = invoice_data["issue_date"].replace(day=28) + datetime.timedelta(days=4)
        ultimo_dia = next_month - datetime.timedelta(days=next_month.day)
        fch_serv_hasta = ultimo_dia.strftime("%Y%m%d")
        
        fch_vto_pago = invoice_data["due_date"].strftime("%Y%m%d") if invoice_data.get("due_date") else (invoice_data["issue_date"] + datetime.timedelta(days=30)).strftime("%Y%m%d")

        wsfe.CrearFactura(
            concepto=2, # Servicios
            tipo_doc=invoice_data["client_doc_tipo"],
            nro_doc=invoice_data["client_doc_nro"],
            tipo_cbte=cbte_tipo,
            punto_vta=pto_vta,
            cbt_desde=proximo_numero,
            cbt_hasta=proximo_numero,
            imp_total=float(invoice_data["total"]),
            imp_tot_conc=0.0, # Not untaxed
            imp_neto=float(invoice_data["subtotal"]),
            imp_iva=float(invoice_data["iva_amount"]) if invoice_data["iva_aplica"] else 0.0,
            imp_trib=0.0,
            imp_op_ex=0.0, # No exempt
            fecha_cbte=fecha_cbte,
            fecha_venc_pago=fch_vto_pago,
            fecha_serv_desde=fch_serv_desde,
            fecha_serv_hasta=fch_serv_hasta,
            moneda_id="PES",
            moneda_ctz=float(invoice_data.get("exchange_rate", 1.0))
        )
        
        # Add IVA breakdown if applicable
        if invoice_data["iva_aplica"] and invoice_data["iva_amount"] > 0:
            iva_id = 5 # 21%
            if invoice_data["iva_rate"] == 10.5:
                iva_id = 4
            elif invoice_data["iva_rate"] == 0:
                iva_id = 3
                
            wsfe.AgregarIva(
                iva_id=iva_id,
                base_imp=float(invoice_data["subtotal"]),
                importe=float(invoice_data["iva_amount"])
            )
            
        wsfe.CAESolicitar()
        
        # Check Result
        if wsfe.Resultado == "A":
            raw_dict = {}
            if hasattr(wsfe, "xml_response"):
               raw_dict["xml_response"] = str(wsfe.xml_response) 
                 
            return {
                "cae": wsfe.CAE,
                "cae_expiry": wsfe.Vencimiento, # typically YYYYMMDD
                "invoice_number": f"{pto_vta:04d}-{proximo_numero:08d}",
                "raw_response": {"Status": "A", "Reproceso": wsfe.Reproceso, "Xml": raw_dict.get("xml_response")}
            }
        else:
            # Rejected or Partial
            msg = wsfe.Observaciones if hasattr(wsfe, "Observaciones") and wsfe.Observaciones else wsfe.ErrMsg
            raise HTTPException(status_code=422, detail=f"Rechazado por AFIP: {msg}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AFIP no disponible, intente nuevamente. Error: {str(e)}")
