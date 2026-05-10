from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from app.auth import create_access_token, hash_password, verify_password
from app.schemas import (
    ErrorResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.storage import users_repo


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse, "description": "Login already exists"},
    },
    summary="Регистрация нового пользователя",
)
def register(payload: RegisterRequest) -> UserResponse:
    if users_repo.get_by_login(payload.login) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login already exists",
        )

    user = users_repo.create(
        login=payload.login,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
    summary="Логин (OAuth2 password flow), возвращает JWT",
)
def login(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    """
    Принимает form-data: `username`, `password`.
    `username` трактуется как `login`.
    Это даёт возможность использовать кнопку **Authorize** в Swagger UI.
    """
    user = users_repo.get_by_login(form.username)
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user.login)
    return TokenResponse(access_token=token)


@router.post(
    "/login-json",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
    summary="Логин по JSON (альтернатива form-data)",
)
def login_json(payload: LoginRequest) -> TokenResponse:
    user = users_repo.get_by_login(payload.login)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user.login)
    return TokenResponse(access_token=token)