from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import uuid

class DatabaseService:
    def __init__(self, db, cache_kv):
        self.db = db
        self.cache_kv = cache_kv

    async def get_restaurant(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """Get restaurant data from D1"""
        cache_key = f"restaurant:{restaurant_id}"
        cached = await self.cache_kv.get(cache_key)
        if cached:
            return json.loads(cached)

        stmt = self.db.prepare("SELECT * FROM restaurants WHERE id = ?")
        result = await stmt.bind(restaurant_id).first()
        
        if result:
            await self.cache_kv.put(cache_key, json.dumps(result), expirationTtl=3600)
        return result

    async def get_inventory(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get inventory data from D1"""
        cache_key = f"inventory:{restaurant_id}"
        cached = await self.cache_kv.get(cache_key)
        if cached:
            return json.loads(cached)

        stmt = self.db.prepare("SELECT * FROM inventory WHERE restaurant_id = ?")
        results = await stmt.bind(restaurant_id).all()
        
        if results:
            await self.cache_kv.put(cache_key, json.dumps(results), expirationTtl=300)
        return results

    async def get_suppliers(self) -> List[Dict[str, Any]]:
        """Get all suppliers from D1"""
        cache_key = "suppliers:all"
        cached = await self.cache_kv.get(cache_key)
        if cached:
            return json.loads(cached)

        stmt = self.db.prepare("SELECT * FROM suppliers")
        results = await stmt.all()
        
        if results:
            await self.cache_kv.put(cache_key, json.dumps(results), expirationTtl=3600)
        return results

    async def get_sales_data(self, restaurant_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get sales data for a date range from D1"""
        cache_key = f"sales:{restaurant_id}:{start_date}:{end_date}"
        cached = await self.cache_kv.get(cache_key)
        if cached:
            return json.loads(cached)

        stmt = self.db.prepare("""
            SELECT * FROM sales_data 
            WHERE restaurant_id = ? AND date BETWEEN ? AND ?
            ORDER BY date
        """)
        results = await stmt.bind(restaurant_id, start_date, end_date).all()
        
        if results:
            await self.cache_kv.put(cache_key, json.dumps(results), expirationTtl=300)
        return results

    async def get_menu_items(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Get menu items from D1"""
        cache_key = f"menu_items:{restaurant_id}"
        cached = await self.cache_kv.get(cache_key)
        if cached:
            return json.loads(cached)

        stmt = self.db.prepare("SELECT * FROM menu_items WHERE restaurant_id = ?")
        results = await stmt.bind(restaurant_id).all()
        
        if results:
            await self.cache_kv.put(cache_key, json.dumps(results), expirationTtl=3600)
        return results

    async def get_customer_feedback(self, restaurant_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get customer feedback for a date range from D1"""
        cache_key = f"feedback:{restaurant_id}:{start_date}:{end_date}"
        cached = await self.cache_kv.get(cache_key)
        if cached:
            return json.loads(cached)

        stmt = self.db.prepare("""
            SELECT * FROM customer_feedback 
            WHERE restaurant_id = ? AND date BETWEEN ? AND ?
            ORDER BY date
        """)
        results = await stmt.bind(restaurant_id, start_date, end_date).all()
        
        if results:
            await self.cache_kv.put(cache_key, json.dumps(results), expirationTtl=300)
        return results

    async def get_waste_records(self, restaurant_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get waste records for a date range from D1"""
        cache_key = f"waste:{restaurant_id}:{start_date}:{end_date}"
        cached = await self.cache_kv.get(cache_key)
        if cached:
            return json.loads(cached)

        stmt = self.db.prepare("""
            SELECT * FROM waste_records 
            WHERE restaurant_id = ? AND waste_date BETWEEN ? AND ?
            ORDER BY waste_date
        """)
        results = await stmt.bind(restaurant_id, start_date, end_date).all()
        
        if results:
            await self.cache_kv.put(cache_key, json.dumps(results), expirationTtl=300)
        return results

    async def update_inventory(self, restaurant_id: str, inventory_data: List[Dict[str, Any]]) -> None:
        """Update inventory data in D1"""
        for item in inventory_data:
            stmt = self.db.prepare("""
                UPDATE inventory 
                SET current_stock = ?, min_stock_level = ?, max_stock_level = ?
                WHERE id = ? AND restaurant_id = ?
            """)
            await stmt.bind(
                item["current_stock"],
                item["min_stock_level"],
                item["max_stock_level"],
                item["id"],
                restaurant_id
            ).run()

        # Invalidate cache
        await self.cache_kv.delete(f"inventory:{restaurant_id}")

    async def add_sales_data(self, restaurant_id: str, sales_data: List[Dict[str, Any]]) -> None:
        """Add new sales data to D1"""
        for sale in sales_data:
            stmt = self.db.prepare("""
                INSERT INTO sales_data (id, restaurant_id, date, items_sold, revenue)
                VALUES (?, ?, ?, ?, ?)
            """)
            await stmt.bind(
                str(uuid.uuid4()),
                restaurant_id,
                sale["date"],
                sale["items_sold"],
                sale["revenue"]
            ).run()

        # Invalidate cache
        await self.cache_kv.delete(f"sales:{restaurant_id}:*")

    async def add_customer_feedback(self, restaurant_id: str, feedback_data: List[Dict[str, Any]]) -> None:
        """Add new customer feedback to D1"""
        for feedback in feedback_data:
            stmt = self.db.prepare("""
                INSERT INTO customer_feedback (
                    id, restaurant_id, date, review_text, rating, 
                    sentiment_score, topics, keywords
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """)
            await stmt.bind(
                str(uuid.uuid4()),
                restaurant_id,
                feedback["date"],
                feedback["review_text"],
                feedback["rating"],
                feedback.get("sentiment_score"),
                json.dumps(feedback.get("topics", [])),
                json.dumps(feedback.get("keywords", []))
            ).run()

        # Invalidate cache
        await self.cache_kv.delete(f"feedback:{restaurant_id}:*")

    async def add_waste_record(self, restaurant_id: str, waste_data: Dict[str, Any]) -> None:
        """Add new waste record to D1"""
        stmt = self.db.prepare("""
            INSERT INTO waste_records (
                id, restaurant_id, ingredient_id, waste_quantity, 
                waste_reason, waste_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """)
        await stmt.bind(
            str(uuid.uuid4()),
            restaurant_id,
            waste_data["ingredient_id"],
            waste_data["waste_quantity"],
            waste_data["waste_reason"],
            waste_data["waste_date"]
        ).run()

        # Invalidate cache
        await self.cache_kv.delete(f"waste:{restaurant_id}:*") 