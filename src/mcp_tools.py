import logging
from typing import Dict, Any

logger = logging.getLogger("pcloudy-mcp-server")

# Tool to list available devices
async def list_available_devices(api) -> dict:
    """List the names of available Android devices."""
    logger.info("Tool called: list_available_devices")
    try:
        devices_response = api.get_devices_list()
        devices = devices_response.get("models", [])
        available_devices = [d["model"] for d in devices if d["available"]]
        if not available_devices:
            logger.info("No devices are currently available")
            return {
                "content": [{"type": "text", "text": "No devices are currently available."}],
                "isError": True
            }
        device_list = ", ".join(available_devices)
        logger.info(f"Found {len(available_devices)} available devices")
        return {
            "content": [{"type": "text", "text": f"Available devices: {device_list}"}],
            "isError": False
        }
    except Exception as e:
        logger.error(f"Error listing devices: {str(e)}")
        return {
            "content": [{"type": "text", "text": f"Error listing devices: {str(e)}"}],
            "isError": True
        }

# Tool to book a device by name
async def book_device_by_name(api, device_name: str) -> dict:
    """Book an Android device by matching the provided device name from the available list."""
    logger.info(f"Tool called: book_device_by_name with device_name={device_name}")
    try:
        devices_response = api.get_devices_list()
        devices = devices_response.get("models", [])
        if not devices:
            logger.info("No devices available")
            return {
                "content": [{"type": "text", "text": "No devices available"}],
                "isError": True
            }
        device_name = device_name.lower().strip()
        selected_device = next(
            (d for d in devices if d["available"] and device_name in d["model"].lower()),
            None
        )
        if not selected_device:
            logger.info(f"No available device found matching '{device_name}'")
            return {
                "content": [{"type": "text", "text": f"No available device found matching '{device_name}'. Please choose from the available devices."}],
                "isError": True
            }
        booking = api.book_device(selected_device["id"])
        api.rid = booking.get("rid")
        if not api.rid:
            logger.error("Failed to get booking ID")
            return {
                "content": [{"type": "text", "text": "Failed to get booking ID"}],
                "isError": True
            }
        logger.info(f"Device '{selected_device['model']}' booked successfully. RID: {api.rid}")
        return {
            "content": [{"type": "text", "text": f"Device '{selected_device['model']}' booked successfully. RID: {api.rid}"}],
            "isError": False
        }
    except Exception as e:
        logger.error(f"Error booking device: {str(e)}")
        return {
            "content": [{"type": "text", "text": f"Error booking device: {str(e)}"}],
            "isError": True
        }

# Tool to upload a file
async def upload_file(api, file_path: str, source_type: str = "raw", filter_type: str = "all") -> dict:
    """Upload a file to the pCloudy cloud drive, but only if it does not already exist."""
    logger.info(f"Tool called: upload_file with file_path={file_path}, source_type={source_type}, filter_type={filter_type}")
    try:
        result = api.upload_file(file_path, source_type, filter_type)
        # result is already a dict with 'content' and 'isError'
        return result
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return {
            "content": [{"type": "text", "text": f"Error uploading file: {str(e)}"}],
            "isError": True
        }

# Tool to execute ADB command
async def execute_adb_command(api, rid: str, adb_command: str) -> dict:
    """Execute an ADB command on a booked device."""
    logger.info(f"Tool called: execute_adb_command with rid={rid}, adb_command={adb_command}")
    try:
        result = api.execute_adb(rid, adb_command)
        output = result.get("output", "No output returned")
        logger.info(f"ADB command executed successfully: {output}")
        return {
            "content": [{"type": "text", "text": f"ADB command executed successfully: {output}"}],
            "isError": False
        }
    except Exception as e:
        logger.error(f"Error executing ADB command: {str(e)}")
        return {
            "content": [{"type": "text", "text": f"Error executing ADB command: {str(e)}"}],
            "isError": True
        }

# Tool to capture device screenshot
async def capture_device_screenshot(api, rid: str, skin: bool = True) -> dict:
    """Capture a screenshot of a booked device."""
    logger.info(f"Tool called: capture_device_screenshot with rid={rid}, skin={skin}")
    try:
        result = api.capture_screenshot(rid, skin)
        file_url = result.get("file")
        if not file_url:
            logger.error("Failed to get screenshot file URL")
            return {
                "content": [{"type": "text", "text": "Failed to get screenshot file URL"}],
                "isError": True
            }
        logger.info(f"Screenshot captured successfully: {file_url}")
        return {
            "content": [{"type": "text", "text": f"Screenshot captured successfully: {file_url}"}],
            "isError": False
        }
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        return {
            "content": [{"type": "text", "text": f"Error capturing screenshot: {str(e)}"}],
            "isError": True
        }

# Tool to install and launch an app
async def install_and_launch_app(api, rid: str, filename: str, grant_all_permissions: bool = True) -> dict:
    """Install and launch an app on a booked device."""
    logger.info(f"Tool called: install_and_launch_app with rid={rid}, filename={filename}, grant_all_permissions={grant_all_permissions}")
    try:
        result = api.install_and_launch_app(rid, filename, grant_all_permissions)
        logger.info(f"App '{filename}' installed and launched successfully on RID: {rid}")
        return {
            "content": [{"type": "text", "text": f"App '{filename}' installed and launched successfully on RID: {rid}"}],
            "isError": False
        }
    except Exception as e:
        logger.error(f"Error installing and launching app: {str(e)}")
        return {
            "content": [{"type": "text", "text": f"Error installing and launching app: {str(e)}"}],
            "isError": True
        }

# Tool to release a device
async def release_device(api, rid: str) -> dict:
    """Release a booked device."""
    logger.info(f"Tool called: release_device with rid={rid}")
    try:
        result = api.release_device(rid)
        logger.info(f"Device with RID {rid} released successfully")
        return {
            "content": [{"type": "text", "text": f"Device with RID {rid} released successfully"}],
            "isError": False
        }
    except Exception as e:
        logger.error(f"Error releasing device: {str(e)}")
        return {
            "content": [{"type": "text", "text": f"Error releasing device: {str(e)}"}],
            "isError": True
        }

# Tool to get device page URL
async def get_device_page_url(api, rid: str) -> dict:
    """Get the pCloudy device page URL to view the device screen."""
    logger.info(f"Tool called: get_device_page_url with rid={rid}")
    try:
        result = api.get_device_page_url(rid)
        return result
    except Exception as e:
        logger.error(f"Error generating device page URL: {str(e)}")
        return {
            "content": [{"type": "text", "text": f"Error generating device page URL: {str(e)}"}],
            "isError": True
        } 