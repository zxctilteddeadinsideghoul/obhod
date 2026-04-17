from pydantic import BaseModel


class HealthRead(BaseModel):
    service: str
    status: str


class CurrentUserRead(BaseModel):
    service: str
    user_id: str | None = None
    user_role: str | None = None
    user_name: str | None = None
