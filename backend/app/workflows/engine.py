from inngest import Inngest, Step
from integrations import TOOL_REGISTRY
from lib.variable_resolver import resolve_variables
from datetime import datetime
from lib.supabase_lib import supabase

# 1. Initialize Inngest
inngest_client = Inngest(app_id="biz_flow_engine")


@inngest_client.create_function(
    fn_id="execute_business_workflow",
    trigger="workflow/run_requested",
)
async def execute_workflow(ctx, step: Step):
    blueprint = ctx.event.data.get("blueprint")
    event_payload = ctx.event.data.get("payload")
    workflow_id = blueprint.get("id")

    # 1. LOG START: Create the entry in Supabase
    log_entry = await step.run(
        "initialize_log",
        lambda: supabase.table("workflow_logs")
        .insert(
            {
                "workflow_id": workflow_id,
                "run_id": ctx.run_id,
                "status": "running",
                "trigger_data": event_payload,
            }
        )
        .execute(),
    )

    results = {"trigger_data": event_payload}

    try:
        for node in blueprint["nodes"]:
            # ... (Your existing node execution logic) ...

            # 2. UPDATE LOG: Save progress after each step
            # This allows the frontend to show "Node 1 Done, Node 2 Processing..."
            await step.run(
                f"update_log_{node['id']}",
                lambda: supabase.table("workflow_logs")
                .update({"step_results": results})
                .eq("run_id", ctx.run_id)
                .execute(),
            )

        # 3. LOG COMPLETION
        await step.run(
            "finalize_log",
            lambda: supabase.table("workflow_logs")
            .update({"status": "completed", "completed_at": datetime.now().isoformat()})
            .eq("run_id", ctx.run_id)
            .execute(),
        )

    except Exception as e:
        # 4. LOG FAILURE
        await step.run(
            "log_failure",
            lambda: supabase.table("workflow_logs")
            .update({"status": "failed", "error_message": str(e)})
            .eq("run_id", ctx.run_id)
            .execute(),
        )
        raise e


async def perform_action(action_data, context_data):
    """
    Standardized router that handles ALL services automatically.
    """
    service = action_data["service"]
    task = action_data["task"]
    raw_params = action_data.get("params", {})

    # 1. Resolve variables against the current state
    resolved_params = {
        k: resolve_variables(v, context_data) if isinstance(v, str) else v
        for k, v in raw_params.items()
    }

    # 2. Lookup the tool in the registry
    tool = TOOL_REGISTRY.get(service)

    if not tool:
        return {"status": "error", "message": f"Service '{service}' is not integrated."}

    # 3. Execute the tool's standardized interface
    try:
        # Every tool now has an '.execute()' method thanks to BaseTool
        return await tool.execute(task, resolved_params)
    except Exception as e:
        return {"status": "error", "details": str(e)}
