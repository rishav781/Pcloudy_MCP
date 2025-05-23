import httpx
import base64
import json
import logging
import time
import os
from typing import Dict, Any
from .config import Config
from .utils import encode_auth, parse_response

logger = logging.getLogger("pcloudy-mcp-server")

class PCloudyAPI:
    def __init__(self, username=None, api_key=None, base_url=None):
        self.username = username or Config.USERNAME
        self.api_key = api_key or Config.API_KEY
        self.base_url = base_url or Config.PCLOUDY_BASE_URL
        self.auth_token = None
        self.token_timestamp = None
        self.client = httpx.Client(timeout=Config.REQUEST_TIMEOUT)
        self.rid = None
        logger.info("PCloudyAPI initialized")

    def authenticate(self):
        try:
            logger.info("Authenticating with pCloudy")
            url = f"{self.base_url}/access"
            auth = encode_auth(self.username, self.api_key)
            headers = {"Authorization": f"Basic {auth}"}
            response = self.client.get(url, headers=headers)
            response.raise_for_status()
            result = parse_response(response)
            self.auth_token = result.get("token")
            if not self.auth_token:
                logger.error("Authentication failed: No token received")
                raise ValueError("Authentication failed: No token received")
            self.token_timestamp = time.time()
            logger.info("Authentication successful")
            return self.auth_token
        except httpx.RequestError as e:
            logger.error(f"Authentication request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise

    def check_token_validity(self):
        if not self.auth_token:
            logger.info("No authentication token present, authenticating...")
            return self.authenticate()
        if self.token_timestamp and (time.time() - self.token_timestamp) > Config.TOKEN_REFRESH_THRESHOLD:
            logger.info("Token expired, refreshing...")
            return self.authenticate()
        return self.auth_token

    def get_devices_list(self, platform=Config.DEFAULT_PLATFORM, duration=Config.DEFAULT_DURATION, available_now=True):
        try:
            self.check_token_validity()
            logger.info(f"Getting device list for platform {platform}")
            url = f"{self.base_url}/devices"
            payload = {
                "token": self.auth_token,
                "platform": platform,
                "duration": duration,
                "available_now": str(available_now).lower()
            }
            headers = {"Content-Type": "application/json"}
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = parse_response(response)
            logger.info(f"Retrieved {len(result.get('models', []))} devices")
            return result
        except httpx.RequestError as e:
            logger.error(f"Device list request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting device list: {str(e)}")
            raise

    def book_device(self, device_id, duration=Config.DEFAULT_DURATION):
        try:
            self.check_token_validity()
            logger.info(f"Booking device with ID {device_id}")
            url = f"{self.base_url}/book_device"
            payload = {
                "token": self.auth_token,
                "id": device_id,
                "duration": duration
            }
            headers = {"Content-Type": "application/json"}
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = parse_response(response)
            logger.info(f"Device booked successfully. RID: {result.get('rid')}")
            return result
        except httpx.RequestError as e:
            logger.error(f"Device booking request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error booking device: {str(e)}")
            raise

    def list_cloud_files(self):
        """List files in the user's pCloudy cloud drive."""
        try:
            self.check_token_validity()
            url = f"{self.base_url}/content"
            params = {"token": self.auth_token}
            response = self.client.get(url, params=params)
            response.raise_for_status()
            result = parse_response(response)
            # result is expected to be a list of dicts with 'name' key
            return [f["name"] for f in result.get("files", [])] if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"Error listing cloud files: {str(e)}")
            return []

    def upload_file(self, file_path, source_type="raw", filter_type="all"):
        try:
            file_path = file_path.strip('"').strip("'")  # Remove quotes if present
            self.check_token_validity()
            logger.info(f"Uploading file: {file_path}")
            if not os.path.isfile(file_path):
                logger.error(f"Provided path is not a file: {file_path}")
                return {
                    "content": [{"type": "text", "text": f"Provided path is not a file: {file_path}"}],
                    "isError": True
                }
            file_name = os.path.basename(file_path)
            # Check if file already exists in cloud drive
            cloud_files = self.list_cloud_files()
            if file_name in cloud_files:
                logger.info(f"File '{file_name}' already exists in cloud drive")
                return {
                    "content": [{"type": "text", "text": f"File '{file_name}' already exists in your pCloudy cloud drive."}],
                    "isError": False
                }
            url = f"{self.base_url}/upload_file"
            files = {"file": open(file_path, "rb")}
            data = {
                "source_type": source_type,
                "token": self.auth_token,
                "filter": filter_type
            }
            headers = {"Authorization": f"Basic {encode_auth(self.username, self.api_key)}"}
            response = self.client.post(url, files=files, data=data, headers=headers)
            response.raise_for_status()
            result = parse_response(response)
            file_name = result.get("file")
            if not file_name:
                logger.error("Failed to get uploaded file name")
                logger.error(f"API response missing file: {result}")
                return {
                    "content": [{"type": "text", "text": "Failed to get uploaded file name"}],
                    "isError": True
                }
            logger.info(f"File '{file_name}' uploaded successfully")
            return {
                "content": [{"type": "text", "text": f"File '{file_name}' uploaded successfully"}],
                "isError": False
            }
        except httpx.RequestError as e:
            logger.error(f"File upload request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise

    def execute_adb(self, rid, adb_command):
        try:
            self.check_token_validity()
            logger.info(f"Executing ADB command: {adb_command} on RID: {rid}")
            url = f"{self.base_url}/execute_adb"
            payload = {
                "token": self.auth_token,
                "rid": rid,
                "adbCommand": adb_command
            }
            headers = {"Content-Type": "application/json"}
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = parse_response(response)
            logger.info(f"ADB command executed successfully: {result}")
            return result
        except httpx.RequestError as e:
            logger.error(f"ADB command request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing ADB command: {str(e)}")
            raise

    def capture_screenshot(self, rid, skin=True):
        try:
            self.check_token_validity()
            logger.info(f"Capturing screenshot for RID: {rid}")
            url = f"{self.base_url}/capture_device_screenshot"
            payload = {
                "token": self.auth_token,
                "rid": rid,
                "skin": str(skin).lower()
            }
            headers = {"Content-Type": "application/json"}
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.debug(f"Raw screenshot API response: {response.text}")
            result = parse_response(response)
            logger.info(f"Screenshot API response: {result}")

            # pCloudy returns 'filename' and 'dir', not 'file'
            filename = result.get("filename")
            dir_ = result.get("dir")
            if not filename or not dir_:
                logger.error("Failed to get screenshot file URL")
                logger.error(f"Full screenshot API response: {result}")
                return {
                    "content": [{"type": "text", "text": f"Failed to get screenshot file URL. API response: {result}"}],
                    "isError": True
                }
            file_url = f"https://device.pcloudy.com/recent/{dir_}/{filename}"
            logger.info(f"Screenshot captured successfully: {file_url}")
            result["file"] = file_url  # Add file URL to result for downstream use
            return result
        except httpx.RequestError as e:
            logger.error(f"Screenshot request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}")
            raise

    def install_and_launch_app(self, rid, filename, grant_all_permissions=True):
        try:
            self.check_token_validity()
            logger.info(f"Installing and launching app: {filename} on RID: {rid}")
            url = f"{self.base_url}/install_app"
            payload = {
                "token": self.auth_token,
                "rid": rid,
                "filename": filename,
                "grant_all_permissions": str(grant_all_permissions).lower()
            }
            headers = {"Content-Type": "application/json"}
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = parse_response(response)
            logger.info(f"App '{filename}' installed and launched successfully: {result}")
            return result
        except httpx.RequestError as e:
            logger.error(f"App install request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error installing and launching app: {str(e)}")
            raise

    def release_device(self, rid):
        try:
            self.check_token_validity()
            logger.info(f"Releasing device with RID: {rid}")
            url = f"{self.base_url}/release_device"
            payload = {
                "token": self.auth_token,
                "rid": rid
            }
            headers = {"Content-Type": "application/json"}
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = parse_response(response)
            logger.info(f"Device with RID {rid} released successfully")
            return {
                "content": [{"type": "text", "text": f"Device with RID {rid} released successfully"}],
                "isError": False
            }
        except httpx.RequestError as e:
            logger.error(f"Device release request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error releasing device: {str(e)}")
            return {
                "content": [{"type": "text", "text": f"Error releasing device: {str(e)}"}],
                "isError": True
            }

    def get_device_page_url(self, rid):
        """Return the pCloudy device page URL for a given RID using the API."""
        try:
            self.check_token_validity()
            logger.info(f"Getting device page URL for RID: {rid}")
            url = f"{self.base_url}/get_device_url"
            payload = {
                "token": self.auth_token,
                "rid": rid
            }
            headers = {"Content-Type": "application/json"}
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Expecting {"result":{"token":"...","code":200,"URL":"https://device.pcloudy.com/device/..."}} 
            result = data.get("result", {})
            device_url = result.get("URL")
            if not device_url:
                logger.error(f"Device page URL not found in API response: {data}")
                return {
                    "content": [{"type": "text", "text": f"Device page URL not found. API response: {data}"}],
                    "isError": True
                }
            logger.info(f"Device page URL for RID {rid}: {device_url}")
            return {
                "content": [{"type": "text", "text": f"Device page URL: {device_url}"}],
                "isError": False
            }
        except Exception as e:
            logger.error(f"Error getting device page URL: {str(e)}")
            return {
                "content": [{"type": "text", "text": f"Error getting device page URL: {str(e)}"}],
                "isError": True
            }

    def __del__(self):
        try:
            self.client.close()
        except:
            pass 