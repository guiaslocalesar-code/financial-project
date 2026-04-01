# Módulo de Facturación Electrónica (AFIP)

## 1. Descripción del Módulo
Este módulo permite la emisión, visualización y anulación (en estado borrador) de comprobantes electrónicos a través del **WebService de AFIP (WSFEv1)**. Todo el flujo de obtención de *Ticket de Acceso (WSAA)* e interacciones SOAP subyacentes se han abstraído de la lógica central de la aplicación.

## 2. Prerrequisitos
- La empresa debe poseer una Clave Privada `.key`/`.pem` y un Certificado Digital `.crt` validado por AFIP.
- La empresa debe tener dado de alta un **Punto de Venta Web Service** habilitado para Factura Electrónica.
- Credenciales en `.env` correctamente seteadas.

## 3. Configuración Inicial
### a. Generar clave Fernet y agregar a `.env`
Ejecutar por única vez via Python:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```
Añadir el output en tu archivo `.env` bajo la clave `AFIP_FERNET_KEY`. Y validar tener el entorno:
```bash
AFIP_ENVIRONMENT=homologacion
AFIP_FERNET_KEY="<TU_CLAVE_AQUI>"
```

### b. Subir certificado y configurar Pto. Venta
Subir los certificados y registrar el punto de venta usando el endpoint: `POST /api/v1/companies/{id}/afip-credentials`
- `cert_file`: Archivo con extensión `.crt`
- `key_file`: Archivo con extensión `.key` o `.pem`
- `point_of_sale`: Ej `1` o `2`

### c. Homologación
Por defecto, la variable `AFIP_ENVIRONMENT=homologacion` apunta el módulo a los endoints de prueba de la AFIP. Una vez funcional, se pasa a prodcucón modificando la variable de entorno a `produccion` y actualizando el `.crt`.

## 4. Flujo de Emisión
El flujo general de emisión consiste en:
1. **Borrdor (`draft`)**: Crear borrador vía `POST /invoices` con los ítems de venta. Se calcula el desglose del subtotal/IVA al vuelo usando `invoice_type_resolver`.
2. **Autorización (`emitted`)**: Llamar a `POST /invoices/{id}/emit`. Se valida el caché del Tra (WSAA Ticket). Se obtiene el próximo comprobante válido y se postea a AFIP. 
   - La respuesta exitosa devuelve un CAE con su respectivo vencimiento y el status pasa a `emitted`.

## 5. Tabla de Errores Comunes de AFIP
| Error | Descripción y Solución |
|---|---|
| **Certificado Invalido** | El `.crt` expiró, fue revocado por AFIP o la clave `.key` no pertenece al mismo. |
| **Fecha Comprobante** | AFIP no admite una fecha de comprobante previa a la del último emitido. Asegurarse de que `issue_date` de tu sistema coordine. |
| **DocTipo Inexistente (Error 10004)** | El CUIT/DNI provisto del cliente no está empadronado en AFIP o la Condición Fiscal asociada no es correcta. |
| **Pto Venta no Habilitado** | En AFIP, el pto de venta debe indicar sistema `"WebService"`, de lo contrario WSFEv1 rechaza autorizar. |

## 6. Producción
Para cambiar a producción:
1. Modificar tu `.env`: `AFIP_ENVIRONMENT=produccion`.
2. Descargar y delegar desde el CUIT el entorno real, volviendo a asociar certificado de producción mediante el endpoint de setup.
3. Asegurarse de utilizar CAEs de validez legal.
