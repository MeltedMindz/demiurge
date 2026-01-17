"""
Claude API Client for Agent Interactions
"""
import logging
from typing import Optional

import anthropic

from demiurge.config import settings

logger = logging.getLogger("demiurge.claude")


class ClaudeClient:
    """Client for Claude API interactions"""

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.claude_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens
        self.temperature = settings.claude_temperature

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from Claude"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return response.content[0].text

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Claude: {e}")
            raise

    async def generate_proposal(
        self,
        agent_name: str,
        agent_system_prompt: str,
        proposal_prompt: str
    ) -> str:
        """Generate a proposal for an agent"""
        return await self.generate(
            system_prompt=agent_system_prompt,
            user_prompt=proposal_prompt,
            max_tokens=500
        )

    async def generate_challenge(
        self,
        agent_name: str,
        agent_system_prompt: str,
        challenge_prompt: str
    ) -> str:
        """Generate a challenge for an agent"""
        return await self.generate(
            system_prompt=agent_system_prompt,
            user_prompt=challenge_prompt,
            max_tokens=200
        )

    async def generate_vote_reasoning(
        self,
        agent_name: str,
        agent_system_prompt: str,
        vote_prompt: str
    ) -> str:
        """Generate vote reasoning for an agent"""
        return await self.generate(
            system_prompt=agent_system_prompt,
            user_prompt=vote_prompt,
            max_tokens=150
        )
