from inngest import Inngest, TriggerEvent
from integrations import TOOL_REGISTRY
from lib.variable_resolver import resolve_variables
from datetime import datetime
from lib.supabase_lib import supabase

# 1. Initialize Inngest for development mode
inngest_client = Inngest(app_id="biz_flow_engine", is_production=False)


@inngest_client.create_function(
    fn_id="execute_business_workflow",
    trigger=TriggerEvent(event="workflow/run_requested"),
)
async def execute_workflow(ctx):
    print("\n" + "=" * 80)
    print("🚀 [WorkflowEngine] execute_workflow function called")
    print(f"🆔 [WorkflowEngine] Run ID: {ctx.run_id}")

    blueprint = ctx.event.data.get("blueprint")
    event_payload = ctx.event.data.get("payload")
    workflow_id = blueprint.get("id")

    print(f"📊 [WorkflowEngine] Blueprint: {blueprint}")
    print(f"📦 [WorkflowEngine] Event payload: {event_payload}")
    print(f"🆔 [WorkflowEngine] Workflow ID: {workflow_id}")
    print(f"📊 [WorkflowEngine] Nodes count: {len(blueprint.get('nodes', []))}")

    # 1. LOG START: Create the entry in Supabase
    print("💾 [WorkflowEngine] Creating workflow_logs entry in Supabase")
    log_entry = await ctx.step.run(
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
    print(f"✅ [WorkflowEngine] Workflow log initialized: {log_entry}")

    results = {"trigger_data": event_payload}
    node_states = {}  # Track individual node execution states
    print(f"📊 [WorkflowEngine] Initial results: {results}")

    try:
        for node in blueprint["nodes"]:
            node_id = node["id"]
            print(f"\n{'-' * 60}")
            print(f"🔵 [WorkflowEngine] Processing node: {node_id}")
            print(f"📊 [WorkflowEngine] Node data: {node.get('data')}")

            # Mark node as running
            node_states[node_id] = {"status": "running", "data": None, "error": None}
            print(f"⏳ [WorkflowEngine] Marking node {node_id} as running")
            print(f"📊 [WorkflowEngine] Current node_states: {node_states}")

            await ctx.step.run(
                f"mark_running_{node_id}",
                lambda ns=node_states.copy(): supabase.table("workflow_logs")
                .update({"step_results": ns})
                .eq("run_id", ctx.run_id)
                .execute(),
            )
            print(f"✅ [WorkflowEngine] Node {node_id} marked as running in Supabase")

            # Execute the node action
            try:
                print(f"🚀 [WorkflowEngine] Executing action for node {node_id}")
                action_result = await ctx.step.run(
                    f"execute_{node_id}", lambda: perform_action(node["data"], results)
                )
                print(
                    f"✅ [WorkflowEngine] Action result for node {node_id}: {action_result}"
                )

                # Store the result
                results[node_id] = action_result
                print(f"💾 [WorkflowEngine] Stored result for node {node_id}")

                # Mark node as completed
                node_states[node_id] = {
                    "status": "completed",
                    "data": action_result,
                    "error": None,
                }
                print(f"✅ [WorkflowEngine] Node {node_id} marked as completed")

            except Exception as node_error:
                print(f"❌ [WorkflowEngine] Error in node {node_id}: {node_error}")
                print(f"❌ [WorkflowEngine] Error type: {type(node_error)}")
                print(f"❌ [WorkflowEngine] Error details: {str(node_error)}")

                # Mark node as failed
                node_states[node_id] = {
                    "status": "failed",
                    "data": None,
                    "error": str(node_error),
                }
                raise node_error

            # Update log with current node state
            print(f"💾 [WorkflowEngine] Updating workflow_logs for node {node_id}")
            await ctx.step.run(
                f"update_log_{node_id}",
                lambda ns=node_states.copy(): supabase.table("workflow_logs")
                .update({"step_results": ns})
                .eq("run_id", ctx.run_id)
                .execute(),
            )
            print(f"✅ [WorkflowEngine] Workflow log updated for node {node_id}")

        # 3. LOG COMPLETION
        print(f"\n{'-' * 60}")
        print("✅ [WorkflowEngine] All nodes completed successfully")
        print("💾 [WorkflowEngine] Finalizing workflow log")
        await ctx.step.run(
            "finalize_log",
            lambda: supabase.table("workflow_logs")
            .update({"status": "completed", "completed_at": datetime.now().isoformat()})
            .eq("run_id", ctx.run_id)
            .execute(),
        )
        print("✅ [WorkflowEngine] Workflow completed successfully")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n{'-' * 60}")
        print(f"❌ [WorkflowEngine] Workflow failed with error: {e}")
        print(f"❌ [WorkflowEngine] Error type: {type(e)}")
        print(f"❌ [WorkflowEngine] Error details: {str(e)}")

        # 4. LOG FAILURE
        print("💾 [WorkflowEngine] Logging failure to Supabase")
        await ctx.step.run(
            "log_failure",
            lambda: supabase.table("workflow_logs")
            .update({"status": "failed", "error_message": str(e)})
            .eq("run_id", ctx.run_id)
            .execute(),
        )
        print("=" * 80 + "\n")
        raise e


async def perform_action(action_data, context_data):
    """
    Standardized router that handles ALL services automatically.
    """
    print(f"\n{'~' * 60}")
    print("🔧 [perform_action] Function called")
    print(f"📊 [perform_action] Action data: {action_data}")
    print(f"📊 [perform_action] Context data: {context_data}")

    service = action_data["service"]
    task = action_data["task"]
    raw_params = action_data.get("params", {})

    print(f"🔧 [perform_action] Service: {service}")
    print(f"📝 [perform_action] Task: {task}")
    print(f"📦 [perform_action] Raw params: {raw_params}")

    # 1. Resolve variables against the current state
    print("🔍 [perform_action] Resolving variables")
    resolved_params = {
        k: resolve_variables(v, context_data) if isinstance(v, str) else v
        for k, v in raw_params.items()
    }
    print(f"✅ [perform_action] Resolved params: {resolved_params}")

    # 2. Lookup the tool in the registry
    print(f"🔍 [perform_action] Looking up tool '{service}' in registry")
    tool = TOOL_REGISTRY.get(service)

    if not tool:
        error_msg = f"Service '{service}' is not integrated."
        print(f"❌ [perform_action] {error_msg}")
        print(f"{'~' * 60}\n")
        return {"status": "error", "message": error_msg}

    print(f"✅ [perform_action] Tool found: {tool}")

    # 3. Execute the tool's standardized interface
    try:
        print(f"🚀 [perform_action] Executing tool.execute({task}, {resolved_params})")
        # Every tool now has an '.execute()' method thanks to BaseTool
        result = await tool.execute(task, resolved_params)
        print(f"✅ [perform_action] Tool execution successful: {result}")
        print(f"{'~' * 60}\n")
        return result
    except Exception as e:
        error_result = {"status": "error", "details": str(e)}
        print(f"❌ [perform_action] Tool execution failed: {e}")
        print(f"❌ [perform_action] Error type: {type(e)}")
        print(f"❌ [perform_action] Returning: {error_result}")
        print(f"{'~' * 60}\n")
        return error_result
