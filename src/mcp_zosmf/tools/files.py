from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from typing import Annotated
from pydantic import Field, ValidationError
import requests
import urllib3
import json

import urllib.parse

from ..schemas import ZosmfJsonDataSetList, ZosmfJsonDataSetMemberList, ZosmfJsonUnixFileList
from ..client import ZosmfClient


class FilesTools:
    def __init__(self, mcp_app: FastMCP, zosmf_client: ZosmfClient):
        self.zosmf_client = zosmf_client
        mcp_app.tool(self.restfiles_ds_list)
        mcp_app.tool(self.restfiles_ds_memberlist)
        mcp_app.tool(self.restfiles_ds_get)
        mcp_app.tool(self.restfiles_ds_put)
        mcp_app.tool(self.restfiles_fs_list)
        mcp_app.tool(self.restfiles_fs_get)
        mcp_app.tool(self.restfiles_fs_post)
        mcp_app.tool(self.restfiles_fs_put)
        mcp_app.tool(self.restfiles_fs_delete)


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

    def restfiles_ds_put(
        self,
        dataset_name: Annotated[
            str,
            Field(description="The dataset name to be written."),
        ],
        body: Annotated[
            str,
            Field(description="The content to be written to the data set or member."),
        ],
        member_name: Annotated[
            str | None,
            Field(
                description="An optional parameter to specify the member name to be written. Required only if the dataset is a PDS."
            ),
        ] = None,
        volser: Annotated[
            str | None,
            Field(
                description="An optional parameter to specify the volume serials which contains the data set. If it's omitted, the dataset will be catalog searched."
            ),
        ] = None,
        binary: Annotated[
            bool,
            Field(
                description="Whether the data should be written in binary mode. Default is False (text mode)."
            ),
        ] = False,
    ) -> str:
        """Write data to a single PS data set or PDS member on z/OS."""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restfiles/ds"
        if volser is not None:
            url += f"/-{volser}"
        url += f"/{dataset_name}"
        if member_name is not None:
            url += f"({member_name})"

        def api_call(headers):
            headers["X-IBM-Data-Type"] = "binary" if binary else "text"
            headers["Content-Type"] = (
                "application/octet-stream" if binary else "text/plain"
            )
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.put(url, headers=headers, data=body, verify=False)

        return self.zosmf_client._call_zosmf_api(api_call)

    def restfiles_fs_list(
        self,
        path: Annotated[
            str,
            Field(
                description="The directory containing the files and directories to be listed. This is required and can consist of one or more directories in the hierarchical file system structure, or a fully qualified file name."
            ),
        ],
        depth: Annotated[
            int | None,
            Field(
                description="The default is 1 (list files/dirs in the path). Set to 0 to list all subdirectories under path recursively."
            ),
        ] = 1,
        limit: Annotated[
            int | None,
            Field(
                description="Specifies the maximum number of items to return."
            ),
        ] = None,
        filesys: Annotated[
            str | None,
            Field(
                description="Default is 'same' (only list sub directories on the same file system). 'all' lists all sub directories."
            ),
        ] = None,
        symlinks: Annotated[
            str | None,
            Field(
                description="Default is 'follow' (symbolic links are followed). If 'report', symbolic links are returned but not followed."
            ),
        ] = None,
        type: Annotated[
            str | None,
            Field(
                description="Filter entries based on type: 'c' Character special, 'd' Directory, 'f' Regular file, 'l' Symbolic link, 'p' FIFO, 's' Socket."
            ),
        ] = None,
        name: Annotated[
            str | None,
            Field(
                description="Filter entries matching the given pattern (glob) according to fnmatch() rules."
            ),
        ] = None,
    ) -> ZosmfJsonUnixFileList:
        """List files and directories in a UNIX file path."""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restfiles/fs"
        params = {
            "path": path,
            "depth": depth,
            "limit": limit,
            "filesys": filesys,
            "symlinks": symlinks,
            "type": type,
            "name": name,
        }
        params = {k: v for k, v in params.items() if v is not None}

        def api_call(headers):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.get(url, headers=headers, params=params, verify=False)

        try:
            result = self.zosmf_client._call_zosmf_api(api_call)
            return ZosmfJsonUnixFileList(**result)
        except ValidationError as e:
            raise ToolError(f"JSON Validation error: {e}")

    def restfiles_fs_get(
        self,
        filepath: Annotated[
            str,
            Field(description="The fully qualified path and name of the file to be read."),
        ],
        binary: Annotated[
            bool,
            Field(
                description="Whether the data should be read in binary mode. Default is False (text mode)."
            ),
        ] = False,
    ) -> str:
        """Retrieve the contents of a z/OS UNIX file."""
        clean_path = urllib.parse.quote(filepath, safe='/')
        if not clean_path.startswith('/'):
            clean_path = f"/{clean_path}"
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restfiles/fs{clean_path}"

        def api_call(headers):
            headers["X-IBM-Data-Type"] = "binary" if binary else "text"
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.get(url, headers=headers, verify=False)

        return self.zosmf_client._call_zosmf_api(api_call)

    def restfiles_fs_post(
        self,
        filepath: Annotated[
            str,
            Field(description="The fully qualified path and name of the file or directory to be created."),
        ],
        type: Annotated[
            str,
            Field(
                description="The type of resource to create. Valid values are 'file' or 'directory' (or 'dir')."
            ),
        ],
        mode: Annotated[
            str | None,
            Field(
                description="Optional permission bits to be used (e.g. 'rwxr-xr-x')."
            ),
        ] = None,
    ) -> str:
        """Create a UNIX file or directory on z/OS."""
        clean_path = urllib.parse.quote(filepath, safe='/')
        if not clean_path.startswith('/'):
            clean_path = f"/{clean_path}"
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restfiles/fs{clean_path}"

        body = {"type": type}
        if mode is not None:
            body["mode"] = mode

        def api_call(headers):
            headers["Content-Type"] = "application/json"
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.post(url, headers=headers, json=body, verify=False)

        self.zosmf_client._call_zosmf_api(api_call)
        return f"Successfully created {type} at {filepath}"

    def restfiles_fs_put(
        self,
        filepath: Annotated[
            str,
            Field(description="The fully qualified path and name of the file to write to."),
        ],
        body: Annotated[
            str,
            Field(description="The content to be written to the file."),
        ],
        binary: Annotated[
            bool,
            Field(
                description="Whether the data should be written in binary mode. Default is False (text mode)."
            ),
        ] = False,
    ) -> str:
        """Write data to a z/OS UNIX file."""
        clean_path = urllib.parse.quote(filepath, safe='/')
        if not clean_path.startswith('/'):
            clean_path = f"/{clean_path}"
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restfiles/fs{clean_path}"

        def api_call(headers):
            headers["X-IBM-Data-Type"] = "binary" if binary else "text"
            headers["Content-Type"] = (
                "application/octet-stream" if binary else "text/plain"
            )
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.put(url, headers=headers, data=body, verify=False)

        self.zosmf_client._call_zosmf_api(api_call)
        return f"Successfully wrote to {filepath}"

    def restfiles_fs_delete(
        self,
        filepath: Annotated[
            str,
            Field(description="The fully qualified path and name of the file or directory to be deleted."),
        ],
        recursive: Annotated[
            bool,
            Field(
                description="If True, deletes a directory and its contents recursively. If False, only deletes an empty directory or a file."
            ),
        ] = False,
    ) -> str:
        """Delete a UNIX file or directory on z/OS."""
        clean_path = urllib.parse.quote(filepath, safe='/')
        if not clean_path.startswith('/'):
            clean_path = f"/{clean_path}"
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restfiles/fs{clean_path}"

        def api_call(headers):
            if recursive:
                headers["X-IBM-Option"] = "recursive"
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.delete(url, headers=headers, verify=False)

        self.zosmf_client._call_zosmf_api(api_call)
        return f"Successfully deleted {filepath}"

