from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.api.deps import get_current_active_user, require_admin
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, CategoryCreate, CategoryResponse
from app.models.product import Product, Category
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])

# ── Category Endpoints ──────────────────────────────────────────────────────

@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

# ── Product Endpoints ───────────────────────────────────────────────────────

@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """[Admin] Create a new product."""
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/", response_model=List[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
):
    """List products with optional filters."""
    query = db.query(Product).filter(Product.is_active == True)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID."""
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, data: ProductUpdate,
    db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    """[Admin] Update a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """[Admin] Soft delete a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
    return {"message": "Product deleted"}
