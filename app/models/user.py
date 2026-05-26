from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    SELLER = "seller"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart = relationship("Cart", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"
