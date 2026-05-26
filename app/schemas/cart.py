from pydantic import BaseModel
from typing import List
from app.schemas.product import ProductResponse

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    subtotal: float
    model_config = {"from_attributes": True}

class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse]
    total: float
    model_config = {"from_attributes": True}
