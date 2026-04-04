"""
Migración de las 4 tablas faltantes: Cloud SQL (GCP) → Supabase
Tablas: debt_installments, commission_recipients, commission_rules, commissions

Uso:
    python scripts/migrar_supabase_4tablas.py [--check-only] [--create-schema] [--migrate]

Flags:
    --check-only    Solo verifica qué tablas existen en cada BD
    --create-schema Crea el schema (DDL) de las 4 tablas en Supabase si faltan
    --migrate       Migra los datos de las 4 tablas
    (sin flags)     Hace todo: create-schema + migrate
"""

import sys
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from datetime import datetime

# ══════════════════════════════════════════════
# CONFIGURACIÓN DE CONEXIONES
# ══════════════════════════════════════════════

# Origen: Cloud SQL (GCP)  ← IP tomada del .env real del proyecto
SRC_HOST = "34.39.132.36"
SRC_PORT = 5432
SRC_DB   = "agente_financiero_db"
SRC_USER = "postgres"
SRC_PASS = "FinancialAgent_2026!"

# Destino: Supabase (directo, no pooler para migraciones)
DEST_HOST = "db.fumejzkghviszmyfjegg.supabase.co"
DEST_PORT = 5432
DEST_DB   = "postgres"
DEST_USER = "postgres"
DEST_PASS = "GuiasSA2020@"

# Las 4 tablas faltantes en orden de dependencia (FKs primero)
TABLAS_FALTANTES = [
    "debt_installments",
    "commission_recipients",
    "commission_rules",
    "commissions",
]

# ══════════════════════════════════════════════
# DDL PARA CREAR LAS TABLAS EN SUPABASE
# Extraído exactamente de los alembic migrations
# ══════════════════════════════════════════════

DDL_TABLAS = {
    "debt_installments": """
        CREATE TABLE IF NOT EXISTS public.debt_installments (
            id UUID NOT NULL,
            debt_id UUID NOT NULL,
            installment_number INTEGER NOT NULL,
            due_date DATE NOT NULL,
            amount NUMERIC(12, 2) NOT NULL,
            capital_amount NUMERIC(12, 2) NOT NULL,
            interest_amount NUMERIC(12, 2) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            transaction_id UUID,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            PRIMARY KEY (id),
            FOREIGN KEY (debt_id) REFERENCES public.debts(id) ON DELETE CASCADE,
            FOREIGN KEY (transaction_id) REFERENCES public.transactions(id) ON DELETE SET NULL
        );
    """,
    "commission_recipients": """
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recipienttype') THEN
                CREATE TYPE recipienttype AS ENUM ('SUPPLIER', 'EMPLOYEE', 'PARTNER');
            END IF;
        END $$;

        CREATE TABLE IF NOT EXISTS public.commission_recipients (
            id UUID NOT NULL,
            company_id UUID NOT NULL,
            type recipienttype NOT NULL,
            name VARCHAR(255) NOT NULL,
            cuit VARCHAR(20),
            email VARCHAR(255),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            PRIMARY KEY (id),
            FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_commission_recipients_company
            ON public.commission_recipients (company_id, is_active);
    """,
    "commission_rules": """
        CREATE TABLE IF NOT EXISTS public.commission_rules (
            id UUID NOT NULL,
            company_id UUID NOT NULL,
            recipient_id UUID NOT NULL,
            client_id VARCHAR(50),
            service_id VARCHAR(50),
            percentage NUMERIC(5, 2) NOT NULL,
            priority INTEGER NOT NULL DEFAULT 1,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            PRIMARY KEY (id),
            UNIQUE (company_id, recipient_id, client_id, service_id),
            CONSTRAINT chk_percentage CHECK (percentage >= 0 AND percentage <= 100),
            FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE,
            FOREIGN KEY (recipient_id) REFERENCES public.commission_recipients(id)
        );
        CREATE INDEX IF NOT EXISTS idx_commission_rules_company
            ON public.commission_rules (company_id, is_active);
    """,
    "commissions": """
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'commissionstatus') THEN
                CREATE TYPE commissionstatus AS ENUM ('PENDING', 'PAID', 'CANCELLED');
            END IF;
        END $$;

        CREATE TABLE IF NOT EXISTS public.commissions (
            id UUID NOT NULL,
            company_id UUID NOT NULL,
            income_transaction_id UUID NOT NULL,
            commission_rule_id UUID,
            recipient_id UUID NOT NULL,
            client_id VARCHAR(50) NOT NULL,
            service_id VARCHAR(50) NOT NULL,
            base_amount NUMERIC(12, 2) NOT NULL,
            commission_amount NUMERIC(12, 2) NOT NULL,
            status commissionstatus NOT NULL DEFAULT 'PENDING',
            payment_transaction_id UUID,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            PRIMARY KEY (id),
            FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE,
            FOREIGN KEY (income_transaction_id) REFERENCES public.transactions(id),
            FOREIGN KEY (commission_rule_id) REFERENCES public.commission_rules(id),
            FOREIGN KEY (recipient_id) REFERENCES public.commission_recipients(id),
            FOREIGN KEY (payment_transaction_id) REFERENCES public.transactions(id) ON DELETE SET NULL
        );
        CREATE INDEX IF NOT EXISTS idx_commissions_income
            ON public.commissions (income_transaction_id);
        CREATE INDEX IF NOT EXISTS idx_commissions_status
            ON public.commissions (company_id, status);
    """,
}


