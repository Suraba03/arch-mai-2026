from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.models import User
from app.schemas import DeliveryCreateRequest, DeliveryResponse, ErrorResponse
from app.storage import deliveries_repo, parcels_repo, users_repo


router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.post(
    "",
    response_model=DeliveryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Parcel does not belong to sender"},
        404: {"model": ErrorResponse, "description": "Parcel or recipient not found"},
    },
    summary="Создание доставки от текущего пользователя к получателю (требуется JWT)",
)
def create_delivery(
    payload: DeliveryCreateRequest,
    current_user: User = Depends(get_current_user),
) -> DeliveryResponse:
    # 1. Получатель должен существовать
    recipient = users_repo.get(payload.recipient_id)
    if recipient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found",
        )

    # 2. Нельзя отправить самому себе
    if recipient.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sender and recipient must differ",
        )

    # 3. Посылка должна существовать
    parcel = parcels_repo.get(payload.parcel_id)
    if parcel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel not found",
        )

    # 4. Посылка должна принадлежать отправителю
    if parcel.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parcel does not belong to sender",
        )

    delivery = deliveries_repo.create(
        parcel_id=parcel.id,
        sender_id=current_user.id,
        recipient_id=recipient.id,
    )
    return DeliveryResponse.model_validate(delivery)


@router.get(
    "/by-sender/{user_id}",
    response_model=List[DeliveryResponse],
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
    },
    summary="Получение доставок, где пользователь — отправитель",
)
def get_deliveries_by_sender(user_id: int) -> List[DeliveryResponse]:
    if users_repo.get(user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    items = deliveries_repo.list_by_sender(user_id)
    return [DeliveryResponse.model_validate(d) for d in items]


@router.get(
    "/by-recipient/{user_id}",
    response_model=List[DeliveryResponse],
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
    },
    summary="Получение доставок, где пользователь — получатель",
)
def get_deliveries_by_recipient(user_id: int) -> List[DeliveryResponse]:
    if users_repo.get(user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    items = deliveries_repo.list_by_recipient(user_id)
    return [DeliveryResponse.model_validate(d) for d in items]