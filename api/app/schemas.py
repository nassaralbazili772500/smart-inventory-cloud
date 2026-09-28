from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )

    category: str = Field(
        min_length=2,
        max_length=100
    )

    quantity: int = Field(
        ge=0
    )

    price: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    minimum_stock: int = Field(
        default=5,
        ge=0
    )


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    category: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    quantity: int | None = Field(
        default=None,
        ge=0
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    minimum_stock: int | None = Field(
        default=None,
        ge=0
    )


class StockUpdate(BaseModel):
    quantity: int = Field(
        ge=0
    )


class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )