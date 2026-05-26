from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class PaymentStatus(str, enum.Enum):
    INITIATED = "initiated"
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    amount_paisa = Column(Integer, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.INITIATED)
    merchant_transaction_id = Column(String, unique=True, index=True)
    phonepe_transaction_id = Column(String, nullable=True)
    payment_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="payment", foreign_keys="Order.payment_id", uselist=False)
