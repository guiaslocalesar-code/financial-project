import psycopg2

DEST_HOST = "db.fumejzkghviszmyfjegg.supabase.co"
DEST_PORT = 5432
DEST_DB   = "postgres"
DEST_USER = "postgres"
DEST_PASS = "GuiasSA2020@"

def apply_perms():
    sql_commands = [
        # Habilitar RLS en las tablas principales
        "ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE public.expense_budgets ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE public.income_budgets ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;",
        "ALTER TABLE public.commissions ENABLE ROW LEVEL SECURITY;",

        # Políticas para TRANSACTIONS
        "DROP POLICY IF EXISTS \"Permitir lectura para todos\" ON public.transactions;",
        "CREATE POLICY \"Permitir lectura para todos\" ON public.transactions FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS \"Permitir inserción desde el front\" ON public.transactions;",
        "CREATE POLICY \"Permitir inserción desde el front\" ON public.transactions FOR INSERT TO anon WITH CHECK (true);",
        "DROP POLICY IF EXISTS \"Permitir actualización desde el front\" ON public.transactions;",
        "CREATE POLICY \"Permitir actualización desde el front\" ON public.transactions FOR UPDATE TO anon USING (true) WITH CHECK (true);",

        # Políticas para EXPENSE_BUDGETS
        "DROP POLICY IF EXISTS \"Permitir lectura para todos\" ON public.expense_budgets;",
        "CREATE POLICY \"Permitir lectura para todos\" ON public.expense_budgets FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS \"Permitir inserción desde el front\" ON public.expense_budgets;",
        "CREATE POLICY \"Permitir inserción desde el front\" ON public.expense_budgets FOR INSERT TO anon WITH CHECK (true);",
        "DROP POLICY IF EXISTS \"Permitir actualización desde el front\" ON public.expense_budgets;",
        "CREATE POLICY \"Permitir actualización desde el front\" ON public.expense_budgets FOR UPDATE TO anon USING (true) WITH CHECK (true);",

        # Políticas para INCOME_BUDGETS
        "DROP POLICY IF EXISTS \"Permitir lectura para todos\" ON public.income_budgets;",
        "CREATE POLICY \"Permitir lectura para todos\" ON public.income_budgets FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS \"Permitir inserción desde el front\" ON public.income_budgets;",
        "CREATE POLICY \"Permitir inserción desde el front\" ON public.income_budgets FOR INSERT TO anon WITH CHECK (true);",
        "DROP POLICY IF EXISTS \"Permitir actualización desde el front\" ON public.income_budgets;",
        "CREATE POLICY \"Permitir actualización desde el front\" ON public.income_budgets FOR UPDATE TO anon USING (true) WITH CHECK (true);",

        # Políticas para CLIENTS
        "DROP POLICY IF EXISTS \"Permitir lectura para todos\" ON public.clients;",
        "CREATE POLICY \"Permitir lectura para todos\" ON public.clients FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS \"Permitir inserción desde el front\" ON public.clients;",
        "CREATE POLICY \"Permitir inserción desde el front\" ON public.clients FOR INSERT TO anon WITH CHECK (true);",
        "DROP POLICY IF EXISTS \"Permitir actualización desde el front\" ON public.clients;",
        "CREATE POLICY \"Permitir actualización desde el front\" ON public.clients FOR UPDATE TO anon USING (true) WITH CHECK (true);",

        # Políticas para COMMISSIONS
        "DROP POLICY IF EXISTS \"Permitir lectura para todos\" ON public.commissions;",
        "CREATE POLICY \"Permitir lectura para todos\" ON public.commissions FOR SELECT USING (true);",
        "DROP POLICY IF EXISTS \"Permitir inserción desde el front\" ON public.commissions;",
        "CREATE POLICY \"Permitir inserción desde el front\" ON public.commissions FOR INSERT TO anon WITH CHECK (true);",
        "DROP POLICY IF EXISTS \"Permitir actualización desde el front\" ON public.commissions;",
        "CREATE POLICY \"Permitir actualización desde el front\" ON public.commissions FOR UPDATE TO anon USING (true) WITH CHECK (true);"
    ]

    passwords = ["GuiasSA2020@", "FinancialAgent_2026!"]
    
    for pwd in passwords:
        try:
            print(f"Connecting to {DEST_HOST} with password: {pwd[:3]}***")
            conn = psycopg2.connect(
                host=DEST_HOST, port=DEST_PORT, dbname=DEST_DB,
                user=DEST_USER, password=pwd, connect_timeout=15,
                sslmode="require"
            )
            conn.autocommit = True
            with conn.cursor() as cur:
                for cmd in sql_commands:
                    print(f"Executing: {cmd[:60]}...")
                    cur.execute(cmd)
            print("\nSUCCESS: Permissions applied correctly.")
            conn.close()
            return # Si funcionó, salimos
        except Exception as e:
            print(f"FAIL with password {pwd[:3]}***: {e}")


if __name__ == "__main__":
    apply_perms()
