from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class ZosmfSettings(BaseSettings):
    """
    Settings for the MCP z/OSMF Server.

    Settings are loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # z/OSMF Client settings
    zosmf_host: str = "192.168.250.200:10443"
    zosmf_username: str = ""
    zosmf_password: str = ""

    # MCP Server settings
    transport: Literal["stdio", "http", "sse", "streamable-http"] = "streamable-http"
    port: int = 18001

settings = ZosmfSettings()