from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from typing import Annotated
from pydantic import Field, ValidationError
import requests
import urllib3
import json

from schemas import ZosmfJsonJob, ZosmfJsonJobFile
from client import ZosmfClient

class JobsTools:
    def __init__(self, mcp_app: FastMCP, zosmf_client: ZosmfClient):
        self.zosmf_client = zosmf_client
        mcp_app.tool(self.restjobs_job_status)
        mcp_app.tool(self.restjobs_jobs)
        mcp_app.tool(self.restjobs_jobs_files_list)
        mcp_app.tool(self.restjobs_jobs_file)
        mcp_app.tool(self.restjobs_jobs_submit_jcl)
        mcp_app.tool(self.restjobs_jobs_submit)

    def restjobs_job_status(
        self,
        jobname: Annotated[str, Field(description="The job name for the job.")],
        jobid: Annotated[str, Field(description="A specific job ID to retrieve.")],
        exec_data: Annotated[
            bool,
            Field(
                description="Optional flag to include execution data like submit time, start time, end time, and running system name. Default False"
            ),
        ] = False,
        step_data: Annotated[
            bool,
            Field(
                description="Optional flag to include information about each step in the job that completed, such as the step name, step number, and completion code. Default False"
            ),
        ] = False,
    ) -> ZosmfJsonJob:
        """Get a single JOB status from z/OS."""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restjobs/jobs/{jobname}/{jobid}"
        params = {
            "exec-data": "Y" if exec_data else "N",
            "step-data": "Y" if step_data else "N",
        }
        params = {k: v for k, v in params.items() if v is not None}

        def api_call(headers):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.get(url, headers=headers, params=params, verify=False)

        try:
            result = self.zosmf_client._call_zosmf_api(api_call)
            return ZosmfJsonJob(**result)
        except ValidationError as e:
            raise ToolError(f"JSON Validation error: {e}")

    def restjobs_jobs(
        self,
        owner: Annotated[
            str,
            Field(
                description="The user ID that owns the jobs (e.g., 'IBMUSER'). If it's omitted, no fillter for owner is applied."
            ),
        ] = "*",
        prefix: Annotated[
            str | None, Field(description="Job name prefix to filter by (e.g., 'MYJOB*').")
        ] = None,
        jobid: Annotated[
            str | None, Field(description="A specific job ID to retrieve.")
        ] = None,
        status: Annotated[
            str | None,
            Field(description="Filter by job status (e.g., 'ACTIVE', 'OUTPUT')."),
        ] = None,
        max_jobs: Annotated[
            int | None,
            Field(
                description="Maximum number of jobs to return. Default is 1000, however, it's 100 when exec-data is true."
            ),
        ] = None,
        exec_data: Annotated[
            bool,
            Field(
                description="Optional flag to include execution data like submit time, start time, end time, and running system name. Default False"
            ),
        ] = False,
    ) -> list[ZosmfJsonJob]:
        """Lists jobs on z/OS with optional filters."""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restjobs/jobs"
        params = {
            "owner": owner,
            "prefix": prefix,
            "jobid": jobid,
            "status": status,
            "max-jobs": max_jobs,
            "exec-data": "Y" if exec_data else "N",
        }
        params = {k: v for k, v in params.items() if v is not None}

        def api_call(headers):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.get(url, headers=headers, params=params, verify=False)

        try:
            jobs_data = self.zosmf_client._call_zosmf_api(api_call)
            return [ZosmfJsonJob(**job_data) for job_data in jobs_data]
        except ValidationError as e:
            raise ToolError(f"JSON Validation error: {e}")

    def restjobs_jobs_files_list(
        self,
        jobid: Annotated[str, Field(description="The job ID for the job.")],
        jobname: Annotated[str, Field(description="The job name for the job.")],
    ) -> list[ZosmfJsonJobFile]:
        """Lists spool files for a job on z/OS"""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restjobs/jobs/{jobname}/{jobid}/files"

        def api_call(headers):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.get(url, headers=headers, verify=False)

        try:
            file_data = self.zosmf_client._call_zosmf_api(api_call)
            return [ZosmfJsonJobFile(**data) for data in file_data]
        except ValidationError as e:
            raise ToolError(f"JSON Validation error: {e}")

    def restjobs_jobs_file(
        self,
        jobid: Annotated[str, Field(description="The job ID for the job.")],
        jobname: Annotated[str, Field(description="The job name for the job.")],
        id: Annotated[
            int | str,
            Field(
                description="Data set number (key), or just 'JCL' for submitted JCL source."
            ),
        ],
    ) -> str:
        """Get a spool file for a job on z/OS"""
        url = (
            f"https://{self.zosmf_client.zosmf_host}/zosmf/restjobs/jobs/{jobname}/{jobid}/files/{id}/records"
        )

        def api_call(headers):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.get(url, headers=headers, verify=False)

        return self.zosmf_client._call_zosmf_api(api_call)

    def restjobs_jobs_submit_jcl(
        self,
        jcl_source: Annotated[str, Field(description="The JCL to submit")],
    ) -> ZosmfJsonJob:
        """Submit a JCL job to z/OS"""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restjobs/jobs"

        def api_call(headers):
            headers["Content-Type"] = "text/plain"
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.put(url, data=jcl_source, headers=headers, verify=False)

        try:
            result = self.zosmf_client._call_zosmf_api(api_call)
            return ZosmfJsonJob(**result)
        except ValidationError as e:
            raise ToolError(f"JSON Validation error: {e}")

    def restjobs_jobs_submit(
        self,
        file_name: Annotated[
            str,
            Field(description="The dataset name, PDS member, or unix file name to submit."),
        ],
        file_type: Annotated[
            str, Field(description="The type of file to submit. MVS or unix.")
        ],
    ) -> ZosmfJsonJob:
        """Submit a dataset, PDS member, or unix file name as job to z/OS"""
        url = f"https://{self.zosmf_client.zosmf_host}/zosmf/restjobs/jobs"

        if file_type == "MVS":
            body = {"file": f"//'{file_name}'"}
        else:
            body = {"file": f"{file_name}"}

        def api_call(headers):
            headers["Content-Type"] = "application/json"
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return requests.put(url, json=body, headers=headers, verify=False)

        try:
            result = self.zosmf_client._call_zosmf_api(api_call)
            return ZosmfJsonJob(**result)
        except ValidationError as e:
            raise ToolError(f"JSON Validation error: {e}")
