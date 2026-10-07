from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    description: str
    price: float = Field(ge=0)
    categories: list[str]


class ProductResponse(ProductBase):
    product_id: int