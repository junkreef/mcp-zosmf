import argparse
from fastmcp import FastMCP

from client import ZosmfClient
from tools.jobs import JobsTools
from tools.files import FilesTools
from tools.console import ConsoleTools

# Create an MCP server based on the QuickStart guide
app = FastMCP("MCP z/OSMF Server")
app.settings.stateless_http = True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MCP z/OSMF Server.")
    parser.add_argument("--username", required=True, help="z/OSMF username")
    parser.add_argument("--password", required=True, help="z/OSMF password")
    parser.add_argument("--zosmf_host", required=False, default="192.168.250.200:10443", help="z/OSMF host and port")
    parser.add_argument(
        "--transport",
        default="stdio",
        required=False,
        help="MCP transport type",
        choices=["stdio", "streamable-http", "sse"],
    )
    args = parser.parse_args()

    # Initialize the z/OSMF client
    zosmf_client = ZosmfClient(
        zosmf_host=args.zosmf_host,
        username=args.username,
        password=args.password
    )

    # Initialize tool groups, which will register the tools with the app
    JobsTools(app, zosmf_client)
    FilesTools(app, zosmf_client)
    ConsoleTools(app, zosmf_client)

    # Run the application
    app.run(transport=args.transport)