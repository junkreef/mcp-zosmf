import requests
import urllib3
from fastmcp.exceptions import ToolError
from typing import Callable, Any

class ZosmfClient:
    def __init__(self, zosmf_host, username, password, max_retries=3):
        self.zosmf_host = zosmf_host
        self.username = username
        self.password = password
        self.max_retries = max_retries
        self.jwt_token = None

    def _call_zosmf_api(self, api_call: Callable[..., requests.Response]) -> Any:
        """Wrapper for z/OSMF API calls to handle authentication and retries."""
        if not self.jwt_token:
            self.authenticate()

        for attempt in range(self.max_retries):
            try:
                headers = {"Authorization": f"Bearer {self.jwt_token}"}
                response = api_call(headers)
                response.raise_for_status()
                # Check if response is empty
                if not response.content:
                    return None
                # Attempt to return JSON, fall back to text
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    return response.text
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and attempt < self.max_retries - 1:
                    self.authenticate()  # Refresh token
                    continue  # Retry
                raise ToolError(
                    f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
                )
            except requests.exceptions.RequestException as e:
                raise ToolError(f"An error occurred while requesting: {e}")
        raise ToolError(f"API call failed after {self.max_retries} retries.")

    def authenticate(self) -> str:
        """Get JWT from z/OS by BASIC auth."""
        url = f"https://{self.zosmf_host}/zosmf/services/authenticate"

        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            response = requests.post(url, auth=(self.username, self.password), verify=False)
            response.raise_for_status()

            self.jwt_token = response.cookies.get("jwtToken")

            return f"Success"
        except requests.exceptions.HTTPError as e:
            raise ToolError(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )
        except requests.exceptions.RequestException as e:
            raise ToolError(f"An error occurred while requesting: {e}")
