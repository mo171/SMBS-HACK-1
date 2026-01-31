from supabase import create_client
import os

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

supabase= create_client(supabase_url, supabase_key)


def get_active_workflows_by_trigger(service_name: str):
    """
    Search Supabase for any workflow that is 'active' 
    and has a trigger node matching our service.
    """
    # We use a JSON path query to look inside the 'nodes' column
    response = supabase.table("workflow_blueprints") \
        .select("*") \
        .eq("is_active", True) \
        .execute()
    
    # Filter for the specific service (e.g., 'razorpay')
    # In a production app, you'd use a more advanced Postgres JSON query
    matching_blueprints = []
    for bp in response.data:
        for node in bp['nodes']:
            if node['type'] == 'trigger' and node['data']['service'] == service_name:
                matching_blueprints.append(bp)
                
    return matching_blueprints