#!/usr/bin/env python3
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE_URL = os.getenv("SMOKE_BASE_URL", "http://127.0.0.1").rstrip("/")
WORKER_TOKEN = os.getenv("SMOKE_WORKER_TOKEN", "dev-token")
ADMIN_TOKEN = os.getenv("SMOKE_ADMIN_TOKEN", "dev-admin-token")
TIMEOUT_SEC = float(os.getenv("SMOKE_TIMEOUT_SEC", "15"))


@dataclass
class SmokeResponse:
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self):
        if not self.body:
            return None
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class SmokeFailure(RuntimeError):
    pass


def log(message: str) -> None:
    print(f"[smoke] {message}", flush=True)


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body=None,
    headers: dict[str, str] | None = None,
    expected: int | tuple[int, ...] = 200,
    body: bytes | None = None,
) -> SmokeResponse:
    expected_statuses = (expected,) if isinstance(expected, int) else expected
    req_headers = dict(headers or {})
    if token is not None:
        req_headers.update(auth_headers(token))

    data = body
    if json_body is not None:
        data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    url = f"{BASE_URL}{path}"
    req = Request(url, data=data, headers=req_headers, method=method)
    try:
        with urlopen(req, timeout=TIMEOUT_SEC) as response:
            smoke_response = SmokeResponse(
                status=response.status,
                headers=dict(response.headers.items()),
                body=response.read(),
            )
    except HTTPError as exc:
        smoke_response = SmokeResponse(
            status=exc.code,
            headers=dict(exc.headers.items()),
            body=exc.read(),
        )
    except URLError as exc:
        raise SmokeFailure(f"{method} {url} failed: {exc}") from exc

    if smoke_response.status not in expected_statuses:
        raise SmokeFailure(
            f"{method} {path}: expected {expected_statuses}, got {smoke_response.status}: "
            f"{smoke_response.text()}"
        )
    return smoke_response


def multipart_request(
    path: str,
    *,
    token: str,
    fields: dict[str, str],
    file_field: str,
    file_name: str,
    file_content: bytes,
    file_content_type: str,
    expected: int = 201,
) -> SmokeResponse:
    boundary = f"----obhod-smoke-{int(time.time() * 1000)}"
    chunks: list[bytes] = []

    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )

    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="{file_field}"; '
                f'filename="{file_name}"\r\n'
            ).encode(),
            f"Content-Type: {file_content_type}\r\n\r\n".encode(),
            file_content,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )

    return request(
        "POST",
        path,
        token=token,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        body=b"".join(chunks),
        expected=expected,
    )


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def assert_json_key(payload: dict, key: str):
    assert_true(key in payload, f"Response has no key {key}: {payload}")
    return payload[key]


def query(path: str, params: dict[str, str]) -> str:
    return f"{path}?{urlencode(params)}"


