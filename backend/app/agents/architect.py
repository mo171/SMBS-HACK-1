from langchain_openai import ChatOpenAI
from ..workflows.schema import WorkflowBlueprint

class WorkflowArchitect:
    def __init__(self):
        # We use gpt-4o for complex architecture logic
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.structured_llm = self.llm.with_structured_output(WorkflowBlueprint)

    async def draft_workflow(self, user_prompt: str) -> WorkflowBlueprint:
        system_msg = (
            "You are a Business Workflow Architect. Convert the user's request into a structured graph. "
            "Identify the 'trigger' (the event that starts it) and the 'actions' (what happens next). "
            "Available Services: razorpay, whatsapp, google_sheets, instagram, timer. "
            "Example: 'If I get a payment, log it to sheets' -> Trigger: razorpay, Action: google_sheets."
        )
        
        # This returns a pure Python object matching our Blueprint schema
        blueprint = await self.structured_llm.ainvoke([
            ("system", system_msg),
            ("human", user_prompt)
        ])
        return blueprint