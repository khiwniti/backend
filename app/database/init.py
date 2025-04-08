from typing import Dict, Any
import json
from datetime import datetime
import uuid

async def init_database(db, cache_kv):
    """Initialize the database with required tables and initial data"""
    
    # Create tables
    await db.batch([
        db.prepare("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """),
        db.prepare("""
            CREATE TABLE IF NOT EXISTS inventory (
                id TEXT PRIMARY KEY,
                restaurant_id TEXT NOT NULL,
                ingredient_name TEXT NOT NULL,
                current_stock REAL NOT NULL,
                min_stock_level REAL NOT NULL,
                max_stock_level REAL NOT NULL,
                unit TEXT NOT NULL,
                supplier_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        """),
        db.prepare("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                min_order_quantity REAL,
                delivery_schedule TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """),
        db.prepare("""
            CREATE TABLE IF NOT EXISTS sales_data (
                id TEXT PRIMARY KEY,
                restaurant_id TEXT NOT NULL,
                date DATE NOT NULL,
                items_sold INTEGER NOT NULL,
                revenue REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
            )
        """),
        db.prepare("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id TEXT PRIMARY KEY,
                restaurant_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                ingredients JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
            )
        """),
        db.prepare("""
            CREATE TABLE IF NOT EXISTS customer_feedback (
                id TEXT PRIMARY KEY,
                restaurant_id TEXT NOT NULL,
                date DATE NOT NULL,
                review_text TEXT NOT NULL,
                rating INTEGER NOT NULL,
                sentiment_score REAL,
                topics JSON,
                keywords JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
            )
        """),
        db.prepare("""
            CREATE TABLE IF NOT EXISTS waste_records (
                id TEXT PRIMARY KEY,
                restaurant_id TEXT NOT NULL,
                ingredient_id TEXT NOT NULL,
                waste_quantity REAL NOT NULL,
                waste_reason TEXT,
                waste_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
                FOREIGN KEY (ingredient_id) REFERENCES inventory(id)
            )
        """)
    ])

    # Create indexes
    await db.batch([
        db.prepare("CREATE INDEX IF NOT EXISTS idx_inventory_restaurant ON inventory(restaurant_id)"),
        db.prepare("CREATE INDEX IF NOT EXISTS idx_sales_restaurant_date ON sales_data(restaurant_id, date)"),
        db.prepare("CREATE INDEX IF NOT EXISTS idx_feedback_restaurant_date ON customer_feedback(restaurant_id, date)"),
        db.prepare("CREATE INDEX IF NOT EXISTS idx_waste_restaurant_date ON waste_records(restaurant_id, waste_date)")
    ])

    # Initialize cache with empty values
    await cache_kv.put("restaurants:all", json.dumps([]))
    await cache_kv.put("suppliers:all", json.dumps([]))
    await cache_kv.put("inventory:all", json.dumps([]))
    await cache_kv.put("menu_items:all", json.dumps([]))

    return True 