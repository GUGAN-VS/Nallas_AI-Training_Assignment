import sqlite3
from datetime import datetime, timedelta
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "database", "db.sqlite")

# DB_PATH = r"C:\Users\Gugan\Desktop\AI-Training-Assignment\data_pipeline_agent\database\db.sqlite"


def validate_jobs():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        issues = []

        # Check 1: Failed jobs
        cursor.execute("SELECT job_name FROM jobs WHERE UPPER(status) = 'FAILED'")
        failed = [row[0] for row in cursor.fetchall()]
        if failed:
            issues.append({"issue": "Failed jobs found", "jobs": failed})

        # Check 2: Jobs not run in last 2 days
        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        cursor.execute(
            "SELECT job_name, MAX(created_at) FROM jobs GROUP BY job_name HAVING MAX(created_at) < ?",
            (two_days_ago,)
        )
        stale = [{"job": row[0], "last_run": row[1]} for row in cursor.fetchall()]
        if stale:
            issues.append({"issue": "Stale jobs", "jobs": stale})

        conn.close()

        return {"status": "healthy"} if not issues else {"status": "unhealthy", "issues": issues}

    except Exception as e:
        return {"error": str(e)}