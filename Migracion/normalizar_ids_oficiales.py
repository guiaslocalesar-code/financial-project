"""
normalizar_ids_oficiales.py
============================
Reescribe los UUIDs aleatorios de la migración con los IDs oficiales del sistema:
  - services.id  → IDs numéricos  (ej: '45311', '45413')
  - clients.id   → IDs tipo cX    (ej: 'c2', 'c3')
  - Todas las foreign keys dependientes en todas las tablas

REQUISITOS:
  - pg_dump disponible en PATH (para el backup)
  - psycopg2-binary instalado
  - .env configurado con DATABASE_URL

EJECUCIÓN (desde la raíz del proyecto):
  python -m Migracion.normalizar_ids_oficiales

IDEMPOTENCIA:
  Si los IDs ya fueron normalizados (services.id no tiene formato UUID),
  el script lo detecta y termina sin hacer cambios.
"""

import os
import re
import sys
import subprocess
from datetime import datetime
from urllib.parse import urlparse

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from psycopg2 import sql
from dotenv import load_dotenv

# ── Config ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

CSV_SERVICIOS = os.path.join(BASE_DIR, "csvs para reemplazar ids", "FLUJO DE DINERO NEW - Servicios.csv")
CSV_CLIENTES  = os.path.join(BASE_DIR, "csvs para reemplazar ids", "FLUJO DE DINERO NEW - manual de marca finanzas.csv")
BACKUP_DIR    = os.path.join(BASE_DIR, "Migracion")

# UUID pattern for idempotence check
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

# ── DB Helpers ──────────────────────────────────────────────────────────────────

def parse_db_url(url: str) -> dict:
    """Convert SQLAlchemy async URL to psycopg2 connect kwargs."""
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    p = urlparse(url)
    return {
        "host":     p.hostname,
        "port":     p.port or 5432,
        "dbname":   p.path.lstrip("/"),
        "user":     p.username,
        "password": p.password,
    }


def get_connection():
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        sys.exit("❌ DATABASE_URL no encontrado en .env")
    params = parse_db_url(db_url)
    return psycopg2.connect(**params)


# ── PASO 0: Backup ──────────────────────────────────────────────────────────────

def hacer_backup(conn_params: dict) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(BACKUP_DIR, f"backup_datos_{timestamp}")
    print(f"\n📦 PASO 0: Backup → {backup_folder}")

    os.makedirs(backup_folder, exist_ok=True)
    
    db_url = os.getenv("DATABASE_URL")
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_url)
    
    tables = [
        "services", "clients", "client_services", 
        "income_budgets", "transactions", "invoices", "invoice_items",
        "companies", "expense_types", "expense_categories", "expense_budgets"
    ]
    
    for table in tables:
        try:
            df = pd.read_sql_table(table, engine)
            df.to_csv(os.path.join(backup_folder, f"{table}.csv"), index=False)
            print(f"    ✅ Tabla {table} respaldada ({len(df)} rows)")
        except Exception as e:
            print(f"    ❌ Error respaldando {table}: {e}")
            if "not found" not in str(e).lower(): # Si es un error real de conexión o permisos, paramos
                sys.exit(f"Abortando por error en backup: {e}")

    print(f"  ✅ Backup de datos completado en: {backup_folder}")
    return backup_folder


# ── PASO 1: Leer CSVs y construir mapas ─────────────────────────────────────────

