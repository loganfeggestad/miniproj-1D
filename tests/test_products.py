import os
import tempfile

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Product


fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

test_engine = create_engine(
    f"sqlite:///{path}",
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=test_engine)


def seed_database():
    db = TestingSessionLocal()

    try:
        db.query(Product).delete()

        db.add_all(
            [
                Product(
                    name="Wireless Mouse",
                    description="A wireless optical mouse.",
                    price=24.99,
                    categories="electronics,computer-accessories",
                ),
                Product(
                    name="Mechanical Keyboard",
                    description="A mechanical keyboard with tactile switches.",
                    price=79.99,
                    categories="electronics,computer-accessories",
                ),
                Product(
                    name="Laptop Stand",
                    description="An adjustable aluminum stand.",
                    price=39.99,
                    categories="office",
                ),
            ]
        )

        db.commit()
    finally:
        db.close()


client = TestClient(app)


def setup_function():
    seed_database()


def test_get_all_products():
    response = client.get("/products")

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 3


def test_search_by_name():
    response = client.get("/products?search=Mouse")

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 1
    assert products[0]["name"] == "Wireless Mouse"


def test_search_by_description():
    response = client.get("/products?search=tactile")

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 1
    assert products[0]["name"] == "Mechanical Keyboard"


def test_search_is_case_insensitive():
    response = client.get("/products?search=mouse")

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 1
    assert products[0]["name"] == "Wireless Mouse"


def test_search_with_no_results():
    response = client.get("/products?search=does-not-exist")

    assert response.status_code == 200
    assert response.json() == []


def test_get_product():
    response = client.get("/products/1")

    assert response.status_code == 200

    product = response.json()

    assert product["product_id"] == 1
    assert product["name"] == "Wireless Mouse"
    assert product["price"] == 24.99


def test_get_nonexistent_product():
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def teardown_module():
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    os.unlink(path)