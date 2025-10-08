from mcp_zosmf.client import ZosmfClient
from unittest.mock import patch, Mock
import pytest
import requests
from fastmcp.exceptions import ToolError

def test_zosmf_client_initialization():
    """
    Tests if the ZosmfClient is initialized with the correct attributes.
    """
    host = "testhost"
    user = "testuser"
    password = "testpassword"

    client = ZosmfClient(zosmf_host=host, username=user, password=password)

    assert client.zosmf_host == host
    assert client.username == user
    assert client.password == password
    assert client.jwt_token is None

@patch('requests.post')
def test_authenticate_success(mock_post):
    """
    Tests successful authentication.
    """
    # 1. Configure the mock
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.cookies = {'jwtToken': 'fake_jwt_token'}
    # The raise_for_status method does nothing on success
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    # 2. Create client and call the method
    client = ZosmfClient(zosmf_host="testhost", username="user", password="pw")
    result = client.authenticate()

    # 3. Assertions
    mock_post.assert_called_once_with(
        "https://testhost/zosmf/services/authenticate",
        auth=("user", "pw"),
        verify=False
    )
    assert client.jwt_token == 'fake_jwt_token'
    assert result == "Success"

@patch('requests.post')
def test_authenticate_failure(mock_post):
    """
    Tests failed authentication due to HTTP error.
    """
    # 1. Configure the mock to simulate an HTTP error
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    # Create an HTTPError instance to be raised by raise_for_status
    http_error = requests.exceptions.HTTPError("401 Client Error: Unauthorized for url")
    http_error.response = mock_response
    mock_response.raise_for_status.side_effect = http_error
    mock_post.return_value = mock_response

    # 2. Create client
    client = ZosmfClient(zosmf_host="testhost", username="user", password="wrongpassword")

    # 3. Call the method and assert that a ToolError is raised
    with pytest.raises(ToolError) as excinfo:
        client.authenticate()

    # 4. Assert that the error message is correct
    assert "HTTP error occurred: 401 - Unauthorized" in str(excinfo.value)

def test_call_zosmf_api_success():
    """
    Tests a successful API call through the _call_zosmf_api wrapper.
    """
    # 1. Create client and pre-authenticate it
    client = ZosmfClient(zosmf_host="testhost", username="user", password="pw")
    client.jwt_token = "fake_jwt_token"

    # 2. Create a mock for the api_call callable
    mock_api_call = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success"}
    mock_response.content = '{"status": "success"}' # Make sure content is not empty
    mock_api_call.return_value = mock_response

    # 3. Call the method
    result = client._call_zosmf_api(mock_api_call)

    # 4. Assertions
    mock_api_call.assert_called_once_with({"Authorization": "Bearer fake_jwt_token"})
    assert result == {"status": "success"}

@patch('mcp_zosmf.client.ZosmfClient.authenticate')
def test_call_zosmf_api_token_refresh(mock_authenticate):
    """
    Tests if the API call wrapper correctly refreshes the token on a 401 error.
    """
    # 1. Create client
    client = ZosmfClient(zosmf_host="testhost", username="user", password="pw")
    client.jwt_token = "old_fake_token"

    # 2. Configure mocks
    # Mock for the api_call callable
    mock_api_call = Mock()

    # First call raises HTTPError, second call returns success
    mock_response_unauthorized = Mock()
    mock_response_unauthorized.status_code = 401
    # We need to mock the response object for the HTTPError
    http_error = requests.exceptions.HTTPError("401 Client Error")
    http_error.response = mock_response_unauthorized
    
    mock_response_success = Mock()
    mock_response_success.json.return_value = {"status": "success_after_refresh"}
    mock_response_success.content = '{"status": "success_after_refresh"}'

    mock_api_call.side_effect = [
        http_error,
        mock_response_success
    ]

    # Mock for the authenticate method
    def update_token():
        client.jwt_token = "new_fake_token"
        return "Success"
    mock_authenticate.side_effect = update_token

    # 3. Call the method
    result = client._call_zosmf_api(mock_api_call)

    # 4. Assertions
    assert mock_authenticate.called
    assert mock_api_call.call_count == 2
    # Check the headers of the first call
    assert mock_api_call.call_args_list[0][0][0]["Authorization"] == "Bearer old_fake_token"
    # Check the headers of the second call
    assert mock_api_call.call_args_list[1][0][0]["Authorization"] == "Bearer new_fake_token"
    assert result == {"status": "success_after_refresh"}