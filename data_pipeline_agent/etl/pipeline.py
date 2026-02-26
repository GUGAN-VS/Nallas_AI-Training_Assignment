import sqlite3
import random
from datetime import datetime
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "database", "db.sqlite")

# DB_PATH = r"C:\Users\Gugan\Desktop\AI-Training-Assignment\data_pipeline_agent\database\db.sqlite"


DEFAULT_JOBS = [
    "daily_sales_etl",
    "customer_sync", 
    "inventory_update",
    "reporting_job"
]

def ensure_table_exists(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name VARCHAR(100) NOT NULL,
            status VARCHAR(20) NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

def run_pipeline():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Step 1: Create table if not exists
        ensure_table_exists(cursor)
        conn.commit()

        today = datetime.now().date().isoformat()

        # Step 2: Check if any jobs exist today
        cursor.execute("SELECT DISTINCT job_name FROM jobs WHERE DATE(created_at) = ?", (today,))
        existing_today = [row[0] for row in cursor.fetchall()]

        # Step 3: Check for failed jobs today
        cursor.execute("""
            SELECT DISTINCT job_name FROM jobs
            WHERE UPPER(status) = 'FAILED'
            AND DATE(created_at) = ?
        """, (today,))
        failed_today = [row[0] for row in cursor.fetchall()]

        # Step 4: Determine which jobs to run
        # - Jobs that failed today → re-run (update)
        # - Jobs not yet run today → run fresh (insert)
        jobs_to_run = failed_today + [j for j in DEFAULT_JOBS if j not in existing_today]

        if not jobs_to_run:
            conn.close()
            return {
                "pipeline_run": "skipped",
                "message": "All jobs already succeeded today. Nothing to re-run.",
                "date": today
            }

        results = []
        now = datetime.now().isoformat()

        for job_name in jobs_to_run:
            status = "SUCCESS" if random.random() > 0.2 else "FAILED"

            # Update if failed record exists today
            cursor.execute("""
                UPDATE jobs SET status = ?, start_time = ?, end_time = ?
                WHERE job_name = ?
                AND UPPER(status) = 'FAILED'
                AND DATE(created_at) = ?
            """, (status, now, now, job_name, today))

            # Insert if no record today
            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO jobs (job_name, status, start_time, end_time)
                    VALUES (?, ?, ?, ?)
                """, (job_name, status, now, now))

            results.append({"job": job_name, "status": status})

        conn.commit()
        conn.close()

        return {
            "pipeline_run": "completed",
            "jobs_executed": len(results),
            "jobs": results,
            "date": today
        }

    except Exception as e:
        return {"error": str(e)}