import argparse
import requests
import urllib3
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from typing import Annotated, Callable, Any
from pydantic import Field, BaseModel, ValidationError
import time
import json

# Create an MCP server based on the QuickStart guide
app = FastMCP("MCP z/OSMF Server")
app.settings.stateless_http = True


username = ""
password = ""
jwt_token = ""

zosmf_host = "192.168.250.200:10443"
MAX_RETRIES = 3


class ZosmfJsonJob(BaseModel):
    jobid: Annotated[str, Field(description="The job ID for the job.")]
    jobname: Annotated[str, Field(description="The job name for the job.")]
    subsystem: Annotated[
        str | None, Field(description="The subsystem that the job is defined to.")
    ] = None
    owner: Annotated[str, Field(description="The owner of the job.")]
    status: Annotated[str, Field(description="The status of the job.")]
    type: Annotated[
        str, Field(description="The type of the job, for example, JOB, STC, or TSU.")
    ]
    job_class: Annotated[
        str | None, Field(alias="class", description="The class for the job.")
    ] = None
    retcode: Annotated[
        str | None, Field(description="The return code for the job.")
    ] = None
    url: Annotated[str, Field(description="URL for this job instance.")]
    files_url: Annotated[
        str,
        Field(
            alias="files-url",
            description="URL for the spool files for this job instance.",
        ),
    ]
    job_correlator: Annotated[
        str,
        Field(
            alias="job-correlator",
            description="Job correlator. If this value is null, the job was submitted to JES3.",
        ),
    ]
    phase: Annotated[
        int | None,
        Field(description="An integer that represents the current phase of the job."),
    ]
    phase_name: Annotated[
        str | None,
        Field(alias="phase-name", description="The name of the current job phase."),
    ]
    step_data: Annotated[
        str | None,
        Field(
            alias="step-data",
            description="Step data information. Provides information about each step in the job, such as the step name, step number, and completion code. ",
        ),
    ] = None
    exec_system: Annotated[
        str | None,
        Field(
            alias="exec-system", description="The system on which the job is executing."
        ),
    ] = None
    exec_member: Annotated[
        str | None,
        Field(
            alias="exec-member", description="The member on which the job is executing."
        ),
    ] = None
    exec_submitted: Annotated[
        str | None,
        Field(
            alias="exec-submitted",
            description="Time when the job was submitted to run (the input end time).",
        ),
    ] = None
    exec_started: Annotated[
        str | None,
        Field(alias="exec-started", description="Time when job execution started."),
    ] = None
    exec_ended: Annotated[
        str | None,
        Field(alias="exec-ended", description="Time when job execution ended."),
    ] = None
    reason_not_running: Annotated[
        str | None,
        Field(
            alias="reason-not-running",
            description="Text identifying one or more reasons why the job is not running.",
        ),
    ] = None


class ZosmfJsonJobFile(BaseModel):
    jobname: Annotated[str, Field(description="Job name.")]
    recfm: Annotated[
        str | None,
        Field(
            description="Record format of the file. The first character of the returned string is one of the following: F Fixed length records V Variable length records U Undefined length records. One or more subsequent characters might also be present in the returned string (in this order): B File has blocked records. S File has standard records (if fixed length format) or spanned records (if variable length format). M File has machine print-control characters. A File has ASA (ANSI) print-control characters. Generally, the B (blocked) and S (standard or spanned) characters are not present for JES spool files. Also, the M (machine) and A (ASA) characters are mutually exclusive."
        ),
    ] = None
    byte_count: Annotated[
        int,
        Field(
            alias="byte-count",
            description="Number of bytes on spool consumed by the spool file. The value can be zero (0).",
        ),
    ]
    record_count: Annotated[
        int,
        Field(
            alias="record-count",
            description="Number of records in the spool file. The value can be zero (0).",
        ),
    ]
    job_correlator: Annotated[
        str | None,
        Field(
            alias="job-correlator",
            description="Job correlator. If this value is null, the job was submitted to JES3.",
        ),
    ] = None
    job_class: Annotated[
        str | None,
        Field(alias="class", description="Class that is assigned to the spool file."),
    ] = None
    jobid: Annotated[str, Field(description="Job ID.")]
    id: Annotated[int, Field(description="Data set number (key).")]
    ddname: Annotated[str, Field(description="DDNAME for the data set creation.")]
    records_url: Annotated[
        str,
        Field(
            alias="records-url",
            description="Resource URL for retrieving the spool file contents for the job.",
        ),
    ]
    lrecl: Annotated[
        int | None,
        Field(
            description="Specifies the length, in bytes, for fixed-length records and the maximum length for variable-length records."
        ),
    ] = None
    subsystem: Annotated[
        str | None,
        Field(
            description="The primary or secondary JES subsystem. If the value is null, the job was processed by the primary subsystem."
        ),
    ] = None
    stepname: Annotated[
        str | None,
        Field(description="Step name for the step that created this data set."),
    ] = None
    procstep: Annotated[
        str | None,
        Field(description="Procedure name for the step that created this data set."),
    ] = None


