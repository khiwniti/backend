import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from app.database.connection import DatabaseConnection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("db_init")

async def init_database():
    """Initialize the database and create sample data"""
    logger.info("Initializing database...")
    
    # Create database connection
    db = DatabaseConnection()
    await db.connect()
    
    try:
        # Create tables
        logger.info("Creating database tables...")
        await db.create_tables()
        
        # Create sample restaurant
        restaurant_id = str(uuid.uuid4())
        logger.info(f"Creating sample restaurant with ID: {restaurant_id}")
        
        current_time = datetime.utcnow()
        
        # Insert sample restaurant
        await db.execute(
            """
            INSERT INTO restaurants (id, name, address, phone, email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                restaurant_id,
                "BiteBase Demo Restaurant",
                "123 Main Street, Anytown, USA",
                "+1-555-123-4567",
                "demo@bitebase.app",
                current_time,
                current_time
            )
        )
        
        # Insert sample inventory items
        logger.info("Creating sample inventory items...")
        inventory_items = [
            (str(uuid.uuid4()), restaurant_id, "Flour", 50.0, "kg", 10.0, 100.0, current_time, current_time, current_time),
            (str(uuid.uuid4()), restaurant_id, "Sugar", 25.0, "kg", 5.0, 50.0, current_time, current_time, current_time),
            (str(uuid.uuid4()), restaurant_id, "Eggs", 100.0, "units", 20.0, 200.0, current_time, current_time, current_time),
            (str(uuid.uuid4()), restaurant_id, "Milk", 30.0, "liters", 5.0, 50.0, current_time, current_time, current_time),
            (str(uuid.uuid4()), restaurant_id, "Chicken", 20.0, "kg", 5.0, 40.0, current_time, current_time, current_time),
        ]
        
        for item in inventory_items:
            await db.execute(
                """
                INSERT INTO inventory (id, restaurant_id, ingredient_name, quantity, unit, min_quantity, max_quantity, last_restocked, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO NOTHING
                """,
                item
            )
        
        # Insert sample suppliers
        logger.info("Creating sample suppliers...")
        supplier_ids = []
        suppliers = [
            (str(uuid.uuid4()), "Farm Fresh Foods", "John Smith", "+1-555-987-6543", "john@farmfresh.com", "456 Farm Road, Ruralville, USA", 10.0, "Monday,Thursday", current_time, current_time),
            (str(uuid.uuid4()), "City Distributors", "Jane Doe", "+1-555-789-0123", "jane@citydist.com", "789 Market St, Metropolis, USA", 5.0, "Tuesday,Friday", current_time, current_time),
            (str(uuid.uuid4()), "Quality Meats", "Bob Johnson", "+1-555-456-7890", "bob@qualitymeats.com", "321 Butcher Lane, Meatville, USA", 15.0, "Wednesday,Saturday", current_time, current_time),
        ]
        
        for supplier in suppliers:
            supplier_id = supplier[0]
            supplier_ids.append(supplier_id)
            await db.execute(
                """
                INSERT INTO suppliers (id, name, contact_person, phone, email, address, min_order_quantity, delivery_days, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO NOTHING
                """,
                supplier
            )
        
        # Insert sample menu items
        logger.info("Creating sample menu items...")
        menu_item_ids = []
        menu_items = [
            (str(uuid.uuid4()), restaurant_id, "Classic Burger", "Juicy beef patty with lettuce, tomato, and cheese", 9.99, "Beef,Lettuce,Tomato,Cheese,Bun", True, current_time, current_time),
            (str(uuid.uuid4()), restaurant_id, "Margherita Pizza", "Traditional pizza with tomato sauce, mozzarella, and basil", 12.99, "Flour,Tomato,Mozzarella,Basil", True, current_time, current_time),
            (str(uuid.uuid4()), restaurant_id, "Chicken Caesar Salad", "Grilled chicken with romaine lettuce and Caesar dressing", 8.99, "Chicken,Lettuce,Croutons,Parmesan,Caesar Dressing", True, current_time, current_time),
            (str(uuid.uuid4()), restaurant_id, "Chocolate Cake", "Rich chocolate cake with ganache", 6.99, "Flour,Sugar,Eggs,Cocoa,Butter", True, current_time, current_time),
        ]
        
        for item in menu_items:
            menu_item_id = item[0]
            menu_item_ids.append(menu_item_id)
            await db.execute(
                """
                INSERT INTO menu_items (id, restaurant_id, name, description, price, ingredients, is_available, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO NOTHING
                """,
                item
            )
        
        # Insert sample sales data
        logger.info("Creating sample sales data...")
        sales_data = []
        for i in range(30):
            for menu_item_id in menu_item_ids:
                quantity = 1 + (i % 5)
                price = 9.99 if "Burger" in menu_item_id else (12.99 if "Pizza" in menu_item_id else (8.99 if "Salad" in menu_item_id else 6.99))
                total_price = quantity * price
                sale_date = current_time - timedelta(days=i)
                sales_data.append((str(uuid.uuid4()), restaurant_id, menu_item_id, quantity, total_price, sale_date, sale_date))
        
        for sale in sales_data:
            await db.execute(
                """
                INSERT INTO sales_data (id, restaurant_id, menu_item_id, quantity, total_price, sale_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO NOTHING
                """,
                sale
            )
        
        # Insert sample customer feedback
        logger.info("Creating sample customer feedback...")
        review_texts = [
            "Great food and service!",
            "The burger was delicious, but the fries were a bit cold.",
            "Excellent pizza, will definitely come back!",
            "Service was slow, but the food made up for it.",
            "Best restaurant in town, highly recommend the chocolate cake!",
            "Average experience, nothing special.",
            "The salad was fresh and tasty, perfect for lunch.",
            "Disappointed with the portion size for the price.",
            "Friendly staff and cozy atmosphere.",
            "Food was good but a bit overpriced.",
        ]
        
        for i in range(20):
            rating = 3 + (i % 3)  # Ratings from 3 to 5
            review_index = i % len(review_texts)
            sentiment_score = 0.7 if rating >= 4 else (0.0 if rating == 3 else -0.7)
            created_at = current_time - timedelta(days=i)
            
            await db.execute(
                """
                INSERT INTO customer_feedback (id, restaurant_id, rating, review_text, sentiment_score, topics, keywords, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(uuid.uuid4()),
                    restaurant_id,
                    rating,
                    review_texts[review_index],
                    sentiment_score,
                    "food,service",
                    "burger,pizza,service,taste",
                    created_at,
                    created_at
                )
            )
        
        # Insert sample waste records
        logger.info("Creating sample waste records...")
        waste_reasons = ["Expired", "Spoiled", "Overcooked", "Returned by customer", "Prep waste"]
        waste_items = ["Flour", "Sugar", "Eggs", "Milk", "Chicken"]
        
        for i in range(15):
            waste_date = current_time - timedelta(days=i)
            for j in range(1 + (i % 3)):
                item_index = (i + j) % len(waste_items)
                reason_index = (i + j) % len(waste_reasons)
                
                await db.execute(
                    """
                    INSERT INTO waste_records (id, restaurant_id, ingredient_name, quantity, unit, reason, waste_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(uuid.uuid4()),
                        restaurant_id,
                        waste_items[item_index],
                        0.5 + (j * 0.5),
                        "kg" if waste_items[item_index] in ["Flour", "Sugar", "Chicken"] else ("units" if waste_items[item_index] == "Eggs" else "liters"),
                        waste_reasons[reason_index],
                        waste_date,
                        waste_date
                    )
                )
        
        await db.commit()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(init_database()) 