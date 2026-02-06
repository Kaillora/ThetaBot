"""Persistent state management for tracking seen jobs"""
import json
import os
from datetime import datetime
from typing import Set
from pathlib import Path


class StateManager:
    """Manages persistent state for seen jobs and last check times"""

    def __init__(self, state_file: str = "data/job_state.json"):
        self.state_file = Path(state_file)
        self._state = self._load()

    def _load(self) -> dict:
        """Load state from JSON file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {"last_checked": None, "seen": []}

    def save(self) -> None:
        """Save current state to JSON file"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self._state, f, indent=2)

    @property
    def seen_jobs(self) -> Set[str]:
        """Get set of seen job IDs"""
        return set(self._state["seen"])

    def is_seen(self, job_id: str) -> bool:
        """Check if a job has been seen before"""
        return job_id in self._state["seen"]

    def mark_seen(self, job_ids: list[str]) -> None:
        """Mark jobs as seen and save"""
        self._state["seen"].extend(job_ids)
        self._state["last_checked"] = datetime.utcnow().isoformat()
        self.save()

    @property
    def last_checked(self) -> str | None:
        """Get last checked timestamp"""
        return self._state.get("last_checked")
