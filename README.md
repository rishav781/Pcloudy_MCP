# pCloudy MCP Server

This project implements an MCP (Model Context Protocol) server for managing Android devices on the pCloudy platform. It provides tools to interact with pCloudy devices, such as listing available devices, booking devices, uploading files, executing ADB commands, capturing screenshots, installing and launching apps, and releasing devices.

## Project Structure

The project is organized into the `src` directory:

-   `src/config.py`: Contains configuration settings for the pCloudy API.
-   `src/utils.py`: Contains utility functions for authentication and response parsing.
-   `src/pcloudy_api.py`: Contains the `PCloudyAPI` class for interacting with the pCloudy API.
-   `src/mcp_tools.py`: Contains the definitions for the MCP tools.
-   `main.py`: The main entry point for the MCP server, handling logging, initialization, and tool registration.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
    (Replace `<repository_url>` and `<repository_directory>` with your actual repository details)

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    -   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    -   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**
    You will need `httpx` and `mcp`. You can install them using pip:
    ```bash
    pip install httpx mcp
    ```

5.  **Configure pCloudy API:**
    Update the `USERNAME` and `API_KEY` in `src/config.py` with your pCloudy credentials.

## Running the Server

To run the MCP server using `mcp dev`, navigate to the project root directory in your terminal and run:

```bash
mcp dev main.py
```

This will start the MCP server, and you can connect to it using a compatible client.

### Installation for Claude Desktop

To install this server for use with Claude Desktop, navigate to the project root directory in your terminal and run:

```bash
mcp install main.py
```

## Available Tools

The following tools are available:

-   `list_available_devices`: List the names of available Android devices.
-   `book_device_by_name`: Book an Android device by matching the provided device name from the available list.
-   `upload_file`: Upload a file to the pCloudy cloud drive, but only if it does not already exist.
-   `execute_adb_command`: Execute an ADB command on a booked device.
-   `capture_device_screenshot`: Capture a screenshot of a booked device.
-   `install_and_launch_app`: Install and launch an app on a booked device.
-   `release_device`: Release a booked device.
-   `get_device_page_url`: Get the pCloudy device page URL to view the device screen.
