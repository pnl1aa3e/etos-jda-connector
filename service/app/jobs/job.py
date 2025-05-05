import asyncio
import logging
from abc import ABCMeta, abstractmethod
from pathlib import Path

import httpx
from pydantic import BaseModel

from app.settings import GraphQLSettings, JDASettings, Settings
from app.utils_oracle import create_oracle_connection

logger = logging.getLogger(__name__)

jda_settings = JDASettings()
graphql_settings = GraphQLSettings()


class Job(metaclass=ABCMeta):
    """Main class for all jobs."""

    def __init__(self):
        super().__init__()
        self.global_settings = Settings()
        self.jda_connection = create_oracle_connection()
        self.supergraph_client = httpx.Client(
            base_url=graphql_settings.supergraph_url, headers=graphql_settings.authorization_header
        )

    @abstractmethod
    def task(self) -> None:
        """Implement tasks for the job."""
        raise NotImplementedError("Task method must be implemented.")

    def run(self) -> None:
        """Run the job."""
        job_name = to_screaming_snake_case(self.__class__.__name__)
        logger.info(f"JOB_{job_name}: ALERT_001_{job_name}_START")
        try:
            self.task()
            logger.info(f"JOB_{job_name}: ALERT_001_{job_name}_COMPLETE")
        except Exception as error:
            logger.error({"msg": f"JOB_{job_name} ERROR", "error": str(error)})
            raise error

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ros_connection.close()
        self.supergraph_client.close()


class Checkpoint:
    def __init__(self, name: str, checkpoint_path: str):
        self.name: str = name
        self.checkpoint_path: str = checkpoint_path
        self.new_checkpoint_on_success: str | None = None

    def save_checkpoint(self, checkpoint_value: str) -> None:
        """Save checkpoint value."""
        checkpoint_path = Path(self.checkpoint_path) / self.name
        checkpoint_path.write_text(str(checkpoint_value))

    def update_checkpoint(self) -> None:
        """Update checkpoint value."""
        if self.new_checkpoint_on_success:
            self.save_checkpoint(self.new_checkpoint_on_success)

    def read_checkpoint(self) -> str | None:
        """Read checkpoint value."""
        checkpoint_path = Path(self.checkpoint_path) / self.name
        if checkpoint_path.exists():
            return checkpoint_path.read_text()
        else:
            return None
        
def to_screaming_snake_case(text: str) -> str:
    """Convert PascalCase to SCREAMING_SNAKE_CASE."""
    return "".join(["_" + c.lower() if c.isupper() else c for c in text]).lstrip("_").upper()
