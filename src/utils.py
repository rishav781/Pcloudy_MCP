import base64
import json
import logging

logger = logging.getLogger("pcloudy-mcp-server")

def encode_auth(username, api_key):
    return base64.b64encode(f"{username}:{api_key}".encode()).decode()

def parse_response(response):
    try:
        data = response.json()
        if "result" not in data:
            logger.error(f"Invalid response format: {json.dumps(data)}")
            raise ValueError(f"Invalid response format: {json.dumps(data)}")
        return data["result"]
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON response: {response.text}")
        raise ValueError(f"Invalid JSON response: {response.text}")
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        raise 