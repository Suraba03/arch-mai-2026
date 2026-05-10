from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import DeliveryStatus


# ===================== AUTH =====================

class RegisterRequest(BaseModel):
    login: str = Field(..., min_length=3, max_length=32, examples=["ivan"])
    password: str = Field(..., min_length=6, max_length=128, examples=["secret123"])
    first_name: str = Field(..., min_length=1, max_length=64, examples=["Ivan"])
    last_name: str = Field(..., min_length=1, max_length=64, examples=["Petrov"])


class LoginRequest(BaseModel):
    login: str = Field(..., examples=["ivan"])
    password: str = Field(..., examples=["secret123"])


class TokenResponse(BaseModel):
    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5..."])
    token_type: str = Field(default="bearer", examples=["bearer"])


# ===================== USER =====================

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    login: str = Field(..., examples=["ivan"])
    first_name: str = Field(..., examples=["Ivan"])
    last_name: str = Field(..., examples=["Petrov"])


# ===================== PARCEL =====================

class ParcelCreateRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=255, examples=["Книга"])
    weight_kg: float = Field(..., gt=0, le=1000, examples=[1.5])


class ParcelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    owner_id: int = Field(..., examples=[1])
    description: str = Field(..., examples=["Книга"])
    weight_kg: float = Field(..., examples=[1.5])
    created_at: datetime


# ===================== DELIVERY =====================

class DeliveryCreateRequest(BaseModel):
    parcel_id: int = Field(..., gt=0, examples=[1])
    recipient_id: int = Field(..., gt=0, examples=[2])


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    parcel_id: int = Field(..., examples=[1])
    sender_id: int = Field(..., examples=[1])
    recipient_id: int = Field(..., examples=[2])
    status: DeliveryStatus = Field(..., examples=[DeliveryStatus.CREATED])
    created_at: datetime


# ===================== ERROR =====================

class ErrorResponse(BaseModel):
    detail: str = Field(..., examples=["Resource not found"])