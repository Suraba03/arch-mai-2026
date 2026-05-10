from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import ErrorResponse, UserResponse
from app.storage import users_repo


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/by-login/{login}",
    response_model=UserResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
    },
    summary="Поиск пользователя по логину",
)
def get_user_by_login(login: str) -> UserResponse:
    user = users_repo.get_by_login(login)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)


@router.get(
    "/search",
    response_model=List[UserResponse],
    summary="Поиск пользователей по маске имени и/или фамилии",
)
def search_users(
    name: Optional[str] = Query(
        default=None,
        description="Подстрока в имени (case-insensitive)",
        examples=["Iv"],
    ),
    surname: Optional[str] = Query(
        default=None,
        description="Подстрока в фамилии (case-insensitive)",
        examples=["Pet"],
    ),
) -> List[UserResponse]:
    if not name and not surname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of 'name' or 'surname' must be provided",
        )
    found = users_repo.search_by_name(name=name, surname=surname)
    return [UserResponse.model_validate(u) for u in found]