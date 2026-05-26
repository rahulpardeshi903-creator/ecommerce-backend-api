from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.order import OrderStatus

class OrderCreate(BaseModel):
    shipping_address: str

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float
    model_config = {"from_attributes": True}

class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    total_amount: float
    shipping_address: str
    items: List[OrderItemResponse]
    created_at: datetime
    model_config = {"from_attributes": True}
