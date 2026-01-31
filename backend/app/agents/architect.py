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
        print("\\n" + "=" * 60)
        print("🤖 [WorkflowArchitect] draft_workflow called")
        print(f"📝 [WorkflowArchitect] User prompt: {user_prompt}")

        system_msg = (
            "You are a Business Workflow Architect. Convert the user's request into a structured graph. "
            "Available Services: razorpay, whatsapp, google_sheets, timer. "
            "Ensure every node has a unique 'id' and 'position'. "
            "For 'razorpay' service, include params: amount, currency, receipt, payment_capture in 'params' dict. "
            "For 'whatsapp' service, include params: phone_number, message, twilio_sandbox_number, whatsapp_id in 'params' dict. "
            "For 'google_sheets' service, include params: spreadsheet_id, range, values. "
            "For 'timer' service, include params: duration_seconds."
        )

        print(f"💬 [WorkflowArchitect] System message: {system_msg[:100]}...")
        print("🔮 [WorkflowArchitect] Invoking LLM with structured output")

        try:
            blueprint = await self.structured_llm.ainvoke(
                [("system", system_msg), ("human", user_prompt)]
            )
            return blueprint
        except Exception as e:
            print(f"Architect Error: {e}")
            raise e

        print(f"✅ [WorkflowArchitect] Blueprint generated successfully")
        print(f"📊 [WorkflowArchitect] Blueprint type: {type(blueprint)}")
        print(f"📊 [WorkflowArchitect] Blueprint: {blueprint}")
        print("=" * 60 + "\\n")
