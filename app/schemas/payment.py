from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentStatus

class PaymentInitiate(BaseModel):
    order_id: int

class PaymentResponse(BaseModel):
    id: int
    amount: float
    status: PaymentStatus
    merchant_transaction_id: str
    payment_url: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
