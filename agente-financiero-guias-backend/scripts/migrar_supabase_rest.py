"""
Migración GCP → Supabase usando la API REST (PostgREST) de Supabase.
Tablas: debt_installments, commission_recipients, commission_rules, commissions

La conexión directa TCP a Supabase (5432/6543) está bloqueada por firewall de red.
Esta solución usa HTTPS (puerto 443) via la API REST de Supabase que siempre está abierta.

Uso:
    python scripts/migrar_supabase_rest.py --check-only
    python scripts/migrar_supabase_rest.py --create-schema
    python scripts/migrar_supabase_rest.py --migrate
    python scripts/migrar_supabase_rest.py              (todo en orden)
"""

import sys
import json
import psycopg2
import requests
from datetime import datetime, date
from decimal import Decimal

# ══════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════

# Origen: Cloud SQL GCP (conexion directa funciona)
SRC_HOST = "34.39.132.36"
SRC_PORT = 5432
SRC_DB   = "agente_financiero_db"
SRC_USER = "postgres"
SRC_PASS = "FinancialAgent_2026!"

# Destino: Supabase via REST API (no TCP directo)
SUPABASE_URL     = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

# Las 4 tablas en orden de dependencia FK
TABLAS_FALTANTES = [
    "debt_installments",
    "commission_recipients",
    "commission_rules",
    "commissions",
]

# DDL para crear las tablas vía Management API / SQL de Supabase
DDL_SQL = """
-- debt_installments
CREATE TABLE IF NOT EXISTS public.debt_installments (
    id UUID NOT NULL PRIMARY KEY,
    debt_id UUID NOT NULL REFERENCES public.debts(id) ON DELETE CASCADE,
    installment_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    capital_amount NUMERIC(12, 2) NOT NULL,
    interest_amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    transaction_id UUID REFERENCES public.transactions(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- commission_recipients
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recipienttype') THEN
        CREATE TYPE recipienttype AS ENUM ('SUPPLIER', 'EMPLOYEE', 'PARTNER');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.commission_recipients (
    id UUID NOT NULL PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    type recipienttype NOT NULL,
    name VARCHAR(255) NOT NULL,
    cuit VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_commission_recipients_company
    ON public.commission_recipients (company_id, is_active);

-- commission_rules
CREATE TABLE IF NOT EXISTS public.commission_rules (
    id UUID NOT NULL PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    recipient_id UUID NOT NULL REFERENCES public.commission_recipients(id),
    client_id VARCHAR(50),
    service_id VARCHAR(50),
    percentage NUMERIC(5, 2) NOT NULL CHECK (percentage >= 0 AND percentage <= 100),
    priority INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_commission_rule UNIQUE (company_id, recipient_id, client_id, service_id)
);
CREATE INDEX IF NOT EXISTS idx_commission_rules_company
    ON public.commission_rules (company_id, is_active);

-- commissions
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'commissionstatus') THEN
        CREATE TYPE commissionstatus AS ENUM ('PENDING', 'PAID', 'CANCELLED');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.commissions (
    id UUID NOT NULL PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    income_transaction_id UUID NOT NULL REFERENCES public.transactions(id),
    commission_rule_id UUID REFERENCES public.commission_rules(id),
    recipient_id UUID NOT NULL REFERENCES public.commission_recipients(id),
    client_id VARCHAR(50) NOT NULL,
    service_id VARCHAR(50) NOT NULL,
    base_amount NUMERIC(12, 2) NOT NULL,
    commission_amount NUMERIC(12, 2) NOT NULL,
    status commissionstatus NOT NULL DEFAULT 'PENDING',
    payment_transaction_id UUID REFERENCES public.transactions(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_commissions_income ON public.commissions (income_transaction_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON public.commissions (company_id, status);
"""


# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════

def connect_src():
    return psycopg2.connect(
        host=SRC_HOST, port=SRC_PORT, dbname=SRC_DB,
        user=SRC_USER, password=SRC_PASS, connect_timeout=15
    )


def supabase_headers(prefer_upsert=False):
    h = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": "Bearer " + SUPABASE_API_KEY,
        "Content-Type": "application/json",
    }
    if prefer_upsert:
        h["Prefer"] = "resolution=ignore-duplicates,return=minimal"
    return h


def serialize_row(row_dict):
    """Serializa tipos Python a JSON-safe."""
    result = {}
    for k, v in row_dict.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif isinstance(v, date):
            result[k] = v.isoformat()
        elif isinstance(v, Decimal):
            result[k] = float(v)
        else:
            result[k] = v
    return result


