"""
Database management module for Educational Performance Analytics.
Uses SQLite for persistent storage of datasets, student records, and saved analytical snapshots.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "educational_analytics.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create or connect to the SQLite database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Initialize database tables if they do not exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Table for saved datasets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        row_count INTEGER NOT NULL,
        columns_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)
    
    # Table for analytical snapshots / bookmarks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        dataset_name TEXT NOT NULL,
        filters_json TEXT NOT NULL,
        metrics_json TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL
    );
    """)
    
    conn.commit()
    conn.close()


def save_dataset_to_db(name: str, df: pd.DataFrame, description: str = "", db_path: str = DB_PATH) -> bool:
    """
    Save a DataFrame as a table in SQLite and register it in the datasets registry.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    clean_table_name = f"dataset_{''.join(c if c.isalnum() else '_' for c in name.lower()).strip('_')}"
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    columns_json = json.dumps(list(df.columns))
    
    try:
        # Save DataFrame to custom table
        df.to_sql(clean_table_name, conn, if_exists="replace", index=False)
        
        # Register in datasets table
        cursor.execute("""
        INSERT INTO datasets (name, description, row_count, columns_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            description=excluded.description,
            row_count=excluded.row_count,
            columns_json=excluded.columns_json,
            created_at=excluded.created_at
        """, (name, description, len(df), columns_json, created_at))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error while saving dataset: {e}")
        return False
    finally:
        conn.close()


def list_saved_datasets(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """List all registered datasets in SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, description, row_count, columns_json, created_at FROM datasets ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Database error while listing datasets: {e}")
        return []
    finally:
        conn.close()


def load_dataset_from_db(name: str, db_path: str = DB_PATH) -> Optional[pd.DataFrame]:
    """Load a dataset table by registered name from SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    clean_table_name = f"dataset_{''.join(c if c.isalnum() else '_' for c in name.lower()).strip('_')}"
    try:
        df = pd.read_sql(f"SELECT * FROM {clean_table_name}", conn)
        return df
    except Exception as e:
        print(f"Database error while loading dataset '{name}': {e}")
        return None
    finally:
        conn.close()


def delete_dataset_from_db(name: str, db_path: str = DB_PATH) -> bool:
    """Delete a dataset and its underlying table from SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    clean_table_name = f"dataset_{''.join(c if c.isalnum() else '_' for c in name.lower()).strip('_')}"
    try:
        cursor.execute("DELETE FROM datasets WHERE name = ?", (name,))
        cursor.execute(f"DROP TABLE IF EXISTS {clean_table_name}")
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error while deleting dataset '{name}': {e}")
        return False
    finally:
        conn.close()


def save_snapshot(title: str, dataset_name: str, filters: Dict[str, Any], metrics: Dict[str, Any], notes: str = "", db_path: str = DB_PATH) -> bool:
    """Save an analytical snapshot for reporting/bookmarking."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
        INSERT INTO snapshots (title, dataset_name, filters_json, metrics_json, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (title, dataset_name, json.dumps(filters), json.dumps(metrics), notes, created_at))
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error while saving snapshot: {e}")
        return False
    finally:
        conn.close()


def list_snapshots(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """List all saved analytical snapshots."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title, dataset_name, filters_json, metrics_json, notes, created_at FROM snapshots ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Database error while listing snapshots: {e}")
        return []
    finally:
        conn.close()