class ZosmfJsonDataSet(BaseModel):
    dsname: Annotated[str, Field(description="Data set name.")]
    vol: Annotated[str | None, Field(description="Volume serial")] = None
    used: Annotated[
        int | None, Field(description="Percentage of used tracks or pages (PDSE)")
    ] = None
    extx: Annotated[
        int | None, Field(description="Number of extents used, long format (5 bytes)")
    ] = None
    cdate: Annotated[str | None, Field(description="Creation date")] = None
    edate: Annotated[str | None, Field(description="Expiration date")] = None
    rdate: Annotated[str | None, Field(description="Date last referenced")] = None
    migr: Annotated[
        str | None,
        Field(
            description="Whether the data set is migrated (YES or NO) based on the value of the VOLUME_OF_MIGRATED_DATA_SETS keyword in the ISPF configuration table. If the volume name of the data set matches the value of VOLUME_OF_MIGRATED_DATA_SETS, ZDLMIGR is set to YES, otherwise it is set to NO."
        ),
    ] = None
    dsntp: Annotated[
        str | None, Field(description="Dsname type (PDS, LIBRARY, or ' ')")
    ] = None
    spacu: Annotated[str | None, Field(description="Space units")] = None
    mvol: Annotated[
        str | None,
        Field(description="Whether the data set is multivolume (Y) or not (N)"),
    ] = None
    ovf: Annotated[
        str | None, Field(description="Space overflow indicator (YES or NO)")
    ] = None
    dsorg: Annotated[str | None, Field(description="Data set organization")] = None
    recfm: Annotated[str | None, Field(description="Record format")] = None
    lrecl: Annotated[int | None, Field(description="Logical record length")] = None
    blksz: Annotated[int | None, Field(description="Block size")] = None
    sizex: Annotated[
        int | None, Field(description="Data set size in tracks, long format (12 bytes)")
    ] = None
    catnm: Annotated[
        str | None,
        Field(description="Name of the catalog where the data set is located"),
    ] = None
    dev: Annotated[str | None, Field(description="Device type")] = None


