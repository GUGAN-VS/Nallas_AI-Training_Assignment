# ETL Job Monitoring Agent

An AI-powered data engineering copilot that lets you monitor ETL pipelines, query job statuses, and trigger pipeline runs using **natural language** — no SQL required.

Built with **LangChain**, **Groq LLM**, and **Model Context Protocol (MCP)**.

---

## Features

- Natural language interface to your jobs database
- Smart pipeline triggering (only re-runs failed or missing jobs)
- Automatic table creation if the jobs table doesn't exist
- Job health validation with detailed issue reporting
- Schema inspection without writing SQL
- Full CRUD support (SELECT, INSERT, UPDATE, DELETE)

---

## Project Structure

```
demo_project/
├── main.py                  # Main agent entrypoint
├── database/
│   └── db.sqlite                 # SQLite database
├── etl/
│   ├── pipeline.py               # ETL pipeline logic
│   └── validate.py               # Job validation logic
└── mcp_servers/
    ├── warehouse_http_server.py  # Port 9001 — SQL execution
    ├── schema_http_server.py     # Port 9002 — Schema inspection
    └── etl_stdio_server.py       # STDIO — Pipeline & validation
```

---

## Prerequisites

- Python 3.12+
- Virtual environment with dependencies installed
- Groq API key

---

## Installation

```bash
# Clone the repo and navigate to project
git clone

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

cd data_pipeline_agent
```

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

---

## Running the System

Open **3 separate terminals** and run:

```bash
# Terminal 1 — Warehouse HTTP Server (port 9001)
py -m data_pipeline_agent.mcp_servers.warehouse_http_server

# Terminal 2 — Schema HTTP Server (port 9002)
py -m data_pipeline_agent.mcp_servers.schema_http_server

# Terminal 3 — Agent
py data_pipeline_agent/main.py
```

The ETL stdio server starts automatically when the agent connects.

---

## Database Schema

### `jobs` table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| job_name | VARCHAR(100) | Name of the ETL job |
| status | VARCHAR(20) | `SUCCESS` or `FAILED` |
| start_time | TIMESTAMP | Job start time |
| end_time | TIMESTAMP | Job end time |
| created_at | TIMESTAMP | Record creation time |

### Default Jobs
- `daily_sales_etl`
- `customer_sync`
- `inventory_update`
- `reporting_job`

---

## MCP Servers

| Server | Transport | Port | Tools |
|--------|-----------|------|-------|
| warehouse_http_server.py | HTTP | 9001 | `run_query` |
| schema_http_server.py | HTTP | 9002 | `get_table_schema` |
| etl_stdio_server.py | STDIO | — | `trigger_pipeline`, `validate_pipeline` |

---

## Sample Questions

### Job Monitoring
```
List all jobs with their status
Show me all failed jobs
How many jobs failed vs succeeded?
What is the overall success rate?
What is the latest status of customer_sync?
```

### ETL Operations
```
Trigger the pipeline
Validate the jobs and tell me if anything is wrong
Trigger the pipeline and check its status after
```

### Database Operations
```
What columns does the jobs table have?
Delete all data from jobs
Modify reporting_job status to FAILED
Create the jobs table if it doesn't exist
```

### Combined Workflows
```
Trigger pipeline, validate, then show any failures
Validate jobs and if unhealthy, show last run time
```

---

## Pipeline Logic

The pipeline uses a smart re-run strategy:

| Scenario | Action |
|----------|--------|
| No jobs table | Creates table + runs all 4 jobs |
| No jobs run today | Runs all 4 jobs fresh |
| Some jobs failed today | Re-runs only the failed jobs (UPDATE) |
| All jobs succeeded today | Skips — returns "nothing to re-run" |

---

## LLM Configuration

```python
llm = ChatGroq(
    model="moonshotai/kimi-k2-instruct",  # Primary
    temperature=0,
    max_tokens=1024
)
```
---

## Known Issues & Fixes

| Issue | Fix |
|-------|-----|
| `unable to open database file` | Use hardcoded absolute `DB_PATH` in all server files |
| `no such column` error | System prompt forces schema check before every query |
| DELETE/UPDATE not persisting | `conn.commit()` added for all write operations |
| Pipeline creates duplicates | Smart re-run: UPDATE failed records, skip successes |

---

## Future Enhancements

- Alert notifications (email/Slack) on job failure
- Pipeline scheduling with APScheduler
- Real data extraction from CSV / external APIs
- Job retry logic with configurable max attempts
- Web dashboard for visual monitoring
- Multi-database support (PostgreSQL, MySQL)

---

## Architecture Diagram

```
User Input (natural language)
        │
        ▼
   main.py (LangChain Agent)
        │
        ├──► Groq LLM (kimi-k2-instruct)
        │         │
        │    decides which tools to call
        │
        ├──► run_query ──────────► warehouse_http_server.py (port 9001)
        │                                    │
        ├──► get_table_schema ───► schema_http_server.py (port 9002)
        │                                    │
        └──► trigger_pipeline               SQLite DB
             validate_pipeline  ──► etl_stdio_server.py (STDIO)
                                             │
                                        pipeline.py
                                        validate.py
```
