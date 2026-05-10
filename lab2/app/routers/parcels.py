from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.models import User
from app.schemas import ErrorResponse, ParcelCreateRequest, ParcelResponse
from app.storage import parcels_repo, users_repo


router = APIRouter(tags=["parcels"])


@router.post(
    "/parcels",
    response_model=ParcelResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    summary="Создание посылки от текущего пользователя (требуется JWT)",
)
def create_parcel(
    payload: ParcelCreateRequest,
    current_user: User = Depends(get_current_user),
) -> ParcelResponse:
    parcel = parcels_repo.create(
        owner_id=current_user.id,
        description=payload.description,
        weight_kg=payload.weight_kg,
    )
    return ParcelResponse.model_validate(parcel)


@router.get(
    "/users/{user_id}/parcels",
    response_model=List[ParcelResponse],
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
    },
    summary="Получение посылок пользователя",
)
def get_user_parcels(user_id: int) -> List[ParcelResponse]:
    if users_repo.get(user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    parcels = parcels_repo.list_by_owner(user_id)
    return [ParcelResponse.model_validate(p) for p in parcels]