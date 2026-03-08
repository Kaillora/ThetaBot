"""PostgreSQL-backed state management for tracking jobs"""
import psycopg2
import psycopg2.extras 
from datetime import datetime
from typing import Optional

from ..config import DATABASE_CONFIG


class StateManager:
    """Manages job persistence and Discord posting status via PostgreSQL"""

    def __init__(self):
        self.conn = psycopg2.connect(**DATABASE_CONFIG)
        self.conn.autocommit = True
        self._create_table()

    def _ensure_connection(self):
        """Reconnect to PostgreSQL if the connection was lost or timed out"""
        try:
            if self.conn.closed:
                raise psycopg2.OperationalError("connection closed")
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            self.conn = psycopg2.connect(**DATABASE_CONFIG)
            self.conn.autocommit = True

    def _create_table(self):
        """Create jobs table if it doesn't exist"""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cycle_metrics (
                    id                SERIAL PRIMARY KEY,
                    cycle_time        TIMESTAMP DEFAULT NOW(),
                    jobs_scraped      INTEGER NOT NULL DEFAULT 0,
                    jobs_new          INTEGER NOT NULL DEFAULT 0,
                    jobs_classified   INTEGER NOT NULL DEFAULT 0,
                    jobs_posted       INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    id                SERIAL PRIMARY KEY,
                    unique_id         TEXT NOT NULL UNIQUE,
                    company           VARCHAR(255) NOT NULL,
                    title             VARCHAR(255) NOT NULL,
                    location          TEXT NOT NULL,
                    apply_link        TEXT NOT NULL,
                    date_posted       VARCHAR(50) NOT NULL,
                    source            VARCHAR(50) NOT NULL,
                    category          VARCHAR(100),
                    first_seen_at     TIMESTAMP DEFAULT NOW(),
                    posted_to_discord BOOLEAN DEFAULT FALSE,
                    posted_at         TIMESTAMP
                )
            """)

    def store_jobs(self, jobs) -> list[int]:
        """Store a list of Job objects into the database.

        Uses INSERT ... ON CONFLICT to avoid duplicates.
        Returns the IDs of newly inserted jobs.
        """
        if not jobs:
            return []
        self._ensure_connection()

        values = [
            (j.unique_id, j.company, j.title, j.location,
             j.apply_link, j.date_posted, j.source, j.category,)
            for j in jobs
        ]

        with self.conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """INSERT INTO jobs (unique_id, company, title, location,
                   apply_link, date_posted, source, category)
                   VALUES %s ON CONFLICT (unique_id) DO NOTHING RETURNING id""",
                values
            )
            return [row[0] for row in cur.fetchall()]

    def update_category(self, job_id: int, category: str) -> None:
        """Update the category for a job by its database ID"""
        self._ensure_connection()
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE jobs SET category = %s WHERE id = %s",
                (category, job_id)
            )

    def get_unposted_jobs(self, job_ids: list[int]) -> list[dict]:
        """Get unposted jobs by their IDs (newly inserted this cycle)."""
        if not job_ids:
            return []
        self._ensure_connection()
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM jobs WHERE id = ANY(%s) AND posted_to_discord = FALSE",
                (job_ids,)
            )
            return cur.fetchall()

    def mark_posted(self, job_ids: list[int]) -> None:
        """Mark jobs as posted to Discord by their database IDs"""
        if not job_ids:
            return
        self._ensure_connection()
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE jobs SET posted_to_discord = TRUE, posted_at = NOW() WHERE id = ANY(%s)",
                (job_ids,)
            )

    def is_seen(self, unique_id: str) -> bool:
        """Check if a job unique_id exists in the database (backward compat)"""
        self._ensure_connection()
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM jobs WHERE unique_id = %s", (unique_id,))
            return cur.fetchone() is not None

    def log_cycle(self, jobs_scraped: int, jobs_new: int, jobs_classified: int, jobs_posted: int) -> None:
        """Log metrics for a single check_jobs cycle"""
        self._ensure_connection()
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO cycle_metrics (jobs_scraped, jobs_new, jobs_classified, jobs_posted)
                   VALUES (%s, %s, %s, %s)""",
                (jobs_scraped, jobs_new, jobs_classified, jobs_posted)
            )

    def get_metrics_summary(self) -> dict:
        """Get aggregate metrics across all cycles"""
        self._ensure_connection()
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total_cycles,
                    SUM(jobs_scraped) AS total_scraped,
                    SUM(jobs_new) AS total_new,
                    SUM(jobs_classified) AS total_classified,
                    SUM(jobs_posted) AS total_posted,
                    MIN(cycle_time) AS first_cycle,
                    MAX(cycle_time) AS last_cycle
                FROM cycle_metrics
            """)
            return cur.fetchone()

    def close(self):
        """Close the database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
