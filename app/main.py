from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .models import Product
from .schemas import ProductResponse


DEFAULT_PRODUCTS = [
    Product(
        name="Wireless Mouse",
        description="A wireless optical mouse for desktop and laptop computers.",
        price=24.99,
        categories="electronics,computer-accessories",
    ),
    Product(
        name="Mechanical Keyboard",
        description="A mechanical keyboard with RGB backlighting and tactile switches.",
        price=79.99,
        categories="electronics,computer-accessories",
    ),
    Product(
        name="USB-C Charging Cable",
        description="A durable USB-C cable for charging phones, tablets, and laptops.",
        price=12.99,
        categories="electronics,accessories",
    ),
    Product(
        name="Laptop Stand",
        description="An adjustable aluminum stand for laptops and notebooks.",
        price=39.99,
        categories="office,computer-accessories",
    ),
    Product(
        name="Water Bottle",
        description="A reusable stainless steel water bottle.",
        price=19.99,
        categories="home,outdoors",
    ),
]


def initialize_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        existing_product = db.execute(select(Product)).first()

        if existing_product is None:
            db.add_all(DEFAULT_PRODUCTS)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Catalog Service",
    description="CSC4201 ecommerce catalog microservice",
    version="1.0.0",
    lifespan=lifespan,
)


def product_to_response(product: Product) -> ProductResponse:
    return ProductResponse(
        product_id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        categories=[
            category.strip()
            for category in product.categories.split(",")
            if category.strip()
        ],
    )


@app.get("/products", response_model=list[ProductResponse])
def get_products(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    statement = select(Product)

    if search:
        search_pattern = f"%{search}%"

        statement = statement.where(
            (Product.name.ilike(search_pattern))
            | (Product.description.ilike(search_pattern))
        )

    products = db.scalars(statement).all()

    return [product_to_response(product) for product in products]


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product_to_response(product)