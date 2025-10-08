from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from typing import Annotated
from pydantic import Field, ValidationError
import requests
import urllib3
import json

from schemas import ZosmfJsonDataSetList, ZosmfJsonDataSetMemberList
from client import ZosmfClient

class FilesTools:
    def __init__(self, mcp_app: FastMCP, zosmf_client: ZosmfClient):
        self.zosmf_client = zosmf_client
        mcp_app.tool(self.restfiles_ds_list)
        mcp_app.tool(self.restfiles_ds_memberlist)
        mcp_app.tool(self.restfiles_ds_get)

    def restfiles_ds_list(
        self,
        dslevel: Annotated[
            str,
            Field(
                description="The search parameter to identify the data sets to be listed. This can be a fully qualified data set name or a partial name with wildcards."
            ),
        ],
        volser: Annotated[
            str | None,
            Field(
                description="An optional parameter to specify the volume serials to be searched."
            ),
        ] = None,
        start: Annotated[
            str | None,
            Field(
                description="An optional parameter to specify the first data set name to return in the response."
            ),
        ] = None,
        max_items: Annotated[
            int | None,
            Field(description="Specifies the maximum number of items to return."),
        ] = None,
        attributes: Annotated[
            str,
            Field(
                description="Specifies a comma-separated list of attributes to be returned for each data set. Valid values include 'base' (for basic attributes) and 'vol' (for volume information). Append ',total' to any value (e.g., 'base,total') to include the total number of data sets found."
            ),
        ] = "base",
    ) -> ZosmfJsonDataSetList:
        """Lists z/OS data sets.""" 
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restfiles/ds"
        params = {
            "dslevel": dslevel,
            "volser": volser,
            "start": start,
        }
        params = {k: v for k, v in params.items() if v is not None}

        def api_call(headers):
            if max_items:
                headers["X-IBM-Max-Items"] = str(max_items)
            if attributes:
                headers["X-IBM-Attributes"] = attributes
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.get(url, headers=headers, params=params, verify=False)

        try:
            result = self.zosmf_client._call_zosmf_api(api_call)
            return ZosmfJsonDataSetList(**result)
        except ValidationError as e:
            raise ToolError(f"JSON Validation error: {e}")

    def restfiles_ds_memberlist(
        self,
        dataset_name: Annotated[
            str,
            Field(description="The dataset name to be read."),
        ],
        max_items: Annotated[
            int | None,
            Field(description="Specifies the maximum number of items to return."),
        ] = None,
        start: Annotated[
            str | None,
            Field(
                description="An optional parameter to specify the first member name to return in the response."
            ),
        ] = None,
        pattern: Annotated[
            str | None,
            Field(
                description=("An optional search parameter restricts the returned member names to only the names that match the given pattern. "
                             "The syntax of this argument is the same as \"pattern\" parameter of the ISPF LMMLIST service.")
            )
        ] = None,
        attributes: Annotated[
            str,
            Field(
                description=("Specifies a comma-separated list of attributes to be returned for each member. "
                             "Valid values include 'base' (for basic attributes) and 'member' (for only member names). "
                             "Append ',total' to any value (e.g., 'base,total') to include the total number of members found.")
            ),
        ] = "base",
    ) -> ZosmfJsonDataSetMemberList:
        """List PDS member on z/OS."""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restfiles/ds/{dataset_name}/member"
        params = {
            "start": start,
            "pattern": pattern,
        }
        params = {k: v for k, v in params.items() if v is not None}

        def api_call(headers):
            if max_items:
                headers["X-IBM-Max-Items"] = str(max_items)
            if attributes:
                headers["X-IBM-Attributes"] = attributes
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.get(url, headers=headers, params=params, verify=False)

        try:
            result = self.zosmf_client._call_zosmf_api(api_call)
            return ZosmfJsonDataSetMemberList(**result)
        except ValidationError as e:
            raise ToolError(f"JSON Validation error: {e}")

    def restfiles_ds_get(
        self,
        dataset_name: Annotated[
            str,
            Field(description="The dataset name to be read."),
        ],
        member_name: Annotated[
            str | None,
            Field(
                description="An optional parameter to specify the member name to be read. Required only if the dataset is a PDS."
            ),
        ] = None,
        volser: Annotated[
            str | None,
            Field(
                description="An optional parameter to specify the volume serials which contains the data set. If it's omitted, the dataset will be catalog searched."
            ),
        ] = None,
    ) -> str:
        """Read a single PS data set or PDS member from z/OS."""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restfiles/ds"
        if volser is not None:
            url += f"/-{volser}"
        url += f"/{dataset_name}"
        if member_name is not None:
            url += f"({member_name})"

        def api_call(headers):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.get(url, headers=headers, verify=False)

        return self.zosmf_client._call_zosmf_api(api_call)
