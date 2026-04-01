import requests
import pandas as pd
import json

SUPABASE_URL = "https://fumejzkghviszmyfjegg.supabase.co"
SUPABASE_API_KEY = "sb_publishable_6ro7Nn8JvbXqP-CXJ-NK6Q_k1Hip3CW"

headers_get = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": "Bearer " + SUPABASE_API_KEY,
    "Content-Type": "application/json"
}

headers_patch = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": "Bearer " + SUPABASE_API_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def fetch_table(table_name):
    # Fetch all records using PostgREST pagination if necessary
    limit = 1000
    offset = 0
    all_data = []
    
    while True:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit={limit}&offset={offset}", 
            headers=headers_get
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        all_data.extend(data)
        if len(data) < limit:
            break
        offset += limit
        
    return all_data

def main():
    print("Fetching data from Supabase...")
    client_services = fetch_table("client_services")
    income_budgets = fetch_table("income_budgets")
    
    print(f"Fetched {len(client_services)} client_services and {len(income_budgets)} income_budgets.")
    
    ib_df = pd.DataFrame(income_budgets)
    if ib_df.empty:
        print("No income budgets found.")
        return
        
    # Sort by year and month descending to get the latest easily
    # First, let's make sure period_year and period_month exist and are numeric
    if 'period_year' in ib_df.columns and 'period_month' in ib_df.columns:
        ib_df['period_year'] = pd.to_numeric(ib_df['period_year'], errors='coerce')
        ib_df['period_month'] = pd.to_numeric(ib_df['period_month'], errors='coerce')
        ib_df = ib_df.sort_values(by=['period_year', 'period_month'], ascending=[False, False])
    else:
        print("Columns period_year or period_month not found in income_budgets. Cannot determine latest month.")
        return
    
    # Group by client_id and service_id and take the first record (which should be the latest month)
    latest_ib = ib_df.groupby(['client_id', 'service_id']).first().reset_index()
    
    budget_map = {}
    for _, row in latest_ib.iterrows():
        budget_map[(row['client_id'], row['service_id'])] = row['budgeted_amount']
        
    updates = []
    for cs in client_services:
        client_id = cs.get('client_id')
        service_id = cs.get('service_id')
        current_fee = cs.get('monthly_fee')
        
        new_fee = budget_map.get((client_id, service_id))
        
        if new_fee is not None:
            # Convert both to float for safe comparison (handling strings/numbers)
            try:
                curr_float = float(current_fee) if current_fee is not None else 0.0
                new_float = float(new_fee)
                
                # if there is a difference or if the current fee is 0 and new fee is something else
                if abs(curr_float - new_float) > 0.01:
                    updates.append({
                        'id': cs['id'],
                        'client_id': client_id,
                        'service_id': service_id,
                        'old_fee': curr_float,
                        'new_fee': new_float
                    })
            except ValueError:
                print(f"Error comparing values for {client_id}-{service_id}: current_fee={current_fee}, new_fee={new_fee}")
                
    print(f"Found {len(updates)} client_services to update.")
    
    if not updates:
        print("No updates needed.")
        return
        
    print("Sample updates to be applied:")
    for u in updates[:10]:
        print(f"  {u['client_id']} - {u['service_id']}: {u['old_fee']} -> {u['new_fee']}")
        
    print("\nApplying updates...")
    success_count = 0
    error_count = 0
    for u in updates:
        cs_id = u['id']
        new_fee = u['new_fee']
        
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/client_services?id=eq.{cs_id}",
            headers=headers_patch,
            json={'monthly_fee': new_fee}
        )
        
        if response.status_code not in (200, 204):
            print(f"Error updating {cs_id}: {response.text}")
            error_count += 1
        else:
            success_count += 1
            
    print(f"\nUpdate complete! {success_count} succeeded, {error_count} failed.")

if __name__ == '__main__':
    main()