class ZosmfJsonDataSetMember(BaseModel):
    member: Annotated[str, Field(description="member name.")]
    vers: Annotated[
        int | None, Field(description="Version number; a number from 1 to 99.")
    ] = None
    mod: Annotated[
        int | None, Field(description="Modification level; a number from 0 to 99.")
    ] = None
    c4date: Annotated[
        str | None, Field(description="Creation date in 4-character year format")
    ] = None
    m4date: Annotated[
        str | None, Field(description="Last change date in 4-character year format")
    ] = None
    cnorc: Annotated[
        int | None,
        Field(description="Current number of records; a number from 0 to 65 535."),
    ] = None
    inorc: Annotated[
        int | None,
        Field(description="Beginning number of records; a number from 0 to 65 535."),
    ] = None
    mnorc: Annotated[
        int | None,
        Field(description="Number of changed records; a number from 0 to 65 535."),
    ] = None
    mtime: Annotated[
        str | None,
        Field(description="Last change time; a character value in the format hh:mm."),
    ] = None
    msec: Annotated[
        str | None,
        Field(
            description="Seconds value of the last change time. This is a two character field."
        ),
    ] = None
    user: Annotated[
        str | None,
        Field(
            description="User ID of last user to change the given member; an alphanumeric field with a maximum length of 7 characters."
        ),
    ] = None
    sclm: Annotated[
        str | None,
        Field(
            description="Indicates whether the member was last modified by SCLM or ISPF. A value of Y indicates the last update was made through SCLM. A value of N indicates that the last update was made."
        ),
    ] = None
    ac: Annotated[
        str | None,
        Field(
            alias="ac",
            description="A 2-character field containing the authorization code of the member.",
        ),
    ] = None
    alias_of: Annotated[
        str | None,
        Field(
            alias="alias-of",
            description="An 8-character field containing the name of the real member that this member is an alias of. If the member is not an alias this field is blank.",
        ),
    ] = None
    amode: Annotated[
        str | None,
        Field(description="A 3-character field containing the AMODE of the member."),
    ] = None
    attr: Annotated[
        str | None,
        Field(
            description="A 20-character field containing the load module attributes. The attributes are 2-character strings separated by blanks. These strings can appear in the attribute string: NX Not executable OL Only Loadable OV Overlay RF Refreshable RN Reentrant RU Reusable SC Scatter Load TS Test"
        ),
    ] = None
    rmode: Annotated[
        str | None,
        Field(description="A 3-character field containing the RMODE of the member."),
    ] = None
    size: Annotated[
        str | None,
        Field(description="An 8-character field containing the load module size in hex."),
    ] = None
    ttr: Annotated[
        str | None,
        Field(description="A 6-character field containing the TTR of the member."),
    ] = None
    ssi: Annotated[
        str | None,
        Field(
            description="An 8-character field containing the SSI information for a load module."
        ),
    ] = None


class ZosmfJsonDataSetMemberList(BaseModel):
    items: Annotated[
        list[ZosmfJsonDataSetMember],
        Field(
            description="An array where each element contains the following key:value pairs"
        ),
    ]
    returnedRows: Annotated[
        int, Field(description="Number of rows that were returned for this request.")
    ]
    moreRows: Annotated[
        bool | None, Field(description="True, if more rows are available to return.")
    ] = None
    totalRows: Annotated[
        int | None,
        Field(
            description='Total number of data sets found matching the dslevel and volser criteria. If you specify ",total" as suffix in X-IBM-Attributes header, like "dsname,total", or "base,total", or "vol,total".'
        ),
    ] = None


class ZosmfJsonDataSetList(BaseModel):
    items: Annotated[
        list[ZosmfJsonDataSet],
        Field(
            description="An array where each element contains the following key:value pairs"
        ),
    ]
    returnedRows: Annotated[
        int, Field(description="Number of rows that were returned for this request.")
    ]
    moreRows: Annotated[
        bool | None, Field(description="True, if more rows are available to return.")
    ] = None
    totalRows: Annotated[
        int | None,
        Field(
            description='Total number of data sets found matching the dslevel and volser criteria. If you specify ",total" as suffix in X-IBM-Attributes header, like "dsname,total", or "base,total", or "vol,total".'
        ),
    ] = None


class ZosmfJsonConsoleIssueSyncCommand(BaseModel):
    cmd_response: Annotated[
        str | None, Field(alias="cmd-response", description="Command response.")
    ] = None



