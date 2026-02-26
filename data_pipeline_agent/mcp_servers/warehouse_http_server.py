from mcp.server.fastmcp import FastMCP
import sqlite3
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "database", "db.sqlite")

# DB_PATH = r"C:\Users\Gugan\Desktop\AI-Training-Assignment\data_pipeline_agent\database\db.sqlite"

mcp = FastMCP("Warehouse MCP")

@mcp.tool()
async def run_query(query: str) -> dict:
    """Run a SQL query on the warehouse database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)

        # If SELECT → return rows
        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            conn.close()
            return {"result": rows}
        
        # If INSERT / UPDATE / DELETE → commit and return affected rows
        else:
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return {"success": True, "rows_affected": affected}

    except Exception as e:
        return {"error": f"run_query failed: {str(e)}"}

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)