from fastmcp import FastMCP, settings as fastmcp_settings

from .client import ZosmfClient
from .settings import settings
from .tools.jobs import JobsTools
from .tools.files import FilesTools
from .tools.console import ConsoleTools

# Create an MCP server based on the QuickStart guide
app = FastMCP("MCP z/OSMF Server")
fastmcp_settings.stateless_http = True

if __name__ == "__main__":

    # Initialize the z/OSMF client
    zosmf_client = ZosmfClient(
        zosmf_host=settings.zosmf_host,
        username=settings.zosmf_username,
        password=settings.zosmf_password
    )

    # Initialize tool groups, which will register the tools with the app
    JobsTools(app, zosmf_client)
    FilesTools(app, zosmf_client)
    ConsoleTools(app, zosmf_client)

    # Run the application
    if settings.transport == "stdio":
        app.run(transport=settings.transport)
    else:
        app.run(transport=settings.transport, port=settings.port)