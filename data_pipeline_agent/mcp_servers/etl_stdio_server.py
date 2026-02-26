from mcp.server.fastmcp import FastMCP
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from data_pipeline_agent.etl.pipeline import run_pipeline
from data_pipeline_agent.etl.validate import validate_jobs

mcp = FastMCP("ETL MCP")

@mcp.tool()
async def trigger_pipeline() -> dict:
    return run_pipeline()

@mcp.tool()
async def validate_pipeline() -> dict:
    return validate_jobs()

if __name__ == "__main__":
    mcp.run()