"""
GPT/LLM Tool for intelligent data processing in workflows.

Allows workflows to analyze, summarize, and format data using AI
before posting to social media or sending messages.
"""

from openai import AsyncOpenAI
import os
from typing import Dict, Any, Optional
from .base import BaseTool


# Pre-defined personas for common use cases
DEFAULT_PERSONAS = {
    "professional": "a professional business analyst who communicates clearly and concisely",
    "friendly": "a friendly and approachable tech enthusiast who uses emojis and casual language",
    "formal": "a formal corporate representative who maintains professional tone",
    "creative": "a creative content creator who writes engaging and viral-worthy posts",
    "technical": "a technical expert who explains complex topics simply",
    "casual": "a casual and relatable person who speaks naturally",
}


class GPTTool(BaseTool):
    def __init__(self):
        """Initialize OpenAI client for GPT processing."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ [GPTTool] Warning: OPENAI_API_KEY not set")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
            print("✅ [GPTTool] Initialized")

    @property
    def service_name(self) -> str:
        return "gpt"

    async def execute(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GPT task based on task name."""
        print(f"\n🧠 [GPTTool] Executing task: {task}")
        print(f"📊 [GPTTool] Parameters: {params}")

        if not self.client:
            return {
                "status": "error",
                "message": "OpenAI client not initialized. Check OPENAI_API_KEY",
            }

        try:
            # Support both process_text and process_data for backward compatibility
            if task in ["process_text", "process_data"]:
                result = await self._process(
                    input_data=params.get("input_data", ""),
                    persona=params.get("persona"),
                    output_format=params.get("output_format", "text"),
                    instructions=params.get("instructions"),
                    temperature=params.get("temperature", 0.7),
                )
                return {"status": "success", **result}
            else:
                return {"status": "error", "message": f"Unknown task: {task}"}

        except Exception as e:
            print(f"❌ [GPTTool] Execution error: {e}")
            return {"status": "error", "message": str(e)}

    async def _process(
        self,
        input_data: str,
        persona: Optional[str] = None,
        output_format: str = "text",
        instructions: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Process text using GPT with custom persona and formatting.

        Args:
            input_data: Raw data to process (can be JSON string, plain text, etc.)
            persona: User's brand voice or pre-defined persona key
            output_format: "text", "json", or "markdown"
            instructions: Specific task instructions
            temperature: Creativity level (0-1, default 0.7)

        Returns:
            Dict with processed_text and metadata
        """
        print(f"🧠 [GPTTool] Processing with persona: {persona}")
        print(f"📋 [GPTTool] Instructions: {instructions}")
        print(f"📊 [GPTTool] Output format: {output_format}")

        try:
            # Build system message
            system_parts = []

            # Add persona
            if persona:
                # Check if it's a pre-defined persona
                if persona.lower() in DEFAULT_PERSONAS:
                    system_parts.append(f"You are {DEFAULT_PERSONAS[persona.lower()]}.")
                else:
                    # Use custom persona
                    system_parts.append(f"You are {persona}.")

            # Add format instructions
            if output_format == "json":
                system_parts.append(
                    "Always respond with valid JSON. Do not include markdown code blocks or explanations."
                )
            elif output_format == "markdown":
                system_parts.append("Format your response in markdown.")

            # Add user instructions
            if instructions:
                system_parts.append(instructions)

            system_message = (
                " ".join(system_parts)
                if system_parts
                else "You are a helpful assistant."
            )

            print(f"💬 [GPTTool] System message: {system_message[:100]}...")

            # Call GPT
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": str(input_data)},
                ],
                temperature=temperature,
            )

            processed_text = response.choices[0].message.content

            print(f"✅ [GPTTool] Processed {len(processed_text)} characters")

            return {
                "processed_text": processed_text,
                "tokens_used": response.usage.total_tokens,
                "model": response.model,
            }

        except Exception as e:
            print(f"❌ [GPTTool] Processing error: {e}")
            raise Exception(f"GPT processing failed: {str(e)}")
