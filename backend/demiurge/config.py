"""
Demiurge Configuration
Central configuration management using Pydantic Settings
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Database
    database_url: str = "postgresql://demiurge:demiurge_secret@localhost:5432/demiurge"

    # Claude API
    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 2000
    claude_temperature: float = 0.7

    # DALL-E API
    dalle_api_key: str = ""
    dalle_model: str = "dall-e-3"
    dalle_size: str = "1024x1024"
    dalle_quality: str = "standard"
    dalle_style: str = "vivid"

    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Debate cycle settings
    cycle_duration_seconds: int = 60  # Real-time cycle duration
    proposal_phase_seconds: int = 15
    challenge_phase_seconds: int = 20
    voting_phase_seconds: int = 15
    result_phase_seconds: int = 10

    # World settings
    world_size: float = 100.0  # World extends from -50 to +50 on X and Z
    max_structures: int = 500
    structure_spawn_distance: float = 5.0  # Min distance between structures

    # WebSocket
    ws_heartbeat_interval: int = 30
    max_ws_connections: int = 100

    # Image generation
    image_generation_enabled: bool = True
    images_per_cycle: int = 1
    image_output_dir: str = "public/images"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Convenience access
settings = get_settings()
