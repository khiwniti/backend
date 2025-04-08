from typing import Optional, List, Dict, Any
import os
from datetime import datetime
import json
from functools import lru_cache
import sqlite3
import aiosqlite
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection handler for SQLite operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "bitebase.db")
        self.connection: Optional[aiosqlite.Connection] = None
        
    async def connect(self):
        """Establish database connection"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            self.connection = await aiosqlite.connect(self.db_path)
            self.connection.row_factory = aiosqlite.Row
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
            
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
            
    async def execute(self, query: str, params: tuple = None) -> None:
        """Execute a query without returning results"""
        try:
            async with self.connection.execute(query, params or ()) as cursor:
                await self.connection.commit()
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
            
    async def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute a query and return a single row"""
        try:
            async with self.connection.execute(query, params or ()) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching one row: {e}")
            raise
            
    async def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return all rows"""
        try:
            async with self.connection.execute(query, params or ()) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all rows: {e}")
            raise
            
    async def create_tables(self):
        """Create all necessary database tables"""
        try:
            # Create restaurants table
            await self.execute("""
                CREATE TABLE IF NOT EXISTS restaurants (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create inventory table
            await self.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id TEXT PRIMARY KEY,
                    restaurant_id TEXT NOT NULL,
                    ingredient_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    min_quantity REAL,
                    max_quantity REAL,
                    last_restocked TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
                )
            """)
            
            # Create suppliers table
            await self.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    min_order_quantity REAL,
                    delivery_days TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create menu_items table
            await self.execute("""
                CREATE TABLE IF NOT EXISTS menu_items (
                    id TEXT PRIMARY KEY,
                    restaurant_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    ingredients TEXT,
                    is_available BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
                )
            """)
            
            # Create sales_data table
            await self.execute("""
                CREATE TABLE IF NOT EXISTS sales_data (
                    id TEXT PRIMARY KEY,
                    restaurant_id TEXT NOT NULL,
                    menu_item_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_price REAL NOT NULL,
                    sale_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
                )
            """)
            
            # Create customer_feedback table
            await self.execute("""
                CREATE TABLE IF NOT EXISTS customer_feedback (
                    id TEXT PRIMARY KEY,
                    restaurant_id TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    review_text TEXT,
                    sentiment_score REAL,
                    topics TEXT,
                    keywords TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
                )
            """)
            
            # Create waste_records table
            await self.execute("""
                CREATE TABLE IF NOT EXISTS waste_records (
                    id TEXT PRIMARY KEY,
                    restaurant_id TEXT NOT NULL,
                    ingredient_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    reason TEXT,
                    waste_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
                )
            """)
            
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    async def execute_many(self, query: str, params_list: List[tuple]):
        """Execute a query multiple times with different parameters"""
        if not self.connection:
            await self.connect()
        
        await self.connection.executemany(query, params_list)

    async def commit(self):
        """Commit the current transaction"""
        if self.connection:
            await self.connection.commit()

    async def rollback(self):
        """Rollback the current transaction"""
        if self.connection:
            await self.connection.rollback()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _init_cache(self):
        """Initialize cache with default values"""
        self.cache = {
            "restaurants": {},
            "inventory": {},
            "suppliers": {},
            "sales_data": {},
            "menu_items": {},
            "customer_feedback": {},
            "waste_records": {}
        }

    async def get_cached_data(self, key: str) -> Optional[dict]:
        """Get data from cache"""
        try:
            data = await self.cache_kv.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error getting cached data: {e}")
            return None

    async def set_cached_data(self, key: str, data: dict, ttl: int = 300):
        """Set data in cache with TTL"""
        try:
            await self.cache_kv.put(key, json.dumps(data), expiration_ttl=ttl)
        except Exception as e:
            print(f"Error setting cached data: {e}")

    async def invalidate_cache(self, prefix: str):
        """Invalidate cache entries with given prefix"""
        try:
            keys = await self.cache_kv.list(prefix=prefix)
            for key in keys:
                await self.cache_kv.delete(key)
        except Exception as e:
            print(f"Error invalidating cache: {e}")

    @lru_cache(maxsize=128)
    def get_db_connection(self):
        """Get cached database connection"""
        return self.connection

    async def execute_query(self, query: str, params: tuple = None):
        """Execute a single query"""
        try:
            stmt = self.connection.prepare(query)
            if params:
                return await stmt.bind(*params).run()
            return await stmt.run()
        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    async def execute_batch(self, queries: list):
        """Execute a batch of queries"""
        try:
            prepared = [self.connection.prepare(q) for q in queries]
            return await self.connection.batch(prepared)
        except Exception as e:
            print(f"Error executing batch: {e}")
            raise 