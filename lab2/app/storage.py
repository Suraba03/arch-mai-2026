from itertools import count
from threading import Lock
from typing import Dict, List, Optional

from app.models import Delivery, Parcel, User


class UserRepository:
    def __init__(self) -> None:
        self._items: Dict[int, User] = {}
        self._by_login: Dict[str, int] = {}
        self._ids = count(1)
        self._lock = Lock()

    def create(self, login: str, password_hash: str, first_name: str, last_name: str) -> User:
        with self._lock:
            if login in self._by_login:
                raise ValueError("login already exists")
            user = User(
                id=next(self._ids),
                login=login,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
            )
            self._items[user.id] = user
            self._by_login[login] = user.id
            return user

    def get(self, user_id: int) -> Optional[User]:
        return self._items.get(user_id)

    def get_by_login(self, login: str) -> Optional[User]:
        uid = self._by_login.get(login)
        return self._items.get(uid) if uid is not None else None

    def search_by_name(self, name: Optional[str], surname: Optional[str]) -> List[User]:
        name_l = (name or "").lower()
        surname_l = (surname or "").lower()
        result: List[User] = []
        for u in self._items.values():
            if name_l and name_l not in u.first_name.lower():
                continue
            if surname_l and surname_l not in u.last_name.lower():
                continue
            result.append(u)
        return result
    
    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._by_login.clear()
            self._ids = count(1)


class ParcelRepository:
    def __init__(self) -> None:
        self._items: Dict[int, Parcel] = {}
        self._ids = count(1)
        self._lock = Lock()

    def create(self, owner_id: int, description: str, weight_kg: float) -> Parcel:
        with self._lock:
            parcel = Parcel(
                id=next(self._ids),
                owner_id=owner_id,
                description=description,
                weight_kg=weight_kg,
            )
            self._items[parcel.id] = parcel
            return parcel

    def get(self, parcel_id: int) -> Optional[Parcel]:
        return self._items.get(parcel_id)

    def list_by_owner(self, owner_id: int) -> List[Parcel]:
        return [p for p in self._items.values() if p.owner_id == owner_id]

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._ids = count(1)

class DeliveryRepository:
    def __init__(self) -> None:
        self._items: Dict[int, Delivery] = {}
        self._ids = count(1)
        self._lock = Lock()

    def create(self, parcel_id: int, sender_id: int, recipient_id: int) -> Delivery:
        with self._lock:
            delivery = Delivery(
                id=next(self._ids),
                parcel_id=parcel_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
            )
            self._items[delivery.id] = delivery
            return delivery

    def get(self, delivery_id: int) -> Optional[Delivery]:
        return self._items.get(delivery_id)

    def list_by_sender(self, sender_id: int) -> List[Delivery]:
        return [d for d in self._items.values() if d.sender_id == sender_id]

    def list_by_recipient(self, recipient_id: int) -> List[Delivery]:
        return [d for d in self._items.values() if d.recipient_id == recipient_id]

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._ids = count(1)


# ---------- Singleton-репозитории для приложения ----------

users_repo = UserRepository()
parcels_repo = ParcelRepository()
deliveries_repo = DeliveryRepository()


def reset_storage() -> None:
    """Очистка состояния (для тестов)."""
    users_repo.clear()
    parcels_repo.clear()
    deliveries_repo.clear()