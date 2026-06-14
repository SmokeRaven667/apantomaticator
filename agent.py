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

## 2. Initialize your chosen LLM (LiteLLM dynamically loads your free API keys)
## Ensure your environment variable is set (e.g., export ANTHROPIC_API_KEY="your-key")
model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet")

print("Initializing Agent Loop and connecting MCP tools...")

## 3. Open the sync communication bridge
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