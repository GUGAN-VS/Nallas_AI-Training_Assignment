from mcp.server.fastmcp import FastMCP
import sqlite3
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "database", "db.sqlite")

# DB_PATH = r"C:\Users\Gugan\Desktop\AI-Training-Assignment\data_pipeline_agent\database\db.sqlite"


mcp = FastMCP("Schema MCP")

@mcp.tool()
async def get_table_schema(table_name: str) -> dict:
    """Get the schema (columns and types) of a given table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        if not columns:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return {"error": f"Table '{table_name}' not found.", "available_tables": tables}

        schema = [
            {
                "name": col[1],
                "type": col[2],
                "not_null": bool(col[3]),
                "primary_key": bool(col[5])
            }
            for col in columns
        ]
        conn.close()
        return {"table": table_name, "schema": schema}
    except Exception as e:
        return {"error": f"get_table_schema failed: {str(e)}"}

app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9002)