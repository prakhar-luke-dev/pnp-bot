import os
from typing import Dict, Optional

from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import (
    text,
    create_engine,
    Column, Integer,
    String, DateTime,
    Table,
    MetaData,
    select,
    insert,
)
from sqlalchemy.orm import Session, sessionmaker


# Load environment variables only once
load_dotenv(override=True)

# Constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
LOG_FILES = ["app.log", "vdb.log", "graph.log", "sql_agent.log"]




class Config:
    """Centralized configuration management"""

    # Bot configuration
    BOT_NAME = os.getenv("BOT_NAME")

    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

    # Auth
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    # View logs
    DISPLAY_LOGS = os.getenv("DISPLAY_LOGS", "false").lower() == "true"
    LOG_KEY = os.getenv("LOG_KEY")
    LOG_PATH = "logs/"

    # Server configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8001"))  # Default port if not specified

    # LLM inference provide configs
    DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_TOKEN")
    DEEPINFRA_BASE_URL = os.getenv("DEEPINFRA_BASE_URL")

    # RAG (pinecone index)
    INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    EMBEDDING_MODEL_ID = "intfloat/multilingual-e5-large"

    # SQL configs
    SQL_DB_NAME = os.getenv('DB_NAME')
    SQL_DB_USER = os.getenv('DB_USER')
    SQL_DB_PASSWORD = os.getenv('DB_PASS')
    SQL_DB_HOST = os.getenv('DB_HOST')
    SQL_DB_PORT = os.getenv('DB_PORT')
    SQL_LLM_MODE = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    # Langfuse configuration
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")
    LANGFUSE_TRACE_TAGS = ["R1.4", "v0.1"]

    # Database configuration for chat history
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    PSQL_CONTAINER_NAME = os.getenv("PSQL_CONTAINER_NAME")
    PSQL_CONTAINER_PORT = os.getenv("PSQL_CONTAINER_PORT", "5432")

    POSTGRES_URI = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}?"

    # Memory connection kwargs
    MEMORY_CONNECTION_KWARGS: Dict = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

    POSTGRES_LISTING_URI = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{PSQL_CONTAINER_NAME}:{PSQL_CONTAINER_PORT}/{POSTGRES_DB}?sslmode=disable"
    engine = create_engine(
        POSTGRES_LISTING_URI,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        future=True)

    metadata = MetaData()

    users = Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', String, nullable=False),
        Column('session_id', String, nullable=False),
        Column('thread_id', String, nullable=False),
        Column('brand_id', String, nullable=False),
        Column('created_at', DateTime, default=datetime.now)
    )


# Pydantic models for output schema
class DecomposedQueryFormat(BaseModel):
    """Decomposed query on different levels"""
    strategy_query: Optional[str] = Field(default=None,
                                          description="Strategy-related query or 'None' if not applicable")
    data_query: Optional[str] = Field(default=None, description="Data-related query or 'None' if not applicable")

