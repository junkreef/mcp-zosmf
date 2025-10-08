from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from typing import Annotated
from pydantic import Field, ValidationError
import requests
import urllib3
import json

from schemas import ZosmfJsonConsoleIssueSyncCommand
from client import ZosmfClient

class ConsoleTools:
    def __init__(self, mcp_app: FastMCP, zosmf_client: ZosmfClient):
        self.zosmf_client = zosmf_client
        mcp_app.tool(self.restconsoles_issue_command)

    def restconsoles_issue_command(
        self,
        command: Annotated[
            str,
            Field(description="The system command to be issued."),
        ],
        timeout: Annotated[
            int,
            Field(
                description="Specifies how long the console attempts to detect responces in seconds. Default is 5 sec."
            ),
        ] = 5,
    ) -> ZosmfJsonConsoleIssueSyncCommand:
        """Issue a command to z/OS from a system console."""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restconsoles/consoles/defcn"
        json_body = {"cmd": command, "detect-time": str(timeout)}

        def api_call(headers):
            headers["Content-Type"] = "application/json"
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.put(url, json=json_body, headers=headers, verify=False)

        try:
            result = self.zosmf_client._call_zosmf_api(api_call)
            return ZosmfJsonConsoleIssueSyncCommand(**result)
        except ValidationError as e:
            raise ToolError(f"JSON Validation error: {e}")
