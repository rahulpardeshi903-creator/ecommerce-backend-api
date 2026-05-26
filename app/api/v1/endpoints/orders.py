from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_active_user, require_admin
from app.schemas.order import OrderCreate, OrderResponse
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import Cart, CartItem
from app.models.user import User
from app.services.email_service import send_order_confirmation_email

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=201)
def place_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Place an order from the current cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Your cart is empty")

    # Validate stock for all items before placing order
    for item in cart.items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"'{item.product.name}' has only {item.product.stock} items in stock"
            )

    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart.items)

    # Create order
    order = Order(
        user_id=current_user.id,
        total_amount=total,
        shipping_address=order_data.shipping_address,
        status=OrderStatus.PENDING
    )
    db.add(order)
    db.flush()  # Get order.id without committing

    # Create order items and deduct stock
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.price,
        )
        db.add(order_item)
        cart_item.product.stock -= cart_item.quantity  # Deduct stock

    # Clear cart after order
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

    db.commit()
    db.refresh(order)

    # Send order confirmation email
    try:
        send_order_confirmation_email(current_user.email, current_user.full_name, order.id, total)
    except Exception:
        pass

    return order

@router.get("/", response_model=List[OrderResponse])
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's order history."""
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific order (must belong to current user)."""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a pending order and restore stock."""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel an order with status '{order.status.value}'")

    # Restore product stock
    for item in order.items:
        item.product.stock += item.quantity

    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order

# Admin routes
@router.get("/admin/all", response_model=List[OrderResponse])
def all_orders(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 50
):
    """[Admin] List all orders."""
    return db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

@router.put("/admin/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """[Admin] Update order status."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    db.refresh(order)
    return order
