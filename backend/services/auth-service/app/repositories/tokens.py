import base64
import binascii
import hashlib
import hmac
import json
import re
import secrets
import time

import asyncpg

from app.core.config import Settings
from app.schemas import PrincipalRead, WorkerCreate, WorkerRead


class TokensRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def initialize_storage(self) -> None:
        conn = await self._connect()
        try:
            await conn.execute(
                """
                create table if not exists auth_user (
                    id varchar(64) primary key,
                    username varchar(128) not null unique,
                    password_hash text not null,
                    salt text not null,
                    role varchar(32) not null,
                    full_name varchar(255) not null,
                    active_flag boolean not null default true,
                    qualification_id varchar(64),
                    department_id varchar(64),
                    created_at timestamptz not null default now(),
                    updated_at timestamptz not null default now()
                )
                """
            )
            await conn.execute("create index if not exists ix_auth_user_role on auth_user(role)")
            await self._upsert_demo_user(
                conn,
                user_id="dev-admin",
                username=self.settings.admin_login,
                password=self.settings.admin_password,
                role="ADMIN",
                full_name="Development Admin",
                qualification_id=None,
                department_id=None,
            )
            await self._upsert_demo_user(
                conn,
                user_id="dev-worker",
                username=self.settings.worker_login,
                password=self.settings.worker_password,
                role="WORKER",
                full_name="Development Worker",
                qualification_id="OPERATOR-TU",
                department_id="DEPT-UGP",
            )
        finally:
            await conn.close()

    async def get_principal_by_authorization(self, authorization: str | None) -> PrincipalRead | None:
        if authorization == f"Bearer {self.settings.dev_admin_token}":
            return PrincipalRead(id="dev-admin", role="ADMIN", name="Development Admin")

        if authorization == f"Bearer {self.settings.dev_auth_token}":
            return PrincipalRead(id="dev-worker", role="WORKER", name="Development Worker")

        if authorization is None or not authorization.startswith("Bearer "):
            return None

        return self.get_principal_by_access_token(authorization.removeprefix("Bearer ").strip())

    async def get_principal_by_credentials(self, username: str, password: str) -> PrincipalRead | None:
        if self._credentials_match(username, password, self.settings.admin_login, self.settings.admin_password):
            return PrincipalRead(id="dev-admin", role="ADMIN", name="Development Admin")

        if self._credentials_match(username, password, self.settings.worker_login, self.settings.worker_password):
            return PrincipalRead(id="dev-worker", role="WORKER", name="Development Worker")

        user = await self._get_user_by_username(username)
        if user is None or not user["active_flag"]:
            return None
        if not self._verify_password(password, user["salt"], user["password_hash"]):
            return None
        return PrincipalRead(id=user["id"], role=user["role"], name=user["full_name"])

    async def create_worker(self, payload: WorkerCreate) -> WorkerRead:
        username = payload.username.strip()
        if not username:
            raise ValueError("Username is required")
        if not payload.password:
            raise ValueError("Password is required")
        if not payload.full_name.strip():
            raise ValueError("Full name is required")

        conn = await self._connect()
        try:
            existing = await conn.fetchrow(
                "select id from auth_user where lower(username) = lower($1)",
                username,
            )
            if existing is not None:
                raise FileExistsError("User with this username already exists")

            employee_id = payload.employee_id or self._make_employee_id(username)
            existing_id = await conn.fetchrow("select id from auth_user where id = $1", employee_id)
            if existing_id is not None:
                raise FileExistsError("User with this employee id already exists")

            salt = secrets.token_urlsafe(16)
            password_hash = self._hash_password(payload.password, salt)
            row = await conn.fetchrow(
                """
                insert into auth_user (
                    id,
                    username,
                    password_hash,
                    salt,
                    role,
                    full_name,
                    active_flag,
                    qualification_id,
                    department_id
                )
                values ($1, $2, $3, $4, 'WORKER', $5, true, $6, $7)
                returning id, username, role, full_name, active_flag, qualification_id, department_id
                """,
                employee_id,
                username,
                password_hash,
                salt,
                payload.full_name.strip(),
                payload.qualification_id,
                payload.department_id,
            )
            await self._upsert_field_employee(
                conn,
                employee_id=employee_id,
                full_name=payload.full_name.strip(),
                qualification_id=payload.qualification_id,
                department_id=payload.department_id,
            )
            return WorkerRead(**dict(row))
        finally:
            await conn.close()

    def issue_access_token(self, principal: PrincipalRead) -> str:
        now = int(time.time())
        payload = {
            "sub": principal.id,
            "role": principal.role,
            "name": principal.name,
            "iat": now,
            "exp": now + self.settings.access_token_ttl_sec,
        }
        payload_b64 = self._b64_json(payload)
        signature = self._sign(payload_b64)
        return f"obhod.{payload_b64}.{signature}"

    def get_principal_by_access_token(self, token: str) -> PrincipalRead | None:
        parts = token.split(".")
        if len(parts) != 3 or parts[0] != "obhod":
            return None

        _, payload_b64, signature = parts
        expected_signature = self._sign(payload_b64)
        if not hmac.compare_digest(signature, expected_signature):
            return None

        try:
            payload = self._json_from_b64(payload_b64)
        except (binascii.Error, ValueError, json.JSONDecodeError, UnicodeDecodeError):
            return None

        try:
            expires_at = int(payload.get("exp", 0))
        except (TypeError, ValueError):
            return None

        if expires_at < int(time.time()):
            return None

        user_id = payload.get("sub")
        role = payload.get("role")
        name = payload.get("name")
        if not isinstance(user_id, str) or not isinstance(role, str) or not isinstance(name, str):
            return None
        if role not in {"ADMIN", "WORKER"}:
            return None

        return PrincipalRead(id=user_id, role=role, name=name)

    def _credentials_match(
        self,
        username: str,
        password: str,
        expected_username: str,
        expected_password: str,
    ) -> bool:
        return hmac.compare_digest(username, expected_username) and hmac.compare_digest(password, expected_password)

    async def _connect(self) -> asyncpg.Connection:
        return await asyncpg.connect(self.settings.database_url)

    async def _get_user_by_username(self, username: str) -> asyncpg.Record | None:
        conn = await self._connect()
        try:
            return await conn.fetchrow(
                """
                select id, username, password_hash, salt, role, full_name, active_flag
                from auth_user
                where lower(username) = lower($1)
                """,
                username,
            )
        finally:
            await conn.close()

    async def _upsert_demo_user(
        self,
        conn: asyncpg.Connection,
        *,
        user_id: str,
        username: str,
        password: str,
        role: str,
        full_name: str,
        qualification_id: str | None,
        department_id: str | None,
    ) -> None:
        salt = f"demo-{user_id}"
        await conn.execute(
            """
            insert into auth_user (
                id,
                username,
                password_hash,
                salt,
                role,
                full_name,
                active_flag,
                qualification_id,
                department_id
            )
            values ($1, $2, $3, $4, $5, $6, true, $7, $8)
            on conflict (id) do update set
                username = excluded.username,
                password_hash = excluded.password_hash,
                salt = excluded.salt,
                role = excluded.role,
                full_name = excluded.full_name,
                active_flag = true,
                qualification_id = excluded.qualification_id,
                department_id = excluded.department_id,
                updated_at = now()
            """,
            user_id,
            username,
            self._hash_password(password, salt),
            salt,
            role,
            full_name,
            qualification_id,
            department_id,
        )
        if role == "WORKER":
            await self._upsert_field_employee(
                conn,
                employee_id=user_id,
                full_name=full_name,
                qualification_id=qualification_id,
                department_id=department_id,
            )

    async def _upsert_field_employee(
        self,
        conn: asyncpg.Connection,
        *,
        employee_id: str,
        full_name: str,
        qualification_id: str | None,
        department_id: str | None,
    ) -> None:
        try:
            await conn.execute(
                """
                insert into field_employee (id, person_id, full_name, qualification_id, department_id, active_flag)
                values ($1, $1, $2, $3, $4, true)
                on conflict (id) do update set
                    full_name = excluded.full_name,
                    qualification_id = excluded.qualification_id,
                    department_id = excluded.department_id,
                    active_flag = true,
                    updated_at = now()
                """,
                employee_id,
                full_name,
                qualification_id,
                department_id,
            )
        except asyncpg.UndefinedTableError:
            # Field migrations may not have been applied yet. Auth user remains valid;
            # the employee row will be created when the worker is created again.
            return

    def _make_employee_id(self, username: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", username.strip().lower()).strip("-")
        if not slug:
            slug = secrets.token_hex(4)
        return f"worker-{slug}"[:64]

    def _hash_password(self, password: str, salt: str) -> str:
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
        return self._b64_bytes(digest)

    def _verify_password(self, password: str, salt: str, expected_hash: str) -> bool:
        return hmac.compare_digest(self._hash_password(password, salt), expected_hash)

    def _sign(self, payload_b64: str) -> str:
        digest = hmac.new(
            self.settings.auth_secret.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return self._b64_bytes(digest)

    def _b64_json(self, value: dict) -> str:
        return self._b64_bytes(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))

    def _json_from_b64(self, value: str) -> dict:
        padding = "=" * (-len(value) % 4)
        decoded = base64.urlsafe_b64decode((value + padding).encode("ascii"))
        result = json.loads(decoded.decode("utf-8"))
        if not isinstance(result, dict):
            raise ValueError("Token payload must be an object")
        return result

    def _b64_bytes(self, value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")
