from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartResponse
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User

router = APIRouter(prefix="/cart", tags=["Cart"])

def get_or_create_cart(user: User, db: Session) -> Cart:
    """Get user's cart or create one if it doesn't exist."""
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

@router.get("/", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get current user's cart."""
    return get_or_create_cart(current_user, db)

@router.post("/items", response_model=CartResponse)
def add_item(
    item: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a product to the cart."""
    product = db.query(Product).filter(Product.id == item.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail=f"Only {product.stock} items in stock")

    cart = get_or_create_cart(current_user, db)

    # If item already in cart, update quantity
    existing = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item.product_id
    ).first()

    if existing:
        existing.quantity += item.quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=item.product_id, quantity=item.quantity)
        db.add(cart_item)

    db.commit()
    db.refresh(cart)
    return cart

@router.put("/items/{item_id}", response_model=CartResponse)
def update_item(
    item_id: int,
    update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update quantity of a cart item."""
    cart = get_or_create_cart(current_user, db)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    if update.quantity <= 0:
        db.delete(item)
    else:
        if item.product.stock < update.quantity:
            raise HTTPException(status_code=400, detail=f"Only {item.product.stock} items in stock")
        item.quantity = update.quantity

    db.commit()
    db.refresh(cart)
    return cart

@router.delete("/items/{item_id}")
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove an item from the cart."""
    cart = get_or_create_cart(current_user, db)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}

@router.delete("/")
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Clear all items from the cart."""
    cart = get_or_create_cart(current_user, db)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"message": "Cart cleared"}
