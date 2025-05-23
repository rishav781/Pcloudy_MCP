import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PCLOUDY_BASE_URL = "https://device.pcloudy.com/api"
    DEFAULT_PLATFORM = "android"
    DEFAULT_DURATION = 10
    REQUEST_TIMEOUT = 300  # seconds
    TOKEN_REFRESH_THRESHOLD = 3600 # seconds (1 hour)

    # Retrieve environment variables
    USERNAME = os.environ.get("PCLOUDY_USERNAME")
    API_KEY = os.environ.get("PCLOUDY_API_KEY")

    print(f"DEBUG: Inside Config class definition - PCLOUDY_USERNAME: {USERNAME}")
    print(f"DEBUG: Inside Config class definition - PCLOUDY_API_KEY: {API_KEY}")