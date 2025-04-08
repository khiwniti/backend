from typing import List, Optional, Dict, Any
from datetime import datetime
from .connection import DatabaseConnection
from .models import (
    Restaurant, Inventory, Supplier, MenuItem,
    SalesData, CustomerFeedback, WasteRecord
)

class DatabaseOperations:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    async def create_restaurant(self, restaurant: Restaurant) -> Restaurant:
        query = """
        INSERT INTO restaurants (id, name, address, phone, email, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(
            query,
            (
                str(restaurant.id), restaurant.name, restaurant.address,
                restaurant.phone, restaurant.email,
                restaurant.created_at, restaurant.updated_at
            )
        )
        return restaurant

    async def get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        query = "SELECT * FROM restaurants WHERE id = ?"
        result = await self.db.execute(query, (restaurant_id,))
        if result:
            return Restaurant(**result[0])
        return None

    async def update_restaurant(self, restaurant: Restaurant) -> Restaurant:
        query = """
        UPDATE restaurants
        SET name = ?, address = ?, phone = ?, email = ?, updated_at = ?
        WHERE id = ?
        """
        await self.db.execute(
            query,
            (
                restaurant.name, restaurant.address, restaurant.phone,
                restaurant.email, datetime.utcnow(), str(restaurant.id)
            )
        )
        return restaurant

    async def create_inventory(self, inventory: Inventory) -> Inventory:
        query = """
        INSERT INTO inventory (
            id, restaurant_id, ingredient_name, quantity, unit,
            min_quantity, max_quantity, last_restocked, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(
            query,
            (
                str(inventory.id), str(inventory.restaurant_id),
                inventory.ingredient_name, inventory.quantity,
                inventory.unit, inventory.min_quantity,
                inventory.max_quantity, inventory.last_restocked,
                inventory.created_at, inventory.updated_at
            )
        )
        return inventory

    async def get_inventory(self, restaurant_id: str) -> List[Inventory]:
        query = "SELECT * FROM inventory WHERE restaurant_id = ?"
        results = await self.db.execute(query, (restaurant_id,))
        return [Inventory(**result) for result in results]

    async def update_inventory(self, inventory: Inventory) -> Inventory:
        query = """
        UPDATE inventory
        SET quantity = ?, min_quantity = ?, max_quantity = ?,
            last_restocked = ?, updated_at = ?
        WHERE id = ?
        """
        await self.db.execute(
            query,
            (
                inventory.quantity, inventory.min_quantity,
                inventory.max_quantity, inventory.last_restocked,
                datetime.utcnow(), str(inventory.id)
            )
        )
        return inventory

    async def create_supplier(self, supplier: Supplier) -> Supplier:
        query = """
        INSERT INTO suppliers (
            id, name, contact_person, phone, email, address,
            min_order_quantity, delivery_days, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(
            query,
            (
                str(supplier.id), supplier.name, supplier.contact_person,
                supplier.phone, supplier.email, supplier.address,
                supplier.min_order_quantity, str(supplier.delivery_days),
                supplier.created_at, supplier.updated_at
            )
        )
        return supplier

    async def get_suppliers(self) -> List[Supplier]:
        query = "SELECT * FROM suppliers"
        results = await self.db.execute(query)
        return [Supplier(**result) for result in results]

    async def create_menu_item(self, menu_item: MenuItem) -> MenuItem:
        query = """
        INSERT INTO menu_items (
            id, restaurant_id, name, description, price,
            ingredients, is_available, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(
            query,
            (
                str(menu_item.id), str(menu_item.restaurant_id),
                menu_item.name, menu_item.description,
                menu_item.price, str(menu_item.ingredients),
                menu_item.is_available, menu_item.created_at,
                menu_item.updated_at
            )
        )
        return menu_item

    async def get_menu_items(self, restaurant_id: str) -> List[MenuItem]:
        query = "SELECT * FROM menu_items WHERE restaurant_id = ?"
        results = await self.db.execute(query, (restaurant_id,))
        return [MenuItem(**result) for result in results]

    async def record_sale(self, sale: SalesData) -> SalesData:
        query = """
        INSERT INTO sales_data (
            id, restaurant_id, menu_item_id, quantity,
            total_price, sale_date, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(
            query,
            (
                str(sale.id), str(sale.restaurant_id),
                str(sale.menu_item_id), sale.quantity,
                sale.total_price, sale.sale_date,
                sale.created_at
            )
        )
        return sale

    async def get_sales_data(
        self,
        restaurant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[SalesData]:
        query = """
        SELECT * FROM sales_data
        WHERE restaurant_id = ? AND sale_date BETWEEN ? AND ?
        """
        results = await self.db.execute(
            query,
            (restaurant_id, start_date, end_date)
        )
        return [SalesData(**result) for result in results]

    async def create_customer_feedback(
        self,
        feedback: CustomerFeedback
    ) -> CustomerFeedback:
        query = """
        INSERT INTO customer_feedback (
            id, restaurant_id, rating, review_text,
            sentiment_score, topics, keywords,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(
            query,
            (
                str(feedback.id), str(feedback.restaurant_id),
                feedback.rating, feedback.review_text,
                feedback.sentiment_score, str(feedback.topics),
                str(feedback.keywords), feedback.created_at,
                feedback.updated_at
            )
        )
        return feedback

    async def get_customer_feedback(
        self,
        restaurant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[CustomerFeedback]:
        query = """
        SELECT * FROM customer_feedback
        WHERE restaurant_id = ? AND created_at BETWEEN ? AND ?
        """
        results = await self.db.execute(
            query,
            (restaurant_id, start_date, end_date)
        )
        return [CustomerFeedback(**result) for result in results]

    async def record_waste(self, waste: WasteRecord) -> WasteRecord:
        query = """
        INSERT INTO waste_records (
            id, restaurant_id, ingredient_name,
            quantity, unit, reason, waste_date, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        await self.db.execute(
            query,
            (
                str(waste.id), str(waste.restaurant_id),
                waste.ingredient_name, waste.quantity,
                waste.unit, waste.reason, waste.waste_date,
                waste.created_at
            )
        )
        return waste

    async def get_waste_records(
        self,
        restaurant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[WasteRecord]:
        query = """
        SELECT * FROM waste_records
        WHERE restaurant_id = ? AND waste_date BETWEEN ? AND ?
        """
        results = await self.db.execute(
            query,
            (restaurant_id, start_date, end_date)
        )
        return [WasteRecord(**result) for result in results] 