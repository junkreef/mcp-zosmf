from pydantic import Field, BaseModel
from typing import Annotated

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
    ] = None
    phase_name: Annotated[
        str | None,
        Field(alias="phase-name", description="The name of the current job phase."),
    ] = None
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
            description=("Record format of the file. The first character of the returned string is one of the following: F Fixed length records V Variable length records U Undefined length records. "
                         "One or more subsequent characters might also be present in the returned string (in this order): B File has blocked records. S File has standard records (if fixed length format) or spanned records (if variable length format). "
                         "M File has machine print-control characters. A File has ASA (ANSI) print-control characters. Generally, the B (blocked) and S (standard or spanned) characters are not present for JES spool files. "
                         "Also, the M (machine) and A (ASA) characters are mutually exclusive.")
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
            description=("Whether the data set is migrated (YES or NO) based on the value of the VOLUME_OF_MIGRATED_DATA_SETS keyword in the ISPF configuration table. "
                         "If the volume name of the data set matches the value of VOLUME_OF_MIGRATED_DATA_SETS, ZDLMIGR is set to YES, otherwise it is set to NO.")
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
            description="""A 20-character field containing the load module attributes. The attributes are 2-character strings separated by blanks. These strings can appear in the attribute string: NX Not executable OL Only Loadable OV Overlay RF Refreshable RN Reentrant RU Reusable SC Scatter Load TS Test"""
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


class ZosmfJsonUnixFile(BaseModel):
    name: Annotated[str, Field(description="File or directory name.")]
    mode: Annotated[
        str | None,
        Field(description="Permissions indicating the file mode (e.g. drwxrwxrwx, -rw-r----)."),
    ] = None
    size: Annotated[
        int | None,
        Field(description="For regular files, the file's size in bytes. For other kinds of files, the value of this field is unspecified."),
    ] = None
    uid: Annotated[
        int | None,
        Field(description="The numeric user ID (UID) of the file's owner."),
    ] = None
    user: Annotated[
        str | None,
        Field(description="The user name of the file's owner got by UID."),
    ] = None
    gid: Annotated[
        int | None,
        Field(description="The numeric group ID (GID) of the file's group."),
    ] = None
    group: Annotated[
        str | None,
        Field(description="The group name of the file's group got by GID."),
    ] = None
    mtime: Annotated[
        str | None,
        Field(description="The most recent time the contents of the file were changed."),
    ] = None
    target: Annotated[
        str | None,
        Field(description="If the file is symlink, this indicates the really file/directory"),
    ] = None


class ZosmfJsonUnixFileList(BaseModel):
    items: Annotated[
        list[ZosmfJsonUnixFile],
        Field(description="JSON array of UNIX files and directories."),
    ]
    returnedRows: Annotated[
        int, Field(description="Number of rows that were returned for this request.")
    ]
    moreRows: Annotated[
        bool | None, Field(description="Optional property; set to true when more rows can be returned.")
    ] = None
    totalRows: Annotated[
        int | None, Field(description="Total number of rows that match the request.")
    ] = None


class ZosmfJsonConsoleIssueSyncCommand(BaseModel):
    cmd_response: Annotated[
        str | None, Field(alias="cmd-response", description="Command response.")
    ] = None