def leer_csvs():
    print("\n📂 PASO 1: Leyendo CSVs...")

    # --- Servicios ---
    df_servicios = pd.read_csv(CSV_SERVICIOS)
    # Normalizar nombres de columnas
    df_servicios.columns = df_servicios.columns.str.strip()
    df_servicios["Id Servicio"] = df_servicios["Id Servicio"].astype(str).str.strip()
    df_servicios["Nombre"]      = df_servicios["Nombre"].astype(str).str.strip()
    df_servicios["Descripcion"] = df_servicios["Descripcion"].fillna("").astype(str).str.strip()

    # service_name → (id_oficial, descripcion)
    # Si hay nombres duplicados en el CSV (ej: "Tik Tok" aparece dos veces),
    # usamos el primero (mayor Id Servicio numérico es el nuevo; el más antiguo tiene más historial).
    # Primero priorizamos los numéricos puro sobre los alfanuméricos.
    df_servicios["es_numerico"] = df_servicios["Id Servicio"].str.match(r'^\d+$')
    df_servicios = df_servicios.sort_values("es_numerico", ascending=False)
    servicios_map = {}  # nombre → (id_oficial, descripcion)
    for _, row in df_servicios.iterrows():
        nombre = row["Nombre"]
        if nombre not in servicios_map:
            servicios_map[nombre] = (row["Id Servicio"], row["Descripcion"])

    print(f"  → {len(servicios_map)} servicios únicos en CSV")

    # --- Clientes (solo Activos) ---
    df_clientes = pd.read_csv(CSV_CLIENTES)
    df_clientes.columns = df_clientes.columns.str.strip()
    df_clientes["ID_Empresa"] = df_clientes["ID_Empresa"].astype(str).str.strip().str.lower()  # c2, c3...
    df_clientes["Empresa"]    = df_clientes["Empresa"].astype(str).str.strip()
    df_clientes["Estado"]     = df_clientes["Estado"].astype(str).str.strip()
    df_clientes["CUIT"]       = df_clientes["CUIT"].fillna("").astype(str).str.strip()
    df_clientes["Servicio"]   = df_clientes["Servicio"].fillna("").astype(str)

    df_activos = df_clientes[df_clientes["Estado"].str.lower() == "activo"].copy()
    df_todos   = df_clientes.copy()  # para mapear también los inactivos (están en la BD con datos)

    print(f"  → {len(df_activos)} clientes ACTIVOS | {len(df_todos)} total en CSV")

    # Construir mapa nombre→(id_oficial, cuit, servicios)
    clientes_map = {}  # nombre → (id_oficial, cuit, [service_ids])
    for _, row in df_todos.iterrows():
        nombre = row["Empresa"]
        id_oficial = row["ID_Empresa"]
        cuit = row["CUIT"] if row["CUIT"] else None

        # Parsear lista de servicios
        servicios_str = row["Servicio"]
        service_ids = []
        if servicios_str.strip():
            for s in re.split(r"[,\s]+", servicios_str):
                s = s.strip()
                if s:
                    service_ids.append(s)

        clientes_map[nombre] = (id_oficial, cuit, service_ids)

    return servicios_map, clientes_map, df_activos


# ── PASO 2: Verificar idempotencia ──────────────────────────────────────────────

def ya_normalizado(cur) -> bool:
    """Retorna True si services.id ya NO tiene formato UUID."""
    cur.execute("SELECT id::text FROM services LIMIT 5;")
    rows = cur.fetchall()
    if not rows:
        return False  # tabla vacía, proceder
    for (val,) in rows:
        if UUID_PATTERN.match(val):
            return False  # todavía tiene UUIDs
    return True  # ya tiene IDs oficiales


# ── PASO 3: Alterar tipos de columnas UUID → VARCHAR ────────────────────────────

def alterar_tipos_columnas(cur):
    """
    Cambia UUID → VARCHAR en todas las columnas de IDs que necesitamos reescribir.
    Droppea FKs para trabajar libremente. Se restauran al final.
    """
    print("\n🔧 PASO 3: Alterando tipos de columna UUID → VARCHAR y Dropping FKs...")

    cur.execute("""
        SELECT
            tc.table_name,
            kcu.column_name,
            tc.constraint_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' 
          AND ccu.table_name IN ('services', 'clients', 'companies');
    """)
    fks = cur.fetchall()
    
    for table, col, name, f_table, f_col in fks:
        cur.execute(sql.SQL("ALTER TABLE {} DROP CONSTRAINT IF EXISTS {}").format(
            sql.Identifier(table), sql.Identifier(name)
        ))
        print(f"      - Dropped FK: {table}.{col} -> {f_table}.{f_col} ({name})")

    columnas = [
        ("services", "id"), ("clients", "id"), ("client_services", "id"),
        ("client_services", "client_id"), ("client_services", "service_id"),
        ("income_budgets", "client_id"), ("income_budgets", "service_id"),
        ("transactions", "client_id"), ("transactions", "service_id"),
        ("invoice_items", "service_id"), ("invoices", "client_id"),
    ]

    for table, col in columnas:
        cur.execute(sql.SQL("ALTER TABLE {} ALTER COLUMN {} TYPE VARCHAR USING {}::text").format(
            sql.Identifier(table), sql.Identifier(col), sql.Identifier(col)
        ))
        # print(f"      - {table}.{col}: UUID -> VARCHAR")

    return fks

