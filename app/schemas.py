import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class Problem(ApiModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None


class OrderItem(ApiModel):
    menu_item_id: uuid.UUID = Field(alias="menuItemId")
    name: str
    quantity: int
    unit_price_cents: int = Field(alias="unitPriceCents")


class OrderSummary(ApiModel):
    id: uuid.UUID
    restaurant_id: uuid.UUID = Field(alias="restaurantId")
    user_id: uuid.UUID = Field(alias="userId")
    status: str
    total_amount_cents: int = Field(alias="totalAmountCents")
    currency: str
    created_at: datetime = Field(alias="createdAt")


class Order(OrderSummary):
    items: list[OrderItem]
    updated_at: datetime = Field(alias="updatedAt")


class OrderListResponse(ApiModel):
    data: list[OrderSummary]
    next_cursor: str | None = Field(alias="nextCursor")


class CreateOrderItem(ApiModel):
    menu_item_id: uuid.UUID = Field(alias="menuItemId")
    quantity: int = Field(ge=1)


class CreateOrderRequest(ApiModel):
    user_id: uuid.UUID = Field(alias="userId")
    items: list[CreateOrderItem] = Field(min_length=1)


class CreatePaymentRequest(ApiModel):
    method: str = Field(pattern="^card$")
    card_token: str = Field(alias="cardToken", min_length=1)


class Payment(ApiModel):
    id: uuid.UUID
    order_id: uuid.UUID = Field(alias="orderId")
    amount_cents: int = Field(alias="amountCents")
    currency: str
    method: str
    status: str
    paid_at: datetime = Field(alias="paidAt")


class UserProfile(ApiModel):
    id: uuid.UUID
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    created_at: datetime = Field(alias="createdAt")