def main() -> int:
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    equipment_id = f"EQ-SMOKE-{suffix}"
    template_id = f"TPL-SMOKE-{suffix}"
    route_id = f"ROUTE-SMOKE-{suffix}"
    round_id = f"ROUND-SMOKE-{suffix}"
    route_step_id = f"{route_id}-STEP-1"
    planned_start = (datetime.now(timezone.utc) + timedelta(minutes=5)).replace(microsecond=0)

    log(f"base url: {BASE_URL}")

    log("auth: current worker")
    worker = request("GET", "/api/auth/me", token=WORKER_TOKEN).json()
    assert_true(worker["role"] == "WORKER", f"Expected WORKER, got {worker}")

    log("auth: current admin")
    admin = request("GET", "/api/auth/me", token=ADMIN_TOKEN).json()
    assert_true(admin["role"] == "ADMIN", f"Expected ADMIN, got {admin}")

    log("health: field and reports")
    request("GET", "/api/field/health")
    request("GET", "/api/reports/health", token=ADMIN_TOKEN)

    log("seed demo data")
    request("POST", "/api/field/admin/seed-demo", token=ADMIN_TOKEN)

    log("worker: demo task detail contains parameters and submitted results list")
    demo_detail = request("GET", "/api/field/tasks/ROUND-2026-04-17-000123", token=WORKER_TOKEN).json()
    assert_true(isinstance(demo_detail["checklist_results"], list), "Task detail has no checklist_results list")
    assert_true(
        any(
            item["equipment_id"] == "EQ-KC0103"
            and item["parameter_def"]["id"] == "PARAM-COMPRESSOR-PRESSURE-OUT"
            for item in demo_detail["equipment_parameters"]
        ),
        f"Task detail has no compressor pressure parameter: {demo_detail['equipment_parameters']}",
    )

    log("rbac: worker cannot create equipment")
    request(
        "POST",
        "/api/field/admin/equipment",
        token=WORKER_TOKEN,
        json_body={"id": f"{equipment_id}-RBAC", "name": "RBAC", "type_id": "demo"},
        expected=403,
    )

    log("admin: create equipment")
    equipment = request(
        "POST",
        "/api/field/admin/equipment",
        token=ADMIN_TOKEN,
        json_body={
            "id": equipment_id,
            "name": "Smoke test equipment",
            "type_id": "smoke",
            "location": "Smoke area",
        },
        expected=201,
    ).json()
    assert_true(equipment["qr_tag"] == f"QR:{equipment_id}", f"Unexpected qr tag: {equipment}")

    log("admin: create checklist template")
    checklist_template = request(
        "POST",
        "/api/field/admin/checklists/templates",
        token=ADMIN_TOKEN,
        json_body={
            "id": template_id,
            "name": "Smoke checklist",
            "equipment_type_id": "smoke",
            "items": [
                {
                    "seq_no": 1,
                    "question": "Smoke visual check is OK",
                    "answer_type": "bool",
                    "required_flag": True,
                },
                {
                    "seq_no": 2,
                    "question": "Smoke numeric value",
                    "answer_type": "number",
                    "required_flag": True,
                },
            ],
        },
        expected=201,
    ).json()
    item_1_id = checklist_template["items"][0]["id"]
    item_2_id = checklist_template["items"][1]["id"]

    log("admin: create route")
    route = request(
        "POST",
        "/api/field/admin/routes",
        token=ADMIN_TOKEN,
        json_body={
            "id": route_id,
            "name": "Smoke route",
            "duration_min": 30,
            "planning_rule": "manual",
            "steps": [
                {
                    "seq_no": 1,
                    "equipment_id": equipment_id,
                    "checkpoint_id": "CP-SMOKE",
                    "mandatory_flag": True,
                    "confirm_by": "qr",
                }
            ],
        },
        expected=201,
    ).json()
    assert_true(route["steps"][0]["id"] == route_step_id, f"Unexpected route step: {route}")

    log("admin: assign round")
    created_round = request(
        "POST",
        "/api/field/admin/rounds",
        token=ADMIN_TOKEN,
        json_body={
            "id": round_id,
            "route_template_id": route_id,
            "checklist_template_id": template_id,
            "employee_id": "dev-worker",
            "planned_start": planned_start.isoformat().replace("+00:00", "Z"),
        },
        expected=201,
    ).json()
    assert_true(created_round["employee_id"] == "dev-worker", f"Unexpected round: {created_round}")

    log("worker: sees assigned task")
    tasks = request("GET", "/api/field/tasks/my", token=WORKER_TOKEN).json()
    assert_true(any(item["id"] == round_id for item in tasks), f"Created round not in worker tasks: {tasks}")

    log("worker: get task detail")
    task_detail = request("GET", f"/api/field/tasks/{round_id}", token=WORKER_TOKEN).json()
    checklist_instance_id = task_detail["checklist_instance"]["id"]
    assert_true(task_detail["route"]["id"] == route_id, f"Unexpected task detail: {task_detail}")

    log("worker: start round")
    started_round = request("POST", f"/api/field/tasks/{round_id}/start", token=WORKER_TOKEN).json()
    assert_true(started_round["status"] == "in_progress", f"Round was not started: {started_round}")

    log("worker: wrong QR is rejected")
    request(
        "POST",
        f"/api/field/tasks/{round_id}/steps/{route_step_id}/confirm",
        token=WORKER_TOKEN,
        json_body={"confirm_by": "qr", "scanned_value": "QR:WRONG"},
        expected=409,
    )

    log("worker: correct QR opens checklist")
    confirm_response = request(
        "POST",
        f"/api/field/tasks/{round_id}/steps/{route_step_id}/confirm",
        token=WORKER_TOKEN,
        json_body={"confirm_by": "qr", "scanned_value": f"QR:{equipment_id}"},
    ).json()
    assert_true(confirm_response["equipment"]["id"] == equipment_id, f"Unexpected confirm response: {confirm_response}")

    log("worker: submit checklist item 1 with warning")
    item_1_result = request(
        "POST",
        f"/api/field/checklists/{checklist_instance_id}/items/{item_1_id}/result",
        token=WORKER_TOKEN,
        json_body={
            "equipment_id": equipment_id,
            "route_step_id": route_step_id,
            "result_code": "warning",
            "result_value": {"value": False},
            "comment": "Smoke check warning",
        },
    ).json()
    item_1_result_id = item_1_result["result"]["id"]
    assert_true(item_1_result["result"]["status"] == "warning", f"Unexpected checklist result: {item_1_result}")

    log("worker: submit checklist item 2")
    request(
        "POST",
        f"/api/field/checklists/{checklist_instance_id}/items/{item_2_id}/result",
        token=WORKER_TOKEN,
        json_body={
            "equipment_id": equipment_id,
            "route_step_id": route_step_id,
            "result_code": "ok",
            "result_value": {"value": 42, "unit": "u"},
            "comment": "Smoke numeric OK",
        },
    )

    log("worker: upload photo evidence")
    photo_content = b"smoke photo bytes\n"
    attachment = multipart_request(
        "/api/field/attachments",
        token=WORKER_TOKEN,
        fields={
            "entity_type": "checklist_item_result",
            "entity_id": item_1_result_id,
            "payload_json": json.dumps({"caption": "Smoke photo", "routeStepId": route_step_id}),
        },
        file_field="file",
        file_name="smoke-photo.txt",
        file_content=photo_content,
        file_content_type="text/plain",
    ).json()
    attachment_id = attachment["id"]
    assert_true(attachment["size_bytes"] == len(photo_content), f"Unexpected attachment: {attachment}")

    log("worker: list and download attachment")
    attachments = request(
        "GET",
        query("/api/field/attachments", {"entity_type": "checklist_item_result", "entity_id": item_1_result_id}),
        token=WORKER_TOKEN,
    ).json()
    assert_true(any(item["id"] == attachment_id for item in attachments), f"Attachment not listed: {attachments}")
    downloaded = request(
        "GET",
        f"/api/field/attachments/{attachment_id}/download",
        token=WORKER_TOKEN,
    )
    assert_true(downloaded.body == photo_content, "Downloaded attachment content mismatch")

    log("worker: submit equipment reading on seeded equipment")
    reading = request(
        "POST",
        "/api/field/equipment/EQ-KC0103/readings",
        token=WORKER_TOKEN,
        json_body={
            "parameter_def_id": "PARAM-COMPRESSOR-PRESSURE-OUT",
            "value_num": 1.5,
            "source": "mobile",
            "route_step_id": "ROUTE-KC0103-STEP-1",
        },
    ).json()
    assert_true(reading["status"] in {"normal", "warning", "critical"}, f"Unexpected reading: {reading}")

    log("worker: finish round")
    finished_round = request("POST", f"/api/field/tasks/{round_id}/finish", token=WORKER_TOKEN).json()
    assert_true(finished_round["status"] == "completed", f"Round was not completed: {finished_round}")

    log("reports: summary")
    summary = request("GET", "/api/reports/analytics/summary", token=ADMIN_TOKEN).json()
    assert_true(summary["rounds_total"] >= 1, f"Unexpected summary: {summary}")

    log("reports: list and detail")
    reports = request("GET", query("/api/reports/rounds", {"status": "completed"}), token=ADMIN_TOKEN).json()
    assert_true(any(item["id"] == round_id for item in reports), f"Completed round not in reports: {reports}")
    detail = request("GET", f"/api/reports/rounds/{round_id}", token=ADMIN_TOKEN).json()
    assert_true(detail["round"]["id"] == round_id, f"Unexpected report detail: {detail}")
    assert_true(len(detail["defects"]) >= 1, f"Auto-created defect not present in report detail: {detail}")
    assert_true(
        detail["defects"][0]["severity"] in {"info", "low", "medium", "high", "critical"},
        f"Unexpected defect severity: {detail['defects']}",
    )
    assert_true(
        any(item["id"] == attachment_id for item in detail["attachments"]),
        f"Attachment not present in report detail: {detail.get('attachments')}",
    )

    log("reports: analytics")
    equipment_analytics = request("GET", "/api/reports/analytics/equipment", token=ADMIN_TOKEN).json()
    employee_analytics = request("GET", "/api/reports/analytics/employees", token=ADMIN_TOKEN).json()
    assert_true(isinstance(equipment_analytics, list), "Equipment analytics is not a list")
    assert_true(isinstance(employee_analytics, list), "Employee analytics is not a list")

    log("rbac: worker cannot access reports")
    request("GET", "/api/reports/analytics/summary", token=WORKER_TOKEN, expected=403)

    log("OK: all smoke checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeFailure as exc:
        print(f"[smoke] FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
