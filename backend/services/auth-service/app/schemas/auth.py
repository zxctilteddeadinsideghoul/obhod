from pydantic import BaseModel


class PrincipalRead(BaseModel):
    id: str
    role: str
    name: str


class AuthVerificationRead(BaseModel):
    status: str
    method: str
    uri: str
    principal: PrincipalRead
