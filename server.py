import httpx
from mcp.server.fastmcp import FastMCP

# initialize the FastMCP server
mcp = FastMCP("Weather Investigator")

@mcp.tool()
def get_temperature(latitude: float, longitude: float) -> str:
    """
    Fetches the current temperature for a given latitude and longitude.
    Always use this tool when asked about weather or temperatures.
    """
    # Use a weather API to get the temperature (replace with your actual API endpoint and key)
    url = f"https://open-meteo.com{latitude}&longitude={longitude}&current=temperature_2m"

    # Make a completely free, no-API-key HTTP request
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