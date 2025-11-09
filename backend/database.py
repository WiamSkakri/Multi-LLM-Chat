"""Database setup and connection management."""
import os
from contextlib import asynccontextmanager
from typing import Optional

import aiosqlite

DB_PATH = os.getenv("DB_PATH", "chat.db")
MAX_CONNECTIONS = 5


async def init_db():
    """Initialize database with schema."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Enable WAL mode for better concurrency
        await db.execute("PRAGMA journal_mode=WAL;")

        # Create tables
        await db.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                thread_id TEXT REFERENCES threads(id),
                role TEXT,
                content TEXT,
                model TEXT,
                mentions TEXT,
                target_message_id TEXT REFERENCES messages(id),
                is_complete BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS model_calls (
                id TEXT PRIMARY KEY,
                message_id TEXT REFERENCES messages(id),
                provider TEXT,
                model_name TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                cost_usd REAL,
                latency_ms INTEGER,
                finish_reason TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_thread_id 
            ON messages(thread_id)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_created_at 
            ON messages(created_at)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_model_calls_message_id 
            ON model_calls(message_id)
        """)

        await db.commit()


@asynccontextmanager
async def get_db():
    """Async context manager that yields a DB connection."""
    connection = await aiosqlite.connect(DB_PATH)
    try:
        yield connection
    finally:
        await connection.close()
