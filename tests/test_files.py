from unittest.mock import Mock
import pytest
from requests.exceptions import HTTPError

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from mcp_zosmf.tools.files import FilesTools
from mcp_zosmf.schemas import ZosmfJsonDataSetList, ZosmfJsonDataSetMemberList


def test_restfiles_ds_list_success():
    """
    Tests the successful listing of data sets.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake JSON response from the API
    fake_ds_list_json = {
        "items": [
            {"dsname": "USER.TEST.DATASET1", "vol": "VOL001"},
            {"dsname": "USER.TEST.DATASET2", "vol": "VOL002"},
        ],
        "returnedRows": 2,
    }
    mock_zosmf_client._call_zosmf_api.return_value = fake_ds_list_json

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = files_tools.restfiles_ds_list(dslevel="USER.TEST.*")

    # 4. Assertions
    assert isinstance(result, ZosmfJsonDataSetList)
    assert len(result.items) == 2
    assert result.items[0].dsname == "USER.TEST.DATASET1"
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_ds_memberlist_success():
    """
    Tests the successful listing of PDS members.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake JSON response from the API
    fake_member_list_json = {
        "items": [{"member": "MEMBER1"}, {"member": "MEMBER2"}],
        "returnedRows": 2,
    }
    mock_zosmf_client._call_zosmf_api.return_value = fake_member_list_json

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = files_tools.restfiles_ds_memberlist(dataset_name="USER.TEST.PDS")

    # 4. Assertions
    assert isinstance(result, ZosmfJsonDataSetMemberList)
    assert len(result.items) == 2
    assert result.items[0].member == "MEMBER1"
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_ds_get_success():
    """
    Tests the successful retrieval of data set content.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake response from the API (plain text content)
    fake_ds_content = "This is the content of the data set."
    mock_zosmf_client._call_zosmf_api.return_value = fake_ds_content

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = files_tools.restfiles_ds_get(dataset_name="USER.TEST.DATASET1")

    # 4. Assertions
    assert result == fake_ds_content
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_ds_get_not_found_error():
    """
    Tests that a ToolError is raised when the data set is not found (404).
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Configure the API wrapper to raise a ToolError, simulating a 404
    mock_zosmf_client._call_zosmf_api.side_effect = ToolError(
        "API call failed: 404 Not Found"
    )

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method and assert that it raises the correct exception
    with pytest.raises(ToolError, match="API call failed: 404 Not Found"):
        files_tools.restfiles_ds_get(dataset_name="USER.NON.EXISTENT")

    # 4. Assert that the mock was called
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_ds_list_validation_error():
    """
    Tests that a ToolError is raised on Pydantic validation error.
    This simulates the API returning an invalid JSON structure.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake JSON response with a missing required field ("items")
    invalid_json = {"returnedRows": 0}
    mock_zosmf_client._call_zosmf_api.return_value = invalid_json

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method and assert that it raises a ToolError
    with pytest.raises(ToolError, match="JSON Validation error"):
        files_tools.restfiles_ds_list(dslevel="USER.TEST.*")

    # 4. Assert that the mock was called
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_ds_get_server_error():
    """
    Tests that a ToolError is raised on a server-side error (500).
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Configure the API wrapper to raise a ToolError, simulating a 500
    mock_zosmf_client._call_zosmf_api.side_effect = ToolError(
        "API call failed: 500 Internal Server Error"
    )

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method and assert that it raises the correct exception
    with pytest.raises(ToolError, match="API call failed: 500 Internal Server Error"):
        files_tools.restfiles_ds_get(dataset_name="USER.TEST.DATASET1")

    # 4. Assert that the mock was called
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restfiles_ds_list_empty_response():
    """
    Tests handling of an empty list response from the API.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake JSON response for an empty list
    fake_empty_list_json = {"items": [], "returnedRows": 0}
    mock_zosmf_client._call_zosmf_api.return_value = fake_empty_list_json

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = files_tools.restfiles_ds_list(dslevel="USER.NO.MATCH")

    # 4. Assertions
    assert isinstance(result, ZosmfJsonDataSetList)
    assert len(result.items) == 0
    assert result.returnedRows == 0
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restfiles_ds_put_success_text():
    """
    Tests the successful write of content in text mode.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake response from the API (usually empty for PUT or a simple success message)
    fake_response = ""
    mock_zosmf_client._call_zosmf_api.return_value = fake_response

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = files_tools.restfiles_ds_put(
        dataset_name="USER.TEST.DATASET1",
        body="New content",
        binary=False
    )

    # 4. Assertions
    assert result == fake_response
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_ds_put_success_binary():
    """
    Tests the successful write of content in binary mode to a PDS member.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake response from the API
    fake_response = ""
    mock_zosmf_client._call_zosmf_api.return_value = fake_response

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = files_tools.restfiles_ds_put(
        dataset_name="USER.TEST.PDS",
        member_name="MEMBER1",
        body="Binary data",
        binary=True
    )

    # 4. Assertions
    assert result == fake_response
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restfiles_ds_put_with_volser():
    """
    Tests the write of content with a volser.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake response from the API
    fake_response = ""
    mock_zosmf_client._call_zosmf_api.return_value = fake_response

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = files_tools.restfiles_ds_put(
        dataset_name="USER.TEST.DATASET1",
        body="Content",
        volser="VOL001"
    )

    # 4. Assertions
    assert result == fake_response
    mock_zosmf_client._call_zosmf_api.assert_called_once()

def test_restfiles_ds_put_error():
    """
    Tests handling of API error during write.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Configure the API wrapper to raise a ToolError
    mock_zosmf_client._call_zosmf_api.side_effect = ToolError(
        "API call failed: 403 Forbidden"
    )

    # 2. Instantiate the tool class
    files_tools = FilesTools(mock_app, mock_zosmf_client)

    # 3. Call the method and assert that it raises the correct exception
    with pytest.raises(ToolError, match="API call failed: 403 Forbidden"):
        files_tools.restfiles_ds_put(
            dataset_name="USER.TEST.DATASET1",
            body="Content"
        )

    # 4. Assert that the mock was called
    mock_zosmf_client._call_zosmf_api.assert_called_once()
