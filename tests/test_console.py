from unittest.mock import Mock
import pytest

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from mcp_zosmf.tools.console import ConsoleTools
from mcp_zosmf.schemas import ZosmfJsonConsoleIssueSyncCommand


def test_restconsoles_issue_command_success():
    """
    Tests the successful issuing of a console command.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake JSON response from the API
    fake_response_json = {"cmd-response": "D A,L\nIEE114I 14.48.51 2024 ACTIVITY ..."}
    mock_zosmf_client._call_zosmf_api.return_value = fake_response_json

    # 2. Instantiate the tool class
    console_tools = ConsoleTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = console_tools.restconsoles_issue_command(command="D A,L")

    # 4. Assertions
    assert isinstance(result, ZosmfJsonConsoleIssueSyncCommand)
    assert "D A,L" in result.cmd_response
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restconsoles_issue_command_empty_response():
    """
    Tests handling of an empty command response from the API.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake JSON response for an empty response
    fake_empty_response_json = {"cmd-response": ""}
    mock_zosmf_client._call_zosmf_api.return_value = fake_empty_response_json

    # 2. Instantiate the tool class
    console_tools = ConsoleTools(mock_app, mock_zosmf_client)

    # 3. Call the method
    result = console_tools.restconsoles_issue_command(command="SOME COMMAND")

    # 4. Assertions
    assert isinstance(result, ZosmfJsonConsoleIssueSyncCommand)
    assert result.cmd_response == ""
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restconsoles_issue_command_http_error():
    """
    Tests that a ToolError is raised on an HTTP error (e.g., 500).
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Configure the API wrapper to raise a ToolError
    mock_zosmf_client._call_zosmf_api.side_effect = ToolError(
        "API call failed: 503 Service Unavailable"
    )

    # 2. Instantiate the tool class
    console_tools = ConsoleTools(mock_app, mock_zosmf_client)

    # 3. Call the method and assert that it raises the correct exception
    with pytest.raises(ToolError, match="API call failed: 503 Service Unavailable"):
        console_tools.restconsoles_issue_command(command="D A,L")

    # 4. Assert that the mock was called
    mock_zosmf_client._call_zosmf_api.assert_called_once()


def test_restconsoles_issue_command_validation_error():
    """
    Tests that a ToolError is raised on Pydantic validation error.
    """
    # 1. Setup Mocks
    mock_app = Mock(spec=FastMCP)
    mock_zosmf_client = Mock()

    # Fake JSON response with the wrong data type for a field
    invalid_json = {"cmd-response": 12345}  # Should be a string
    mock_zosmf_client._call_zosmf_api.return_value = invalid_json

    # 2. Instantiate the tool class
    console_tools = ConsoleTools(mock_app, mock_zosmf_client)

    # 3. Call the method and assert that it raises a ToolError
    with pytest.raises(ToolError, match="JSON Validation error"):
        console_tools.restconsoles_issue_command(command="D A,L")

    # 4. Assert that the mock was called
    mock_zosmf_client._call_zosmf_api.assert_called_once()
