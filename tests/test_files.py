from unittest.mock import Mock
import pytest
from requests.exceptions import HTTPError

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from mcp_zosmf.tools.files import FilesTools
from mcp_zosmf.schemas import ZosmfJsonDataSetList, ZosmfJsonDataSetMemberList, ZosmfJsonUnixFileList



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


def test_files_tools_registration():
    """
    Tests that the newly added UNIX file tools are successfully registered to the FastMCP app.
    """
    mock_app = FastMCP("TestApp")
    mock_zosmf_client = Mock()

    # Instantiate FilesTools to trigger registration
    FilesTools(mock_app, mock_zosmf_client)

    # Get the names of all registered tools
    registered_tool_names = list(mock_app._tool_manager._tools.keys())



    expected_new_tools = [
        "restfiles_fs_list",
        "restfiles_fs_get",
        "restfiles_fs_post",
        "restfiles_fs_put",
        "restfiles_fs_delete",
    ]

    for tool_name in expected_new_tools:
        assert tool_name in registered_tool_names


def test_restfiles_fs_list_success():
    """
    Tests the successful listing of UNIX files.
    """
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    fake_fs_list_json = {
        "items": [
            {
                "name": "file.txt",
                "mode": "-rw-r----",
                "size": 128,
                "uid": 1001,
                "user": "IBMUSER",
                "gid": 10,
                "group": "SYS1",
                "mtime": "2026-05-25T12:00:00"
            },
            {
                "name": "dir1",
                "mode": "drwxr-xr-x",
                "size": 4096,
                "uid": 1001,
                "user": "IBMUSER",
                "gid": 10,
                "group": "SYS1",
                "mtime": "2026-05-25T12:05:00"
            }
        ],
        "returnedRows": 2,
        "totalRows": 2
    }
    mock_zosmf_client._call_zosmf_api.return_value = fake_fs_list_json

    files_tools = FilesTools(mock_app, mock_zosmf_client)
    result = files_tools.restfiles_fs_list(path="/u/user")

    assert isinstance(result, ZosmfJsonUnixFileList)
    assert len(result.items) == 2
    assert result.items[0].name == "file.txt"
    assert result.items[0].size == 128
    assert result.items[1].mode == "drwxr-xr-x"
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_fs_list_validation_error():
    """
    Tests that a ToolError is raised when the UNIX file listing response has an invalid format.
    """
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Missing the required 'items' field
    invalid_json = {"returnedRows": 2}
    mock_zosmf_client._call_zosmf_api.return_value = invalid_json

    files_tools = FilesTools(mock_app, mock_zosmf_client)
    with pytest.raises(ToolError, match="JSON Validation error"):
        files_tools.restfiles_fs_list(path="/u/user")

    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_fs_get_success():
    """
    Tests the successful retrieval of UNIX file content.
    """
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    fake_content = "Hello from z/OS UNIX File System!"
    mock_zosmf_client._call_zosmf_api.return_value = fake_content

    files_tools = FilesTools(mock_app, mock_zosmf_client)
    result = files_tools.restfiles_fs_get(filepath="/u/user/file.txt")

    assert result == fake_content
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_fs_post_success():
    """
    Tests the successful creation of a UNIX file or directory.
    """
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()
    mock_zosmf_client._call_zosmf_api.return_value = None

    files_tools = FilesTools(mock_app, mock_zosmf_client)
    result = files_tools.restfiles_fs_post(
        filepath="/u/user/newdir",
        type="directory",
        mode="rwxr-xr-x"
    )

    assert "Successfully created directory at /u/user/newdir" in result
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_fs_put_success():
    """
    Tests successfully writing data to a UNIX file.
    """
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()
    mock_zosmf_client._call_zosmf_api.return_value = ""

    files_tools = FilesTools(mock_app, mock_zosmf_client)
    result = files_tools.restfiles_fs_put(
        filepath="/u/user/file.txt",
        body="New Content",
        binary=False
    )

    assert "Successfully wrote to /u/user/file.txt" in result
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restfiles_fs_delete_success():
    """
    Tests successfully deleting a UNIX file or directory.
    """
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()
    mock_zosmf_client._call_zosmf_api.return_value = None

    files_tools = FilesTools(mock_app, mock_zosmf_client)
    result = files_tools.restfiles_fs_delete(
        filepath="/u/user/file.txt",
        recursive=False
    )

    assert "Successfully deleted /u/user/file.txt" in result
    mock_zosmf_client._call_zosmf_api.assert_called_once()