# ══════════════════════════════════════════════
# FUNCIONES DE CONEXIÓN
# ══════════════════════════════════════════════

def connect_src():
    """Conectar a Cloud SQL (origen)."""
    return psycopg2.connect(
        host=SRC_HOST, port=SRC_PORT, dbname=SRC_DB,
        user=SRC_USER, password=SRC_PASS, connect_timeout=15,
        sslmode="require"
    )


def connect_dest():
    """Conectar a Supabase (destino)."""
    return psycopg2.connect(
        host=DEST_HOST, port=DEST_PORT, dbname=DEST_DB,
        user=DEST_USER, password=DEST_PASS, connect_timeout=15,
        sslmode="require"
    )


def get_tables(conn) -> list[str]:
    """Retorna lista de tablas en schema public."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        return [r[0] for r in cur.fetchall()]


def get_count(conn, tabla: str) -> int:
    """Cuenta registros en una tabla."""
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM public.{tabla};")
            return cur.fetchone()[0]
    except Exception:
        return -1


# ══════════════════════════════════════════════
# FASE 1: VERIFICACIÓN
# ══════════════════════════════════════════════

def check_tables():
    print("\n" + "═" * 60)
    print("🔍 VERIFICACIÓN DE TABLAS")
    print("═" * 60)

    print("\n📡 Conectando a Cloud SQL (GCP)...")
    src = connect_src()
    print("✅ Conectado a Cloud SQL")

    print("\n📡 Conectando a Supabase...")
    dest = connect_dest()
    print("✅ Conectado a Supabase")

    tablas_src  = get_tables(src)
    tablas_dest = get_tables(dest)

    print(f"\n📊 Tablas en Cloud SQL (origen):  {len(tablas_src)}")
    for t in sorted(tablas_src):
        print(f"   {'✅' if t in tablas_dest else '❌'} {t}")

    print(f"\n📊 Tablas en Supabase (destino): {len(tablas_dest)}")
    for t in sorted(tablas_dest):
        marker = "✅" if t in tablas_src else "➕ (extra)"
        print(f"   {marker} {t}")

    faltantes = [t for t in tablas_src if t not in tablas_dest]
    print(f"\n🔴 Tablas faltantes en Supabase: {len(faltantes)}")
    for t in faltantes:
        src_count = get_count(src, t)
        print(f"   ❌ {t}  ({src_count} rows en origen)")

    src.close()
    dest.close()

    print("\n" + "═" * 60)
    return faltantes


# ══════════════════════════════════════════════
# FASE 2: CREAR SCHEMA EN SUPABASE
# ══════════════════════════════════════════════

def create_schema_supabase():
    print("\n" + "═" * 60)
    print("🏗️  CREANDO SCHEMA DE LAS 4 TABLAS EN SUPABASE")
    print("═" * 60)

    dest = connect_dest()
    tablas_existentes = get_tables(dest)

    for tabla in TABLAS_FALTANTES:
        if tabla in tablas_existentes:
            print(f"  ⏭️  {tabla} ya existe en Supabase, omitiendo.")
            continue
        print(f"\n  🔨 Creando tabla: {tabla}...")
        ddl = DDL_TABLAS.get(tabla)
        if not ddl:
            print(f"  ⚠️  No hay DDL definido para {tabla}")
            continue
        try:
            with dest.cursor() as cur:
                # Ejecutar DDL por bloques separados por ;
                for statement in ddl.split(";"):
                    stmt = statement.strip()
                    if stmt:
                        cur.execute(stmt)
            dest.commit()
            print(f"  ✅ {tabla} creada correctamente")
        except Exception as e:
            dest.rollback()
            print(f"  ❌ Error creando {tabla}: {e}")
            raise

    dest.close()
    print("\n✅ Schema creado en Supabase")


# ══════════════════════════════════════════════
# FASE 3: MIGRAR DATOS
# ══════════════════════════════════════════════

def migrar_tabla(src_conn, dest_conn, tabla: str) -> dict:
    """Migra todos los datos de una tabla de src → dest (idempotente)."""
    print(f"\n  📦 Migrando: {tabla}")

    # PRE-conteos
    pre_src  = get_count(src_conn, tabla)
    pre_dest = get_count(dest_conn, tabla)
    print(f"     PRE  → origen: {pre_src} | destino: {pre_dest}")

    if pre_src == 0:
        print(f"     ℹ️  Tabla vacía en origen, nada que migrar.")
        return {"tabla": tabla, "origen": 0, "migrados": 0, "errores": 0}

    # Obtener columnas de la tabla en el origen
    with src_conn.cursor() as cur:
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (tabla,))
        columnas = [r[0] for r in cur.fetchall()]

    cols_sql = ", ".join(f'"{c}"' for c in columnas)
    placeholders = ", ".join(["%s"] * len(columnas))
    insert_sql = f"""
        INSERT INTO public.{tabla} ({cols_sql})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING;
    """

    # Leer todos los datos del origen
    with src_conn.cursor(name=f"cursor_{tabla}") as cur:
        cur.execute(f"SELECT {cols_sql} FROM public.{tabla};")
        migrados = 0
        errores = 0
        BATCH_SIZE = 500

        while True:
            rows = cur.fetchmany(BATCH_SIZE)
            if not rows:
                break
            try:
                with dest_conn.cursor() as dest_cur:
                    dest_cur.executemany(insert_sql, rows)
                dest_conn.commit()
                migrados += len(rows)
                print(f"     ... {migrados}/{pre_src} registros", end="\r")
            except Exception as e:
                dest_conn.rollback()
                errores += len(rows)
                print(f"\n     ⚠️  Error en batch: {e}")

    # POST-conteo
    post_dest = get_count(dest_conn, tabla)
    nuevos = post_dest - pre_dest
    print(f"\n     POST → destino: {post_dest} | nuevos: {nuevos} | errores: {errores}")

    return {
        "tabla": tabla,
        "origen": pre_src,
        "pre_dest": pre_dest,
        "post_dest": post_dest,
        "nuevos": nuevos,
        "errores": errores,
    }


def migrar_datos():
    print("\n" + "═" * 60)
    print("🚀 MIGRACIÓN DE DATOS: GCP → SUPABASE")
    print("═" * 60)

    print("\n📡 Conectando a ambas bases de datos...")
    src  = connect_src()
    dest = connect_dest()
    print("✅ Conexiones establecidas")

    # Verificar que las tablas existen en destino
    tablas_dest = get_tables(dest)
    for t in TABLAS_FALTANTES:
        if t not in tablas_dest:
            print(f"❌ Tabla {t} no existe en Supabase. Ejecutá primero --create-schema")
            sys.exit(1)

    resultados = []
    inicio = datetime.now()

    for tabla in TABLAS_FALTANTES:
        resultado = migrar_tabla(src, dest, tabla)
        resultados.append(resultado)

    src.close()
    dest.close()

    duracion = (datetime.now() - inicio).total_seconds()

    # ─── Reporte Final ───
    print("\n" + "═" * 60)
    print("📋 REPORTE FINAL")
    print("═" * 60)
    print(f"\n{'Tabla':<30} {'Origen':>8} {'Pre-Dest':>10} {'Post-Dest':>10} {'Nuevos':>8} {'Errores':>8}")
    print("-" * 76)
    total_nuevos = 0
    for r in resultados:
        print(f"{r['tabla']:<30} {r['origen']:>8} {r.get('pre_dest', 0):>10} {r.get('post_dest', 0):>10} {r.get('nuevos', 0):>8} {r.get('errores', 0):>8}")
        total_nuevos += r.get("nuevos", 0)
    print("-" * 76)
    print(f"\n✅ Migración completada en {duracion:.1f}s | {total_nuevos} registros nuevos insertados")

    return resultados


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

def main():
    args = sys.argv[1:]

    check_only    = "--check-only"    in args
    create_schema = "--create-schema" in args
    migrate       = "--migrate"       in args
    do_all        = not (check_only or create_schema or migrate)

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  MIGRACIÓN CLOUD SQL (GCP) → SUPABASE                   ║")
    print("║  Proyecto: Agente Financiero Guías                       ║")
    print(f"║  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                         ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("\nTablas a migrar:", ", ".join(TABLAS_FALTANTES))

    if check_only:
        check_tables()
        return

    if create_schema or do_all:
        check_tables()
        create_schema_supabase()

    if migrate or do_all:
        migrar_datos()


if __name__ == "__main__":
    main()
