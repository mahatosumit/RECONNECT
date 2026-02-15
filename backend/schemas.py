from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

GST_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$")
PHONE_PATTERN = re.compile(r"^(?:\+91|91)?[6-9]\d{9}$")


class InvoiceRequest(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=120)
    business_address: str = Field(..., min_length=5, max_length=300)
    business_gst_number: str = Field(..., min_length=15, max_length=15)
    customer_name: str = Field(..., min_length=2, max_length=120)
    customer_phone: str = Field(..., min_length=10, max_length=14)
    invoice_number: str = Field(..., min_length=3, max_length=30)
    invoice_date: date
    item_name: str = Field(..., min_length=2, max_length=120)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    gst_rate: Literal[5, 12, 18, 28]

    @field_validator("business_gst_number")
    @classmethod
    def validate_gst(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not GST_PATTERN.match(normalized):
            raise ValueError("Enter a valid 15-character GST number.")
        return normalized

    @field_validator("customer_phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip().replace(" ", "")
        if not PHONE_PATTERN.match(normalized):
            raise ValueError("Enter a valid Indian mobile number.")
        return normalized[-10:]

    @field_validator("business_name", "business_address", "customer_name", "invoice_number", "item_name")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class InvoiceTotals(BaseModel):
    subtotal: Decimal
    gst_amount: Decimal
    total: Decimal


def calculate_totals(quantity: Decimal, unit_price: Decimal, gst_rate: int) -> InvoiceTotals:
    subtotal = (quantity * unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    gst_amount = (subtotal * Decimal(gst_rate) / Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (subtotal + gst_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return InvoiceTotals(subtotal=subtotal, gst_amount=gst_amount, total=total)