def restaurar_constraints(cur, fks):
    print("\n🏗️  POST-PROCESAMIENTO: Restaurando Constraints...")
    for table, col, name, f_table, f_col in fks:
        cur.execute(sql.SQL(
            "ALTER TABLE {} ADD CONSTRAINT {} FOREIGN KEY ({}) REFERENCES {} ({})"
        ).format(
            sql.Identifier(table), sql.Identifier(name), sql.Identifier(col),
            sql.Identifier(f_table), sql.Identifier(f_col)
        ))
        print(f"      - Restored FK: {table}.{col} -> {f_table}.{f_col}")


# ── PASO 4: Mapeo y Reemplazo de Services ──────────────────────────────────────

def procesar_services(cur, servicios_map, clientes_map):
    print("\n🛠️  PASO 4: Procesando services...")
    cur.execute("SELECT id, name FROM services;")
    servicios_actuales = cur.fetchall()
    mapping = {} 
    
    print("    📥 Insertando servicios oficiales...")
    ids_oficiales = set()
    for nombre, (id_oficial, desc) in servicios_map.items():
        cur.execute("""
            INSERT INTO services (id, company_id, name, description, is_active, created_at, updated_at) 
            VALUES (%s, (SELECT id FROM companies LIMIT 1), %s, %s, true, NOW(), NOW()) 
            ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name;
        """, (id_oficial, nombre, desc or None))
        ids_oficiales.add(id_oficial)

    for s_id, name in servicios_actuales:
        if name in servicios_map: mapping[s_id] = servicios_map[name][0]
        elif name in clientes_map:
            ids = clientes_map[name][2]
            mapping[s_id] = ids[0] if ids else (list(servicios_map.values())[0][0])
        else: mapping[s_id] = s_id 

    return mapping, ids_oficiales


# ── PASO 5: Mapeo y Reemplazo de Clients ───────────────────────────────────────

def procesar_clients(cur, clientes_map):
    print("\n👤 PASO 5: Procesando clients...")
    cur.execute("SELECT id, name FROM clients;")
    clientes_actuales = cur.fetchall()
    mapping = {}
    ids_oficiales = set()

    print("    📥 Insertando clientes oficiales...")
    for nombre, (id_oficial, cuit, _) in clientes_map.items():
        cur.execute("""
            INSERT INTO clients (id, company_id, name, cuit_cuil_dni, fiscal_condition, is_active, created_at, updated_at)
            VALUES (%s, (SELECT id FROM companies LIMIT 1), %s, %s, 'CONSUMIDOR_FINAL', true, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, updated_at=NOW();
        """, (id_oficial, nombre, cuit or "20000000000"))
        ids_oficiales.add(id_oficial)

    for c_id, name in clientes_actuales:
        if name in clientes_map: mapping[c_id] = clientes_map[name][0]
        else: mapping[c_id] = c_id
    
    return mapping, ids_oficiales


# ── PASO 6: Re-link de toda la data ───────────────────────────────────────────

def relink_data(cur, service_map, client_map):
    print("\n🔗 PASO 6: Re-vinculando data en budgets/transactions...")
    tablas_fks = [
        ("income_budgets", "service_id", service_map),
        ("income_budgets", "client_id", client_map),
        ("transactions", "service_id", service_map),
        ("transactions", "client_id", client_map),
        ("invoices", "client_id", client_map),
        ("invoice_items", "service_id", service_map),
    ]
    for table, col, mapa in tablas_fks:
        count = 0
        for old_id, new_id in mapa.items():
            if old_id != new_id:
                cur.execute(sql.SQL("UPDATE {} SET {} = %s WHERE {} = %s").format(
                    sql.Identifier(table), sql.Identifier(col), sql.Identifier(col)
                ), (new_id, old_id))
                count += cur.rowcount
        if count > 0: print(f"    ✅ {table}.{col}: {count} filas re-vinculadas")


# ── PASO 7: Reconstruir client_services ────────────────────────────────────────

def reconstruir_client_services(cur, clientes_map):
    print("\n🔗 PASO 7: Reconstruyendo client_services...")
    cur.execute("DELETE FROM client_services;")
    insertados = 0
    from datetime import date
    for _, (id_cliente, _, s_ids) in clientes_map.items():
        for s_id in s_ids:
            cur.execute("INSERT INTO client_services (id, client_id, service_id, monthly_fee, currency, start_date, status, created_at, updated_at) "
                        "VALUES (gen_random_uuid()::text, %s, %s, 0, 'ARS', %s, 'ACTIVE', NOW(), NOW()) ON CONFLICT DO NOTHING;",
                        (id_cliente, s_id, date(2025,1,1)))
            insertados += cur.rowcount
    print(f"    ✅ {insertados} relaciones creadas")


