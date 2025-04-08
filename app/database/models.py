from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .config import Base
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    restaurants = relationship("Restaurant", back_populates="owner")

class Restaurant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    address: str
    phone: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Inventory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    restaurant_id: UUID
    ingredient_name: str
    quantity: float
    unit: str
    min_quantity: float
    max_quantity: float
    last_restocked: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Supplier(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    contact_person: str
    phone: str
    email: str
    address: str
    min_order_quantity: float
    delivery_days: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MenuItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    restaurant_id: UUID
    name: str
    description: str
    price: float
    ingredients: List[dict]
    is_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SalesData(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    restaurant_id: UUID
    menu_item_id: UUID
    quantity: int
    total_price: float
    sale_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CustomerFeedback(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    restaurant_id: UUID
    rating: int
    review_text: str
    sentiment_score: Optional[float] = None
    topics: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WasteRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    restaurant_id: UUID
    ingredient_name: str
    quantity: float
    unit: str
    reason: str
    waste_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AnalyticsData(Base):
    __tablename__ = "analytics"

    id = Column(String, primary_key=True, index=True)
    restaurant_id = Column(String, ForeignKey("restaurants.id"))
    metric_type = Column(String)
    value = Column(Float)
    timestamp = Column(DateTime)
    metadata = Column(JSON, nullable=True)

    restaurant = relationship("Restaurant", back_populates="analytics")

class MenuItemSales(Base):
    __tablename__ = "menu_item_sales"

    id = Column(String, primary_key=True, index=True)
    menu_item_id = Column(String, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    revenue = Column(Float)
    timestamp = Column(DateTime)
    metadata = Column(JSON, nullable=True)

    menu_item = relationship("MenuItem", back_populates="sales_data")

class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    cuisine_type = Column(String)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 