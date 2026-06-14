# Prompt

what us the best way to learn agentic mcp loop ai programming and so forth without spending money?

# Google Browser Answer

Build a Local Weather Investigator Agent using Python. This beginner-friendly project avoids complex code while teaching you the exact pattern of an agentic loop: AI reasons → AI calls an MCP tool → Tool returns data → AI interprets the result.You will use FastMCP (the official, highly simplified Python SDK for MCP) alongside smolagents (Hugging Face's ultra-lightweight, free-to-use agent framework).

# Step 1: Set Up Your Free Environment

Open your terminal and run these commands to set up a virtual environment and install the required official libraries.

```bash
# Install uv (the fastest, free Python package manager)

curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize your project directory
`uv init mcp_agent && cd mcp_agent`

# Install FastMCP and the agent loop toolkit
uv add "mcp[cli]" smolagents httpx
```

# Step 2: Write Your Custom MCP Server

Create a file named `server.py`. This script explicitly exposes a Python function as a standardized AI tool using the `FastMCP` decorator.

```python
# server.py
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server instance
mcp = FastMCP("Weather Investigator")

@mcp.tool()
def get_temperature(latitude: float, longitude: float) -> str:
    """
    Fetches the current temperature for a given latitude and longitude.
    Always use this tool when asked about weather or temperatures.
    """
    url = f"https://open-meteo.com{latitude}&longitude={longitude}&current=temperature_2m"
    
    # Make a completely free, no-API-key HTTP request
    response = httpx.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data["current"]["temperature_2m"]
        unit = data["current_units"]["temperature_2m"]
        return f"The current temperature is {temp}{unit}."
    return "Error: Could not retrieve temperature data."

if __name__ == "__main__":
    # Start the server using standard Input/Output (stdio) transport
    mcp.run(transport="stdio")
```

# Step 3: Connect Your Custom Script Agent Loop

Create a separate script named `agent.py`. This script starts an orchestration engine using [Hugging Face's smolagents](https://github.com/huggingface/smolagents). It boots up your custom `server.py` in the background, automatically reads the tool definitions, and hands them to the AI model.

```python
# agent.py
import os
from smolagents import CodeAgent, LiteLLMModel
from mcp.client.stdio import StdioServerParameters
from mcp.client.sync import mcp_sync_client

# 1. Configure how the client talks to your custom server script
server_params = StdioServerParameters(
    command="python",
    args=["server.py"]
)

# 2. Initialize your chosen LLM (LiteLLM dynamically loads your free API keys)
# Ensure your environment variable is set (e.g., export ANTHROPIC_API_KEY="your-key")
model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet")

print("Initializing Agent Loop and connecting MCP tools...")

# 3. Open the sync communication bridge
with mcp_sync_client(server_params) as client:
    # Read available tools directly from your server.py metadata
    mcp_tools = client.list_tools()
    
    # Create an agent that solves problems by writing and executing Python blocks
    agent = CodeAgent(tools=mcp_tools, model=model)
    
    # 4. Trigger the agentic loop
    prompt = "Find the current temperature at coordinates 40.7128 (Lat) and -74.0060 (Lon). Is it freezing there?"
    response = agent.run(prompt)
    
    print("\n--- Final Agent Response ---")
    print(response)
```

# Step 4: Test and Troubleshoot Globally

To verify that your tools and routing pathways conform to the global protocol, test your script in the interactive web UI provided by the protocol creators:

```bash 
run mcp dev server.py
```

This boots up the MCP Inspector web panel. You can manually click "Call Tool", input test coordinates, and view the precise JSON chunks exchanged behind the scenes. Once verified, run `python agent.py` to see your agent loops make autonomous calculations.