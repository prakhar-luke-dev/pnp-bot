import json
import logging
import os
from functools import lru_cache
from pathlib import Path

import bugsnag
import logstash
from bugsnag.handlers import BugsnagHandler
from dotenv import load_dotenv, find_dotenv
from logs_operations.logger_setup import setup_logger

# Load environment variables only once
load_dotenv(find_dotenv(), override=True)

# Constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
LOG_FILES = ["app.log", "vdb.log", "graph.log", "sql_agent.log"]



class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "path": record.pathname,
            "line_number": record.lineno,
            "function": record.funcName,
        }
        return json.dumps(log_entry).encode("utf-8") + b'\n'  # Return bytes instead of str



class LogConfig(logging.Formatter):
    """Centralized configuration management"""

    # API Keys and services
    BUGSNAG_API = os.getenv("BUGSNAG_API", None)
    LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", None)
    LOGSTASH_PORT = os.getenv("LOGSTASH_PORT", None)


    @classmethod
    def get_log_dir(cls) -> Path:
        """Get the logs directory path"""
        return Path(__file__).resolve().parent.parent / "logs"

    @classmethod
    def get_log_path(cls, filename: str) -> Path:
        """Get the full path for a log file"""
        return cls.get_log_dir() / filename



if LogConfig.BUGSNAG_API is not None:
    # Configure Bugsnag once
    bugsnag.configure(
        api_key=LogConfig.BUGSNAG_API,
        project_root="app_vida"
    )


def configure_logger(name: str, log_file: str, handler_to_add = None) -> logging.Logger:
    """Configure a logger with Bugsnag integration"""
    log_file_path = Path(__file__).resolve().parent.parent / "logs"
    logger = setup_logger(
        log_file=f"{log_file_path}/{log_file}",
        log_handler=f"{name}-logger",
        backup=10,
        log_format=LOG_FORMAT,
        _utc=True,
    )
    if LogConfig.BUGSNAG_API is not None:
        # Add Bugsnag handler
        handler = BugsnagHandler()
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)
    if handler_to_add is not None:
        logger.addHandler(handler_to_add)
    return logger



# Setup loggers for different tasks - lazy loading
@lru_cache(maxsize=None)
def get_app_logger():
    return configure_logger("app", "app.log")


@lru_cache(maxsize=None)
def get_vector_db_logger():
    return configure_logger("vector-db", "vdb.log")


@lru_cache(maxsize=None)
def get_graph_logger():
    return configure_logger("graph", "graph.log")


@lru_cache(maxsize=None)
def get_sql_agent_logger():
    logger = configure_logger("sql-db", "sql_agent.log")
    logger.setLevel(logging.INFO)
    return logger


def create_log_files():
    """Create log directories and files if they don't exist"""
    log_dir = LogConfig.get_log_dir()

    # Ensure the logs directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create each log file if it does not exist
    for log_file in LOG_FILES:
        log_path = log_dir / log_file
        if not log_path.exists():
            log_path.touch()  # Create an empty file
            print(f"Created: {log_path}")
        else:
            print(f"Exists: {log_path}")


# Initialize loggers and files when imported
app_logger = get_app_logger()
vector_db_logger = get_vector_db_logger()
graph_logger = get_graph_logger()
sql_agent_logger = get_sql_agent_logger()

# Ensure log files exist
# create_log_files()