def _call_zosmf_api(api_call: Callable[..., requests.Response]) -> Any:
    """Wrapper for z/OSMF API calls to handle authentication and retries."""
    global jwt_token
    if not jwt_token:
        services_authenticate()

    for attempt in range(MAX_RETRIES):
        try:
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = api_call(headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401 and attempt < MAX_RETRIES - 1:
                services_authenticate()  # Refresh token
                continue  # Retry
            raise ToolError(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )
        except requests.exceptions.RequestException as e:
            raise ToolError(f"An error occurred while requesting: {e}")
    raise ToolError(f"API call failed after {MAX_RETRIES} retries.")


def services_authenticate() -> str:
    """Get JWT from z/OS by BASIC auth."""
    global jwt_token

    url = f"https://{zosmf_host}/zosmf/services/authenticate"

    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.post(url, auth=(username, password), verify=False)
        response.raise_for_status()

        jwt_token = response.cookies.get("jwtToken")

        return f"Success"
    except requests.exceptions.HTTPError as e:
        raise ToolError(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        )
    except requests.exceptions.RequestException as e:
        raise ToolError(f"An error occurred while requesting: {e}")


@app.tool(
    annotations={
        "title": "Get a single JOB status from z/OS.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    }
)
def restjobs_job_status(
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
    url = f"https://{zosmf_host}/zosmf/restjobs/jobs/{jobname}/{jobid}"
    params = {
        "exec-data": "Y" if exec_data else "N",
        "step-data": "Y" if step_data else "N",
    }
    params = {k: v for k, v in params.items() if v is not None}

    def api_call(headers):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests.get(url, headers=headers, params=params, verify=False)

    try:
        result_text = _call_zosmf_api(api_call)
        result = json.loads(result_text) if result_text else {}
        return ZosmfJsonJob(**result)
    except ValidationError as e:
        raise ToolError(f"JSON Validation error: {e}")


@app.tool(
    annotations={
        "title": "Get a single JOB status from z/OS",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    }
)
def restjobs_jobs(
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
    url = f"https://{zosmf_host}/zosmf/restjobs/jobs"
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
        jobs_data_text = _call_zosmf_api(api_call)
        jobs_data = json.loads(jobs_data_text) if jobs_data_text else []
        return [ZosmfJsonJob(**job_data) for job_data in jobs_data]
    except ValidationError as e:
        raise ToolError(f"JSON Validation error: {e}")


@app.tool(
    annotations={
        "title": "List spool files for a job",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    }
)
def restjobs_jobs_files_list(
    jobid: Annotated[str, Field(description="The job ID for the job.")],
    jobname: Annotated[str, Field(description="The job name for the job.")],
) -> list[ZosmfJsonJobFile]:
    """Lists spool files for a job on z/OS"""
    url = f"https://{zosmf_host}/zosmf/restjobs/jobs/{jobname}/{jobid}/files"

    def api_call(headers):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests.get(url, headers=headers, verify=False)

    try:
        file_data_text = _call_zosmf_api(api_call)
        file_data = json.loads(file_data_text) if file_data_text else []
        return [ZosmfJsonJobFile(**data) for data in file_data]
    except ValidationError as e:
        raise ToolError(f"JSON Validation error: {e}")


@app.tool(
    annotations={
        "title": "Get a spool file or submitted JCL source for a job on z/OS",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    }
)
def restjobs_jobs_file(
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
        f"https://{zosmf_host}/zosmf/restjobs/jobs/{jobname}/{jobid}/files/{id}/records"
    )

    def api_call(headers):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests.get(url, headers=headers, verify=False)

    return _call_zosmf_api(api_call)


@app.tool(
    annotations={
        "title": "Submit a JCL job to z/OS",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True,
    }
)
def restjobs_jobs_submit_jcl(
    jcl_source: Annotated[str, Field(description="The JCL to submit")],
) -> ZosmfJsonJob:
    """Submit a JCL job to z/OS"""
    url = f"https://{zosmf_host}/zosmf/restjobs/jobs"

    def api_call(headers):
        headers["Content-Type"] = "text/plain"
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests.put(url, data=jcl_source, headers=headers, verify=False)

    try:
        result_text = _call_zosmf_api(api_call)
        result = json.loads(result_text) if result_text else {}
        return ZosmfJsonJob(**result)
    except ValidationError as e:
        raise ToolError(f"JSON Validation error: {e}")


@app.tool(
    annotations={
        "title": "Submit a dataset, PDS member, or unix file name as job to z/OS",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True,
    }
)
def restjobs_jobs_submit(
    file_name: Annotated[
        str,
        Field(description="The dataset name, PDS member, or unix file name to submit."),
    ],
    file_type: Annotated[
        str, Field(description="The type of file to submit. MVS or unix.")
    ],
) -> ZosmfJsonJob:
    """Submit a dataset, PDS member, or unix file name as job to z/OS"""
    url = f"https://{zosmf_host}/zosmf/restjobs/jobs"

    if file_type == "MVS":
        body = {"file": f"//'{file_name}'"}
    else:
        body = {"file": f"{file_name}"}

    def api_call(headers):
        headers["Content-Type"] = "application/json"
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests.put(url, json=body, headers=headers, verify=False)

    try:
        result_text = _call_zosmf_api(api_call)
        result = json.loads(result_text) if result_text else {}
        return ZosmfJsonJob(**result)
    except ValidationError as e:
        raise ToolError(f"JSON Validation error: {e}")


@app.tool(
    annotations={
        "title": "List z/OS data sets.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    }
)
def restfiles_ds_list(
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
    url = f"https://{zosmf_host}/zosmf/restfiles/ds"
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
        result_text = _call_zosmf_api(api_call)
        result = json.loads(result_text) if result_text else {}
        return ZosmfJsonDataSetList(**result)
    except ValidationError as e:
        raise ToolError(f"JSON Validation error: {e}")

@app.tool(
    annotations={
        "title": "List PDS member on z/OS.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    }
)
def restfiles_ds_memberlist(
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
            description="An optional search parameter restricts the returned member names to only the names that match the given pattern. \
                 The syntax of this argument is the same as \"pattern\" parameter of the ISPF LMMLIST service."
        )
    ] = None,
    attributes: Annotated[
        str,
        Field(
            description="Specifies a comma-separated list of attributes to be returned for each member. \
                Valid values include 'base' (for basic attributes) and 'member' (for only member names). \
                Append ',total' to any value (e.g., 'base,total') to include the total number of members found."
        ),
    ] = "base",
) -> ZosmfJsonDataSetMemberList:
    """List PDS member on z/OS."""
    url = f"https://{zosmf_host}/zosmf/restfiles/ds/{dataset_name}/member"
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
        result_text = _call_zosmf_api(api_call)
        result = json.loads(result_text) if result_text else {}
        return ZosmfJsonDataSetMemberList(**result)
    except ValidationError as e:
        raise ToolError(f"JSON Validation error: {e}")


@app.tool(
    annotations={
        "title": "Read a single PS data set or PDS member from z/OS.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    }
)
def restfiles_ds_get(
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
    url = f"https://{zosmf_host}/zosmf/restfiles/ds"
    if volser is not None:
        url += f"/-{volser}"
    url += f"/{dataset_name}"
    if member_name is not None:
        url += f"({member_name})"

    def api_call(headers):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests.get(url, headers=headers, verify=False)

    return _call_zosmf_api(api_call)


@app.tool(
    annotations={
        "title": "Issue a command to z/OS from a system console.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    }
)
def restconsoles_issue_command(
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
    url = f"https://{zosmf_host}/zosmf/restconsoles/consoles/defcn"
    json_body = {"cmd": command, "detect-time": str(timeout)}

    def api_call(headers):
        headers["Content-Type"] = "application/json"
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return requests.put(url, json=json_body, headers=headers, verify=False)

    try:
        result_text = _call_zosmf_api(api_call)
        result = json.loads(result_text) if result_text else {}
        return ZosmfJsonConsoleIssueSyncCommand(**result)
    except ValidationError as e:
        raise ToolError(f"JSON Validation error: {e}")


if __name__ == "__main__":
    # Note: This is for development.
    # With `reload=True`, the server will automatically restart when code changes.

    parser = argparse.ArgumentParser(description="Run the MCP z/OSMF Server.")
    parser.add_argument("--username", required=True, help="z/OSMF username")
    parser.add_argument("--password", required=True, help="z/OSMF password")
    parser.add_argument(
        "--transport",
        default="stdio",
        required=False,
        help="MCP transport type",
        choices=["stdio", "streamable-http", "sse"],
    )
    args = parser.parse_args()

    username = args.username
    password = args.password
    transport = args.transport

    app.run(transport=transport)