def get_tables_supabase():
    """Lista tablas en Supabase via REST."""
    url = SUPABASE_URL + "/rest/v1/"
    r = requests.get(url, headers=supabase_headers(), timeout=15)
    if r.status_code == 200:
        data = r.json()
        # PostgREST devuelve las rutas disponibles
        if "paths" in data:
            return [p.lstrip("/") for p in data["paths"].keys()]
    # Alternativa: consultar via RPC o inspection
    return []


def count_supabase(tabla):
    """Cuenta registros en tabla Supabase."""
    url = "%s/rest/v1/%s?select=id" % (SUPABASE_URL, tabla)
    h = supabase_headers()
    h["Prefer"] = "count=exact"
    h["Range"] = "0-0"
    r = requests.get(url, headers=h, timeout=15)
    if r.status_code in (200, 206):
        content_range = r.headers.get("Content-Range", "")
        if "/" in content_range:
            return int(content_range.split("/")[-1])
    return -1


def count_src(conn, tabla):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM public.%s;" % tabla)
        return cur.fetchone()[0]


def get_columns_src(conn, tabla):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='public' AND table_name=%s
            ORDER BY ordinal_position;
        """, (tabla,))
        return [r[0] for r in cur.fetchall()]


# ══════════════════════════════════════════════
# FASE 2: CREAR SCHEMA (via Supabase SQL API)
# ══════════════════════════════════════════════

def create_schema():
    print("\n=== CREANDO SCHEMA EN SUPABASE ===")
    url = "%s/rest/v1/rpc/exec_sql" % SUPABASE_URL
    
    # Supabase no tiene endpoint SQL nativo en REST para DDL sin service_role key.
    # Pero podemos usar el endpoint de Management API o el SQL editor vía API.
    # Con la publishable key, podemos ejecutar DDL via sql edge function si existe.
    # Alternativa: usar la Supabase Management API.
    
    # Intentar con Management API (requiere service_role, usamos publishable)
    # Nota: el DDL debe ejecutarse desde el dashboard o con service_role key
    print("NOTA: Para crear tablas, se necesita ejecutar el siguiente SQL en el SQL Editor de Supabase:")
    print("Dashboard -> SQL Editor -> New Query -> pegar y ejecutar")
    print("\n" + "=" * 60)
    print(DDL_SQL)
    print("=" * 60)
    
    # Guardar el DDL en un archivo para facilitar la ejecución 
    with open("scripts/supabase_create_tables.sql", "w", encoding="utf-8") as f:
        f.write(DDL_SQL)
    print("\nDDL guardado en: scripts/supabase_create_tables.sql")


# ══════════════════════════════════════════════
# FASE 1: VERIFICACIÓN
# ══════════════════════════════════════════════

def check_tables():
    print("\n=== VERIFICACION DE TABLAS ===")
    
    print("Conectando a Cloud SQL GCP...")
    src = connect_src()
    print("OK - Cloud SQL conectado")
    
    print("Verificando Supabase REST API...")
    r = requests.get(SUPABASE_URL + "/rest/v1/", headers=supabase_headers(), timeout=15)
    print("Supabase HTTP status:", r.status_code)
    
    # Tablas origen
    with src.cursor() as cur:
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='public' AND table_type='BASE TABLE'
            ORDER BY table_name;
        """)
        tablas_src = [r[0] for r in cur.fetchall()]
    
    print("\nTablas en Cloud SQL GCP (%d):" % len(tablas_src))
    for t in tablas_src:
        n = count_src(src, t)
        print("  %s  (%d rows)" % (t, n))
    
    print("\nVerificando tablas faltantes en Supabase:")
    for tabla in TABLAS_FALTANTES:
        n = count_supabase(tabla)
        if n == -1:
            print("  FALTA: %s  (no existe en Supabase)" % tabla)
        else:
            print("  OK:    %s  (%d rows en Supabase)" % (tabla, n))
    
    src.close()


# ══════════════════════════════════════════════
# FASE 3: MIGRAR DATOS
# ══════════════════════════════════════════════

