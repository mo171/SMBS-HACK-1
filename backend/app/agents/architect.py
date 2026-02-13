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
            "Available Services: razorpay, whatsapp, google_sheets, timer, shiprocket, bluesky, social_logic, pixelfed, instagram, database, gpt. "
            "Ensure every node has a unique 'id' and 'position'. "
            "IMPORTANT: Automatically set up variable mappings between nodes for full automation. "
            "PHONE NUMBERS: Always look for phone numbers in the trigger_data. If the user mentions a specific number, use it. "
            "Ensure phone numbers are mapped to the 'phone' or 'phoneNumber' parameter exactly as found or via {{trigger_data.customer_phone}}. "
            "DATA INFERENCE: If the user wants to 'log everything' or 'save details', infer a list of columns for 'google_sheets' task 'append_data'. "
            'Use values like \'{{"customer": "{{trigger_data.customer_name}}", "amount": "{{trigger_data.amount}}", "link": "{{razorpay_1.payment_url}}", "time": "{{trigger_data.timestamp}}"}}\'. '
            "SHIPROCKET LOGIC: If the user mentions 'delivery', 'shipping', 'courier', or 'sending items', include a 'shiprocket' node. "
            "Place it AFTER payment nodes. Map address, city, and pincode from {{trigger_data}}. "
            "BLUESKY LOGIC: If the user mentions 'post to social', 'post to bluesky', 'broadcast', or 'share update', include a 'bluesky' node. "
            "PIXELFED LOGIC: If the user mentions 'post to pixelfed', 'share photo', or 'post image', include a 'pixelfed' node with task 'publish_post'. "
            "For 'pixelfed' service with 'publish_post' task, include params: caption (text), image_url (URL of image). "
            "AUTO-REPLY LOGIC: If the user says 'reply to mentions' or 'monitor social', build a loop: "
            "1. 'bluesky' (or 'instagram' or 'pixelfed') task 'read_notifications' (or 'get_conversations') -> 2. 'social_logic' task 'draft_reply' (param: mention={{trigger_data}}, context_type='stock', product_name={{trigger_data.text}}) "
            "-> 3. 'bluesky' (or 'instagram' or 'pixelfed') task 'post_content' (or 'send_dm') (param: text={{social_logic_1.suggested_text}}, reply_to={{social_logic_1.reply_to}} or recipient_id={{trigger_data.sender_id}}). "
            "IG LOGIC: If the user mentions 'post to instagram' or 'share on ig', include an 'instagram' node with task 'publish_post'. "
            "For 'instagram' service with 'send_dm' task, include params: recipient_id (ID of the user), text (Message content). "
            "text (String content of the post, e.g., 'New deal! {{trigger_data.deal_name}} only for ₹{{trigger_data.price}}'). "
            "For 'shiprocket' service with 'create_order' task, include params: "
            "customer_name ('{{trigger_data.customer_name}}'), address ('{{trigger_data.address}}'), "
            "city ('{{trigger_data.city}}'), pincode ('{{trigger_data.pincode}}'), state ('{{trigger_data.state}}'), "
            "phone ('{{trigger_data.customer_phone}}'), amount (number from trigger). "
            "For 'razorpay' service with 'create_payment_link' task, include params: "
            "amount (number), currency ('INR'), customer_name ('{{trigger_data.customer_name}}'), "
            "customer_email ('{{trigger_data.customer_email}}'), customer_phone ('{{trigger_data.customer_phone}}'), "
            "description ('Payment for order {{trigger_data.order_id}}'). "
            "For 'whatsapp' service with 'send_message' task, include params: "
            "phone ('{{trigger_data.phone}}' or '{{trigger_data.customer_phone}}' or '{{razorpay_1.customer_phone}}'), "
            "message ('Hi {{trigger_data.customer_name}}! Your payment link: {{razorpay_1.payment_url}}. Please complete payment.'). "
            "If shippable, mention tracking info: 'Track here: https://shiprocket.co/{{shiprocket_1.awb_number}}'. "
            "For 'google_sheets' service with 'append_data' task, include params: "
            "spreadsheet_id ('{{env.DEFAULT_SPREADSHEET_ID}}' or '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'), "
            "sheet_name ('Sheet1' or 'Class Data'), "
            'data (\'{"name": "{{trigger_data.customer_name}}", "status": "Success"}\' or similar structured object). '
            "DATABASE LOGIC: If user mentions 'check database', 'query users', 'find records', 'who hasn't paid', 'unpaid users', include a 'database' node. "
            "For 'database' service with 'query_table' task, include params: "
            "table (table name like 'users', 'orders', 'payments'), "
            'filters (dict like {"status": "unpaid", "payment_due": true}), '
            "select (columns like 'name, email, phone, amount' or '*'). "
            '{"table": "users", "filters": {"payment_status": "unpaid"}, "select": "name, phone, amount_due"}. '
            "Use database results in next nodes via {{database_1.results}} or {{database_1.data}}. "
            "GPT/AI PROCESSING: If user mentions 'analyze', 'summarize', 'create post', 'write caption', 'format data', 'make it engaging', include a 'gpt' node BEFORE posting/messaging nodes. "
            "For 'gpt' service with 'process_text' task, include params: "
            "input_data (data to process, use {{database_1.results}} or {{trigger_data.info}}), "
            "persona (brand voice: 'professional', 'friendly', 'creative', 'casual', or custom like 'sustainable fashion brand'), "
            "instructions (specific task like 'Create an engaging social media post summarizing this data with emojis'), "
            "output_format ('text', 'json', 'markdown'). "
            'Example: {"service": "gpt", "task": "process_text", "params": {"input_data": "{{database_1.results}}", "persona": "friendly", "instructions": "Summarize weekly sales into engaging Bluesky post", "output_format": "text"}}. '
            "Use GPT output in next nodes via {{gpt_1.processed_text}}. "
            "For 'timer' service, include params: duration (number). "
            "Always use variable references like {{trigger_data.field}} and {{node_id.field}} to connect data between nodes. "
            "Set realistic positions with proper spacing (x: 100, 200... y: 100, 200...). "
            "Create meaningful node IDs like 'razorpay_1', 'whatsapp_1', 'sheets_1', 'shiprocket_1', 'pixelfed_1', 'database_1', 'gpt_1'."
            "LOOPING/RECURRING TASKS: If the user says 'every X seconds', 'repeat every X minutes', 'loop every X hours', 'every day', or 'daily', "
            "set the blueprint's 'loop_seconds' field to the interval in seconds. "
            "Example: 'every 5 seconds' -> loop_seconds = 5. 'every 1 minute' -> loop_seconds = 60. 'every day' or 'daily' -> loop_seconds = 86400. "
            "If no repetition is mentioned, keep loop_seconds = 0."
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
