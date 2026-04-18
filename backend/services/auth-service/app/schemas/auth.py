from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class PrincipalRead(BaseModel):
    id: str
    role: str
    name: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: PrincipalRead


class WorkerCreate(BaseModel):
    username: str
    password: str
    full_name: str
    employee_id: str | None = None
    qualification_id: str | None = "OPERATOR-TU"
    department_id: str | None = "DEPT-UGP"


class WorkerRead(BaseModel):
    id: str
    username: str
    role: str
    full_name: str
    active_flag: bool
    qualification_id: str | None = None
    department_id: str | None = None


class AuthVerificationRead(BaseModel):
    status: str
    method: str
    uri: str
    principal: PrincipalRead
