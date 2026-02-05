"""
This module defines the WorkflowArchitect agent, which acts as a bridge between natural
language user requirements and a structured execution graph.

Functionality:
- Translates high-level business logic (e.g., "Send a WhatsApp message after a Razorpay payment")
  into a directed graph of automation nodes.
- Utilizes GPT-4o via LangChain's structured output (function calling) to ensure
  the generated JSON conforms strictly to the `WorkflowBlueprint` schema.
- Automatically handles variable injection and data mapping between services like
  Razorpay, WhatsApp, Google Sheets, and Timers.

Output:
- A `WorkflowBlueprint` instance containing the validated sequence of nodes and their logical connections.

"""

from langchain_openai import ChatOpenAI
from workflows.schema import WorkflowBlueprint


class WorkflowArchitect:
    def __init__(self):
        # We use gpt-4o for complex architecture logic
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # We switch to 'function_calling' to avoid the strict schema 400 errors
        self.structured_llm = self.llm.with_structured_output(
            WorkflowBlueprint,
            method="function_calling",  # <--- THIS IS THE FIX
        )

    async def draft_workflow(self, user_prompt: str) -> WorkflowBlueprint:
        print("\n" + "=" * 60)
        print("🤖 [WorkflowArchitect] draft_workflow called")
        print(f"📝 [WorkflowArchitect] User prompt: {user_prompt}")

        system_msg = (
            "You are a Business Workflow Architect. Convert the user's request into a structured graph with proper automation. "
            "Available Services: razorpay, whatsapp, google_sheets, timer. "
            "Ensure every node has a unique 'id' and 'position'. "
            "IMPORTANT: Automatically set up variable mappings between nodes for full automation. "
            "For 'razorpay' service with 'create_payment_link' task, include params: "
            "amount (number), currency ('INR'), customer_name ('{{trigger_data.customer_name}}'), "
            "customer_email ('{{trigger_data.customer_email}}'), customer_phone ('{{trigger_data.customer_phone}}'), "
            "description ('Payment for order {{trigger_data.order_id}}'). "
            "For 'whatsapp' service with 'send_message' task, include params: "
            "phoneNumber ('{{trigger_data.customer_phone}}' or '{{razorpay_1.customer_phone}}'), "
            "message ('Hi {{trigger_data.customer_name}}! Your payment link: {{razorpay_1.payment_url}}. Please complete payment.'). "
            "For 'google_sheets' service with 'append_data' task, include params: "
            "spreadsheet_id ('{{env.DEFAULT_SPREADSHEET_ID}}' or '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'), "
            "range ('A:E'), "
            'values (\'[["{{trigger_data.customer_name}}", "{{trigger_data.customer_email}}", "{{razorpay_1.amount}}", "{{razorpay_1.payment_url}}", "{{trigger_data.timestamp}}"]]\'). '
            "For 'timer' service, include params: duration_seconds (number). "
            "Always use variable references like {{trigger_data.field}} and {{node_id.field}} to connect data between nodes. "
            "Set realistic positions with proper spacing (x: 100, 200, 300... y: 100, 200, 300...). "
            "Create meaningful node IDs like 'razorpay_1', 'whatsapp_1', 'sheets_1'."
        )
        print("🔮 [WorkflowArchitect] Invoking LLM with structured output")

        try:
            blueprint = await self.structured_llm.ainvoke(
                [("system", system_msg), ("human", user_prompt)]
            )

            print("✅ [WorkflowArchitect] Blueprint generated successfully")
            print(f"📊 [WorkflowArchitect] Blueprint type: {type(blueprint)}")
            print(
                f"📊 [WorkflowArchitect] Nodes: {len(blueprint.nodes) if blueprint.nodes else 0}"
            )
            print(
                f"🔗 [WorkflowArchitect] Edges: {len(blueprint.edges) if blueprint.edges else 0}"
            )

            # Log the generated nodes for debugging
            if blueprint.nodes:
                for node in blueprint.nodes:
                    print(
                        f"🔵 [WorkflowArchitect] Node {node.id}: {node.data.service} - {node.data.task}"
                    )
                    if hasattr(node.data, "params") and node.data.params:
                        print(f"   📋 [WorkflowArchitect] Params: {node.data.params}")

            print("=" * 60 + "\n")
            return blueprint

        except Exception as e:
            print(f"❌ [WorkflowArchitect] Error: {e}")
            print("=" * 60 + "\n")
            raise e
