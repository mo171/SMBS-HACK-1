import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class SocialMention(BaseModel):
    platform: str = Field(description="The platform (e.g., 'bluesky', 'instagram')")
    author: str = Field(
        description="The username of the person who mentioned the business"
    )
    text: str = Field(description="The content of the mention or message")
    uri: Optional[str] = Field(
        None, description="Platform-specific identifier for the message/post"
    )
    cid: Optional[str] = Field(None, description="Platform-specific content identifier")


class SocialReply(BaseModel):
    thought: str = Field(description="Internal reasoning for the reply")
    suggested_text: str = Field(description="The text content for the reply")
    needs_human_approval: bool = Field(
        default=False, description="True if the reply is sensitive or risky"
    )
    action_type: str = Field(description="POST_REPLY, CHECK_STOCK, etc.")


class SocialService:
    def __init__(self):
        self.system_instruction = (
            "You are a Brand Voice Assistant for a small business (Bharat Biz). "
            "Your goal is to reply to social media mentions professionally and helpfully. "
            "1. CONTEXT: You will receive the mention text and any available business context (like stock details). "
            "2. PERSONALITY: Be polite, helpful, and concise. "
            "3. SALES: If someone asks about availability, check the context provided. If available, encourage them to buy. "
            "4. PRIVACY: Do not share sensitive business data like profit margins or customer addresses. "
            "5. APPROVAL: If the mention is a complaint or complex, set 'needs_human_approval' to True."
        )

    async def draft_reply(
        self, mention: Dict[str, Any], business_context: str = ""
    ) -> SocialReply:
        """
        Drafts a reply to a social media mention.
        mention: { platform, author, text, ... }
        business_context: Stringified data (e.g., stock levels)
        """
        prompt = (
            f"Platform: {mention.get('platform')}\n"
            f"Customer (@{mention.get('author')}): {mention.get('text')}\n\n"
            f"Business Context:\n{business_context}\n\n"
            f"Draft a response."
        )

        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": prompt},
                ],
                response_format=SocialReply,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            logger.error(f"Error drafting social reply: {e}")
            return SocialReply(
                thought="Error occurred during generation.",
                suggested_text="I'm sorry, I'm having trouble processing that right now.",
                needs_human_approval=True,
                action_type="NONE",
            )


social_service = SocialService()
