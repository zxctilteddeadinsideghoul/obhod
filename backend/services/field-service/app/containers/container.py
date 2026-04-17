from dependency_injector import containers, providers

from app.db import SessionLocal
from app.repositories import FieldRepository
from app.services import FieldService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app.api.routes"])

    session_factory = providers.Object(SessionLocal)

    field_repository = providers.Factory(FieldRepository, session_factory=session_factory)
    field_service = providers.Factory(FieldService, repository=field_repository)
