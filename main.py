# Imports
import httpx
import logging
import os
from fastmcp import FastMCP
from src.pcloudy_api import PCloudyAPI
from src.mcp_tools import (
    list_available_devices,
    book_device_by_name,
    upload_file,
    execute_adb_command,
    capture_device_screenshot,
    install_and_launch_app,
    release_device,
    get_device_page_url
)

# Configure logging with more detailed format and file output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pcloudy_server.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("pcloudy-mcp-server")

# Initialize MCP server
mcp = FastMCP("pcloudy_MCP", description="MCP server for pCloudy Android device management")

# Initialize PCloudyAPI instance
api = PCloudyAPI()

# Register tools
@mcp.tool()
async def list_available_devices_tool() -> dict:
    """List the names of available Android devices."""
    return await list_available_devices(api)

@mcp.tool()
async def book_device_by_name_tool(device_name: str) -> dict:
    """Book an Android device by matching the provided device name from the available list."""
    return await book_device_by_name(api, device_name)

@mcp.tool()
async def upload_file_tool(file_path: str, source_type: str = "raw", filter_type: str = "all") -> dict:
    """Upload a file to the pCloudy cloud drive, but only if it does not already exist."""
    return await upload_file(api, file_path, source_type, filter_type)

@mcp.tool()
async def execute_adb_command_tool(rid: str, adb_command: str) -> dict:
    """Execute an ADB command on a booked device."""
    return await execute_adb_command(api, rid, adb_command)

@mcp.tool()
async def capture_device_screenshot_tool(rid: str, skin: bool = True) -> dict:
    """Capture a screenshot of a booked device."""
    return await capture_device_screenshot(api, rid, skin)

@mcp.tool()
async def install_and_launch_app_tool(rid: str, filename: str, grant_all_permissions: bool = True) -> dict:
    """Install and launch an app on a booked device."""
    return await install_and_launch_app(api, rid, filename, grant_all_permissions)

@mcp.tool()
async def release_device_tool(rid: str) -> dict:
    """Release a booked device."""
    return await release_device(api, rid)

@mcp.tool()
async def get_device_page_url_tool(rid: str) -> dict:
    """Get the pCloudy device page URL to view the device screen."""
    return await get_device_page_url(api, rid)

# Add this block at the end of the file
if __name__ == "__main__":
    print("\n--- Starting FastMCP Server via __main__ ---")
    # Remove 'host' argument for Render compatibility
    mcp.run(
        transport="streamable-http",
        port=int(os.environ.get("PORT", 8000))  # Use Render's PORT env var or default to 8000
    )