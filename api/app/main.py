from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Product
from app.schemas import ProductCreate, ProductResponse


# --------------------------------------------------
# Application startup
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables automatically if they do not exist
    Base.metadata.create_all(bind=engine)
    yield


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Smart Inventory Cloud API",
    description="Cloud-based inventory management REST API",
    version="1.0.0",
    lifespan=lifespan
)


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Smart Inventory Cloud API is running",
        "version": "1.0.0"
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health_check(
    db: Session = Depends(get_db)
):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        )


# --------------------------------------------------
# CREATE PRODUCT
# --------------------------------------------------

@app.post(
    "/api/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    product = Product(
        name=product_data.name,
        category=product_data.category,
        quantity=product_data.quantity,
        price=product_data.price,
        minimum_stock=product_data.minimum_stock
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# --------------------------------------------------
# GET ALL PRODUCTS
# --------------------------------------------------

@app.get(
    "/api/products",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK
)
def get_products(
    db: Session = Depends(get_db)
):
    products = db.scalars(
        select(Product).order_by(Product.id)
    ).all()

    return products


# --------------------------------------------------
# LOW STOCK ALERT
# --------------------------------------------------

@app.get(
    "/api/products/alerts/low-stock",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK
)
def get_low_stock_products(
    db: Session = Depends(get_db)
):
    products = db.scalars(
        select(Product)
        .where(Product.quantity <= Product.minimum_stock)
        .order_by(Product.quantity)
    ).all()

    return products


# --------------------------------------------------
# SEARCH PRODUCTS
# --------------------------------------------------

@app.get(
    "/api/products/filter/search",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK
)
def search_products(
    name: str,
    db: Session = Depends(get_db)
):
    products = db.scalars(
        select(Product)
        .where(Product.name.ilike(f"%{name}%"))
        .order_by(Product.id)
    ).all()

    return products


# --------------------------------------------------
# GET PRODUCT BY ID
# --------------------------------------------------

@app.get(
    "/api/products/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


# --------------------------------------------------
# UPDATE PRODUCT
# --------------------------------------------------

@app.put(
    "/api/products/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK
)
def update_product(
    product_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product.name = product_data.name
    product.category = product_data.category
    product.quantity = product_data.quantity
    product.price = product_data.price
    product.minimum_stock = product_data.minimum_stock

    db.commit()
    db.refresh(product)

    return product


# --------------------------------------------------
# DELETE PRODUCT
# --------------------------------------------------

@app.delete(
    "/api/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return None