def migrar_tabla(src_conn, tabla):
    print("\n--- Migrando: %s ---" % tabla)
    
    pre_src  = count_src(src_conn, tabla)
    pre_dest = count_supabase(tabla)
    print("  PRE: origen=%d | destino=%d" % (pre_src, pre_dest))
    
    if pre_src == 0:
        print("  Tabla vacia en origen, nada que migrar.")
        return {"tabla": tabla, "origen": 0, "nuevos": 0, "errores": 0}
    
    columnas = get_columns_src(src_conn, tabla)
    cols_sql = ", ".join('"%s"' % c for c in columnas)
    
    url = "%s/rest/v1/%s" % (SUPABASE_URL, tabla)
    h = supabase_headers(prefer_upsert=True)
    
    BATCH = 250
    insertados = 0
    errores = 0
    
    with src_conn.cursor(name="cur_%s" % tabla) as cur:
        cur.execute("SELECT %s FROM public.%s ORDER BY created_at;" % (cols_sql, tabla))
        
        while True:
            rows = cur.fetchmany(BATCH)
            if not rows:
                break
            
            payload = [serialize_row(dict(zip(columnas, row))) for row in rows]
            
            r = requests.post(url, headers=h, data=json.dumps(payload), timeout=60)
            
            if r.status_code in (200, 201):
                insertados += len(rows)
                print("  ... %d/%d" % (insertados, pre_src), end="\r")
            else:
                errores += len(rows)
                print("\n  ERROR batch (%d rows): HTTP %d - %s" % (len(rows), r.status_code, r.text[:200]))
    
    post_dest = count_supabase(tabla)
    nuevos = post_dest - pre_dest if pre_dest >= 0 else insertados
    print("\n  POST: destino=%d | nuevos=%d | errores=%d" % (post_dest, nuevos, errores))
    
    return {"tabla": tabla, "origen": pre_src, "pre_dest": pre_dest, "post_dest": post_dest, "nuevos": nuevos, "errores": errores}


def migrar_datos():
    print("\n=== MIGRACION DE DATOS: GCP -> SUPABASE ===")
    
    # Verificar que las tablas existen en Supabase antes de migrar
    print("Verificando tablas en Supabase...")
    faltantes_sin_datos = []
    for tabla in TABLAS_FALTANTES:
        n = count_supabase(tabla)
        if n == -1:
            faltantes_sin_datos.append(tabla)
    
    if faltantes_sin_datos:
        print("AVISO: Las siguientes tablas aun no existen en Supabase:")
        for t in faltantes_sin_datos:
            print("  - %s" % t)
        print("\nEjecutar primero el DDL en el SQL Editor de Supabase.")
        print("El DDL esta en: scripts/supabase_create_tables.sql")
        print("\nGenerando el DDL ahora...")
        create_schema()
        print("\nPor favor:")
        print("1. Ir a https://supabase.com/dashboard/project/fumejzkghviszmyfjegg/sql/new")
        print("2. Pegar el contenido de scripts/supabase_create_tables.sql")
        print("3. Ejecutar")
        print("4. Volver a correr: python scripts/migrar_supabase_rest.py --migrate")
        return
    
    src = connect_src()
    inicio = datetime.now()
    resultados = []
    
    for tabla in TABLAS_FALTANTES:
        r = migrar_tabla(src, tabla)
        resultados.append(r)
    
    src.close()
    duracion = (datetime.now() - inicio).total_seconds()
    
    print("\n" + "=" * 70)
    print("REPORTE FINAL")
    print("=" * 70)
    print("%-30s %8s %10s %10s %8s %8s" % ("Tabla", "Origen", "Pre-Dest", "Post-Dest", "Nuevos", "Errores"))
    print("-" * 70)
    total_nuevos = 0
    for r in resultados:
        print("%-30s %8d %10d %10d %8d %8d" % (
            r["tabla"], r["origen"], r.get("pre_dest", 0),
            r.get("post_dest", 0), r.get("nuevos", 0), r.get("errores", 0)
        ))
        total_nuevos += r.get("nuevos", 0)
    print("-" * 70)
    print("Duracion: %.1fs | Total nuevos: %d" % (duracion, total_nuevos))


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

def main():
    args = sys.argv[1:]
    check_only    = "--check-only"    in args
    create_s      = "--create-schema" in args
    migrate       = "--migrate"       in args
    do_all        = not (check_only or create_s or migrate)
    
    print("=" * 60)
    print("MIGRACION CLOUD SQL (GCP) -> SUPABASE via REST")
    print("Fecha: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Tablas: %s" % ", ".join(TABLAS_FALTANTES))
    print("=" * 60)
    
    if check_only:
        check_tables()
        return
    
    if create_s or do_all:
        check_tables()
        create_schema()
    
    if migrate or do_all:
        migrar_datos()


if __name__ == "__main__":
    main()
