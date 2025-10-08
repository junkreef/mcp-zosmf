from unittest.mock import Mock
from mcp_zosmf.tools.jobs import JobsTools
from mcp_zosmf.schemas import ZosmfJsonJob, ZosmfJsonJobFile
from fastmcp import FastMCP

def test_restjobs_job_status_success():
    """
    Tests the successful retrieval of a single job's status.
    """
    # 1. Setup Mocks
    # Mock for FastMCP app (needed for tool initialization)
    mock_app = Mock(spec=FastMCP)
    
    # Mock for ZosmfClient
    mock_zosmf_client = Mock()
    
    # Fake JSON response from the API
    fake_job_json = {
        "jobid": "JOB00123",
        "jobname": "TESTJOB",
        "owner": "USER1",
        "status": "OUTPUT",
        "type": "JOB",
        "url": "https://host/zosmf/restjobs/jobs/TESTJOB/JOB00123",
        "files-url": "https://host/zosmf/restjobs/jobs/TESTJOB/JOB00123/files",
        "job-correlator": "some.correlator.id"
    }
    
    # Configure the client's API wrapper to return the fake JSON
    mock_zosmf_client._call_zosmf_api.return_value = fake_job_json

    # 2. Instantiate the tool class with mocks
    jobs_tools = JobsTools(mock_app, mock_zosmf_client)

    # 3. Call the method under test
    result = jobs_tools.restjobs_job_status(jobname="TESTJOB", jobid="JOB00123")

    # 4. Assertions
    # Check if the result is an instance of the correct Pydantic model
    assert isinstance(result, ZosmfJsonJob)
    # Check if the content is correct
    assert result.jobid == "JOB00123"
    assert result.status == "OUTPUT"

    # Check if the API wrapper was called
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restjobs_jobs_success():
    """
    Tests the successful retrieval of a list of jobs.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()
    
    # Fake JSON response from the API (a list of jobs)
    # NOTE: This data is intentionally missing 'phase' and 'phase-name'
    # to align with the user's request to postpone the schema fix.
    # This test is expected to fail.
    fake_jobs_list_json = [
        {
            "jobid": "JOB00123",
            "jobname": "TESTJOB1",
            "owner": "USER1",
            "status": "OUTPUT",
            "type": "JOB",
            "url": "...",
            "files-url": "...",
            "job-correlator": "..."
        },
        {
            "jobid": "JOB00124",
            "jobname": "TESTJOB2",
            "owner": "USER1",
            "status": "ACTIVE",
            "type": "JOB",
            "url": "...",
            "files-url": "...",
            "job-correlator": "..."
        }
    ]
    
    mock_zosmf_client._call_zosmf_api.return_value = fake_jobs_list_json

    # 2. Instantiate the tool class
    jobs_tools = JobsTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = jobs_tools.restjobs_jobs(owner="USER1")

    # 4. Assertions
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], ZosmfJsonJob)
    assert result[0].jobname == "TESTJOB1"
    assert result[1].status == "ACTIVE"
    
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restjobs_jobs_files_list_success():
    """
    Tests the successful retrieval of a list of spool files for a job.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()
    
    # Fake JSON response
    fake_files_list_json = [
        {
            "jobname": "TESTJOB",
            "jobid": "JOB00123",
            "id": 102,
            "ddname": "JESMSGLG",
            "byte-count": 1234,
            "record-count": 56,
            "records-url": "..."
        },
        {
            "jobname": "TESTJOB",
            "jobid": "JOB00123",
            "id": 103,
            "ddname": "JESJCL",
            "byte-count": 500,
            "record-count": 20,
            "records-url": "..."
        }
    ]
    
    mock_zosmf_client._call_zosmf_api.return_value = fake_files_list_json

    # 2. Instantiate the tool class
    jobs_tools = JobsTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = jobs_tools.restjobs_jobs_files_list(jobname="TESTJOB", jobid="JOB00123")

    # 4. Assertions
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], ZosmfJsonJobFile)
    assert result[0].ddname == "JESMSGLG"
    assert result[1].id == 103
    
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restjobs_jobs_file_success():
    """
    Tests the successful retrieval of a job's spool file content.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()
    
    # Fake response from the API (plain text content)
    fake_spool_content = "JES2 JOB LOG...\n...CONTENT..."
    mock_zosmf_client._call_zosmf_api.return_value = fake_spool_content

    # 2. Instantiate the tool class
    jobs_tools = JobsTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = jobs_tools.restjobs_jobs_file(jobname="TESTJOB", jobid="JOB00123", id=102)

    # 4. Assertions
    assert result == fake_spool_content
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restjobs_jobs_submit_jcl_success():
    """
    Tests the successful submission of a JCL job.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()
    
    # Fake JSON response for the submitted job
    fake_submitted_job_json = {
        "jobid": "JOB00125",
        "jobname": "SUBMIT1",
        "owner": "USER1",
        "status": "INPUT",
        "type": "JOB",
        "url": "...", "files-url": "...", "job-correlator": "...",
    }
    mock_zosmf_client._call_zosmf_api.return_value = fake_submitted_job_json

    # 2. Instantiate the tool class
    jobs_tools = JobsTools(mock_app, mock_zosmf_client)
    
    jcl_to_submit = "//TESTJOB JOB ...\n// EXEC PGM=IEFBR14"

    # 3. Call the method
    result = jobs_tools.restjobs_jobs_submit_jcl(jcl_source=jcl_to_submit)

    # 4. Assertions
    # This will fail due to the schema issue, as expected
    assert isinstance(result, ZosmfJsonJob)
    assert result.jobid == "JOB00125"
    
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restjobs_jobs_submit_mvs_success():
    """
    Tests the successful submission of a job from a dataset.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()
    
    # Fake JSON response for the submitted job
    fake_submitted_job_json = {
        "jobid": "JOB00126",
        "jobname": "SUBMIT2",
        "owner": "USER1",
        "status": "INPUT",
        "type": "JOB",
        "url": "...", "files-url": "...", "job-correlator": "...",
    }
    mock_zosmf_client._call_zosmf_api.return_value = fake_submitted_job_json

    # 2. Instantiate the tool class
    jobs_tools = JobsTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = jobs_tools.restjobs_jobs_submit(file_name="USER.JCL(MEMBER)", file_type="MVS")

    # 4. Assertions
    assert isinstance(result, ZosmfJsonJob)
    assert result.jobid == "JOB00126"
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restjobs_jobs_submit_unix_success():
    """
    Tests the successful submission of a job from a unix file.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()
    
    # Fake JSON response for the submitted job
    fake_submitted_job_json = {
        "jobid": "JOB00127",
        "jobname": "SUBMIT3",
        "owner": "USER1",
        "status": "INPUT",
        "type": "JOB",
        "url": "...", "files-url": "...", "job-correlator": "...",
    }
    mock_zosmf_client._call_zosmf_api.return_value = fake_submitted_job_json

    # 2. Instantiate the tool class
    jobs_tools = JobsTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = jobs_tools.restjobs_jobs_submit(file_name="/u/user/jcl/myjob.jcl", file_type="unix")

    # 4. Assertions
    assert isinstance(result, ZosmfJsonJob)
    assert result.jobid == "JOB00127"
    mock_zosmf_client._call_zosmf_api.assert_called_once()
