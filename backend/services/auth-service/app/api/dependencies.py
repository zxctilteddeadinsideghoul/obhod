from fastapi import Request

from app.containers import Container
from app.use_cases import GetCurrentUserUseCase, VerifyAccessUseCase


def get_container(request: Request) -> Container:
    return request.app.container  # type: ignore[attr-defined]


def get_verify_access_use_case(request: Request) -> VerifyAccessUseCase:
    return get_container(request).verify_access_use_case()


def get_current_user_use_case(request: Request) -> GetCurrentUserUseCase:
    return get_container(request).get_current_user_use_case()