def verificar(cur):
    print("\n✅ PASO 8: Verificaciones...")
    cur.execute("SELECT COUNT(*) FROM services WHERE id ~ '^[0-9]';")
    print(f"  Services oficiales: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM clients WHERE id LIKE 'c%';")
    print(f"  Clients oficiales:  {cur.fetchone()[0]}")

import logging
logging.basicConfig(filename='migracion_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

def main():
    logging.info("Starting normalization")
    print("=" * 60)
    print("  NORMALIZAR IDs OFICIALES (Stable Swap)")
    print("=" * 60)
    s_map_csv, c_map_csv, _ = leer_csvs()
    conn = get_connection()
    conn.autocommit = False
    try:
        logging.info("Backup starting")
        hacer_backup(parse_db_url(os.getenv("DATABASE_URL")))
        cur = conn.cursor()
        
        logging.info("Checking idempotency")
        if ya_normalizado(cur):
            print("  ✅ Ya normalizado."); return
        
        logging.info("Step 3: Altering types and dropping constraints")
        fks_to_restore = alterar_tipos_columnas(cur)
        
        logging.info("Step 4: Mappings and Insertion")
        s_mapping, ids_serv_oficiales = procesar_services(cur, s_map_csv, c_map_csv)
        c_mapping, ids_clie_oficiales = procesar_clients(cur, c_map_csv)
        
        logging.info("Step 6: Relinking data")
        relink_data(cur, s_mapping, c_mapping)
        
        logging.info("Step 3: Cleanup and Fallback")
        print("\n🧹 Limpiando records obsoletos y huérfanos...")
        
        # Aseguramos placeholders oficiales para huérfanos Not Null
        def_cid, def_sid = 'c99', '45898'
        cur.execute("INSERT INTO services (id, company_id, name, is_active, created_at, updated_at) VALUES (%s, (SELECT id FROM companies LIMIT 1), 'Generic Service', true, NOW(), NOW()) ON CONFLICT (id) DO NOTHING;", (def_sid,))
        cur.execute("INSERT INTO clients (id, company_id, name, cuit_cuil_dni, fiscal_condition, is_active, created_at, updated_at) VALUES (%s, (SELECT id FROM companies LIMIT 1), 'Generic Client', '20000000000', 'CONSUMIDOR_FINAL', true, NOW(), NOW()) ON CONFLICT (id) DO NOTHING;", (def_cid,))
        ids_serv_oficiales.add(def_sid); ids_clie_oficiales.add(def_cid)

        tablas_limpieza = [
            ("income_budgets", "service_id", "services", def_sid), 
            ("income_budgets", "client_id", "clients", def_cid),
            ("transactions", "service_id", "services", None), 
            ("transactions", "client_id", "clients", None),
            ("invoices", "client_id", "clients", None), 
            ("invoice_items", "service_id", "services", None),
        ]
        for table, col, ref_table, fallback in tablas_limpieza:
            v_ids = ids_serv_oficiales if ref_table == "services" else ids_clie_oficiales
            if fallback:
                cur.execute(sql.SQL("UPDATE {} SET {} = %s WHERE {} NOT IN %s").format(
                    sql.Identifier(table), sql.Identifier(col), sql.Identifier(col)
                ), (fallback, tuple(v_ids)))
                if cur.rowcount > 0: print(f"    ⚠️ {table}.{col}: {cur.rowcount} huérfanos -> {fallback}")
            else:
                cur.execute(sql.SQL("UPDATE {} SET {} = NULL WHERE {} NOT IN %s AND {} IS NOT NULL").format(
                    sql.Identifier(table), sql.Identifier(col), sql.Identifier(col), sql.Identifier(col)
                ), (tuple(v_ids),))
                if cur.rowcount > 0: print(f"    ⚠️ {table}.{col}: {cur.rowcount} huérfanos -> NULL")

        cur.execute("DELETE FROM services WHERE id NOT IN %s", (tuple(ids_serv_oficiales),))
        cur.execute("DELETE FROM clients WHERE id NOT IN %s", (tuple(ids_clie_oficiales),))
        
        logging.info("Finalizing Structure")
        reconstruir_client_services(cur, c_map_csv)
        restaurar_constraints(cur, fks_to_restore)
        verificar(cur)
        
        conn.commit()
        logging.info("Normalization committed successfully")
        print("\n🎉 NORMALIZACIÓN EXITOSA")
    except Exception as e:
        conn.rollback()
        logging.error(f"FATAL ERROR: {e}", exc_info=True)
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback; traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
