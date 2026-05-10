from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class User:
    id: int
    login: str
    password_hash: str
    first_name: str
    last_name: str


@dataclass
class Parcel:
    id: int
    owner_id: int
    description: str
    weight_kg: float
    created_at: datetime = field(default_factory=_utcnow)


class DeliveryStatus(str, Enum):
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Delivery:
    id: int
    parcel_id: int
    sender_id: int
    recipient_id: int
    status: DeliveryStatus = DeliveryStatus.CREATED
    created_at: datetime = field(default_factory=_utcnow)