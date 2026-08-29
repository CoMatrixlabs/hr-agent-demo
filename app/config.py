"""Runtime settings for the HR assistant.

Baseline is a benign HR-policy assistant: it answers questions from the HR policy /
FAQ knowledge base and reports the company holiday calendar. It holds no employee
PII, has no employee-keyed lookups, and has no data-export or write capability.
Sensitive tools, when added, require human approval.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.2          # low for tool-driving / effectful paths
    max_tool_iterations: int = 6

    require_tool_approval: bool = True        # human-in-the-loop for any write / effectful tool

    log_level: str = "INFO"

    class Config:
        env_prefix = "HR_AGENT_"


settings = Settings()
