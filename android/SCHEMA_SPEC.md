Обходной лист
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RoundSheet",
  "type": "object",
  "required": [
    "id", "orgId", "routeId", "plannedStart", "employeeId",
    "shiftId", "status", "objects", "signatures"
  ],
  "properties": {
    "id": { "type": "string" },
    "orgId": { "type": "string" },
    "routeId": { "type": "string" },
    "plannedStart": { "type": "string", "format": "date-time" },
    "plannedEnd": { "type": "string", "format": "date-time" },
    "employeeId": { "type": "string" },
    "shiftId": { "type": "string" },
    "qualificationId": { "type": "string" },
    "status": { "enum": ["planned", "sent", "in_progress", "paused", "done", "done_with_remarks", "cancelled"] },
    "objects": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["equipmentId", "seqNo", "checkpointId"],
        "properties": {
          "seqNo": { "type": "integer" },
          "equipmentId": { "type": "string" },
          "checkpointId": { "type": "string" },
          "parameterReadings": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["parameterCode", "value", "unit", "withinLimits"],
              "properties": {
                "parameterCode": { "type": "string" },
                "value": {},
                "unit": { "type": "string" },
                "withinLimits": { "type": "boolean" },
                "comment": { "type": "string" }
              }
            }
          }
        }
      }
    },
    "attachments": { "type": "array" },
    "signatures": { "type": "array" },
    "audit": { "type": "object" }
  }
}
{
  "id": "ROUND-2026-04-17-000123",
  "orgId": "ORG-01",
  "routeId": "ROUTE-KC0103",
  "plannedStart": "2026-04-17T06:00:00+03:00",
  "plannedEnd": "2026-04-17T07:00:00+03:00",
  "employeeId": "EMP-145",
  "shiftId": "SHIFT-A-2026-04-17",
  "qualificationId": "OPERATOR-TU",
  "status": "in_progress",
  "objects": [
    {
      "seqNo": 1,
      "equipmentId": "EQ-KC0103",
      "checkpointId": "PI-2",
      "parameterReadings": [
        {
          "parameterCode": "PRESSURE_OUT",
          "value": 1.48,
          "unit": "MPa",
          "withinLimits": true,
          "comment": "норма"
        }
      ]
    }
  ],
  "attachments": [],
  "signatures": [],
  "audit": {
    "deviceId": "MOB-0091",
    "schemaVersion": "1.0.0",
    "snapshotTsUtc": "2026-04-17T03:18:44Z"
  }
}
Маршрутный лист
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RouteSheet",
  "type": "object",
  "required": ["id", "name", "orgId", "durationMin", "planningRule", "steps", "version"],
  "properties": {
    "id": { "type": "string" },
    "name": { "type": "string" },
    "orgId": { "type": "string" },
    "departmentId": { "type": "string" },
    "qualificationId": { "type": "string" },
    "location": { "type": "string" },
    "durationMin": { "type": "integer" },
    "planningRule": { "type": "string" },
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["seqNo", "equipmentId", "mandatoryVisit"],
        "properties": {
          "seqNo": { "type": "integer" },
          "equipmentId": { "type": "string" },
          "checkpointId": { "type": "string" },
          "mandatoryVisit": { "type": "boolean" },
          "confirmBy": { "enum": ["manual", "qr", "nfc", "geofence"] }
        }
      }
    },
    "version": { "type": "string" }
  }
}
{
  "id": "ROUTE-KC0103",
  "name": "КС0103",
  "orgId": "ORG-01",
  "departmentId": "DEPT-UGP",
  "qualificationId": "OPERATOR-TU",
  "location": "АНГКМ / ЦПТГ / УКПГ",
  "durationMin": 60,
  "planningRule": "every_3_hours",
  "steps": [
    {
      "seqNo": 1,
      "equipmentId": "EQ-KC0103",
      "checkpointId": "PI-2",
      "mandatoryVisit": true,
      "confirmBy": "nfc"
    }
  ],
  "version": "3"
}
Чек-лист
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ChecklistInstance",
  "type": "object",
  "required": ["id", "templateId", "entityRef", "startedAt", "items", "status"],
  "properties": {
    "id": { "type": "string" },
    "templateId": { "type": "string" },
    "entityRef": {
      "type": "object",
      "required": ["entityType", "entityId"],
      "properties": {
        "entityType": { "enum": ["round", "work_order", "equipment_audit"] },
        "entityId": { "type": "string" }
      }
    },
    "startedAt": { "type": "string", "format": "date-time" },
    "finishedAt": { "type": "string", "format": "date-time" },
    "status": { "enum": ["draft", "running", "paused", "completed", "signed"] },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["seqNo", "question", "answerType"],
        "properties": {
          "seqNo": { "type": "integer" },
          "question": { "type": "string" },
          "answerType": { "enum": ["bool", "enum", "number", "text", "photo"] },
          "result": {},
          "comment": { "type": "string" },
          "dueDate": { "type": "string", "format": "date" }
        }
      }
    }
  }
}
{
  "id": "CL-2026-04-17-555",
  "templateId": "TPL-EVERYDAY-SAFTY-02",
  "entityRef": {
    "entityType": "round",
    "entityId": "ROUND-2026-04-17-000123"
  },
  "startedAt": "2026-04-17T06:05:00+03:00",
  "finishedAt": "2026-04-17T06:21:00+03:00",
  "status": "completed",
  "items": [
    {
      "seqNo": 1,
      "question": "На оборудовании установлены защитные кожухи и блокировки",
      "answerType": "bool",
      "result": true,
      "comment": ""
    },
    {
      "seqNo": 2,
      "question": "Давление на выходе компрессора",
      "answerType": "number",
      "result": 1.48,
      "comment": "в пределах допуска"
    }
  ]
}
Карточка оборудования
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "EquipmentCard",
  "type": "object",
  "required": ["id", "name", "type", "location", "passportData", "state"],
  "properties": {
    "id": { "type": "string" },
    "code": { "type": "string" },
    "name": { "type": "string" },
    "type": { "type": "string" },
    "location": { "type": "string" },
    "passportData": {
      "type": "object",
      "properties": {
        "manufacturer": { "type": "string" },
        "productionDate": { "type": "string", "format": "date" },
        "passportNo": { "type": "string" },
        "serialNo": { "type": "string" },
        "techNo": { "type": "string" }
      }
    },
    "state": { "type": "string" },
    "serviceNorms": { "type": "array" },
    "parameters": { "type": "array" },
    "tags": {
      "type": "object",
      "properties": {
        "qr": { "type": "string" },
        "nfc": { "type": "string" }
      }
    }
  }
}
{
  "id": "EQ-KC0103",
  "code": "000000029",
  "name": "Поршневая компрессорная установка КС-0103",
  "type": "compressor",
  "location": "АНГКМ / ЦПТГ / УКПГ",
  "passportData": {
    "manufacturer": "не указано",
    "productionDate": "2018-05-12",
    "passportNo": "PS-0103-2018",
    "serialNo": "SN-778812",
    "techNo": "KC0103"
  },
  "state": "in_operation",
  "serviceNorms": [
    { "kind": "inspection", "periodicity": "3h" }
  ],
  "parameters": [
    {
      "code": "PRESSURE_OUT",
      "unit": "MPa",
      "min": 1.4,
      "max": 1.6,
      "criticalMin": 1.3,
      "criticalMax": 1.7
    }
  ],
  "tags": {
    "qr": "QR:EQ-KC0103",
    "nfc": "NFC:04AABB11CC"
  }
}
Пример записи журнала 1С:ТОИР
Публично доступные описания 1С:ТОИР показывают, что факт выполнения работ в системе не замыкается на одном объекте: есть журнал объекта ремонта, наряд на ремонтные работы, акт выполнения этапа, акт выполнения регламентного мероприятия, дефект/неисправность и регистрационный журнал платформы. Поэтому для нового приложения я рекомендую делать единый событийный журнал поверх этих типов документов. [27]
{
  "journalEntryId": "JE-2026-04-17-987654",
  "eventTsUtc": "2026-04-17T03:22:15Z",
  "eventType": "defect_registered",
  "entityType": "defect",
  "entityId": "DEF-00001353",
  "orgId": "ORG-01",
  "equipmentId": "EQ-BLOCK-REAGENT-01",
  "checkpointId": "PI-2",
  "employeeId": "EMP-145",
  "shiftId": "SHIFT-A-2026-04-17",
  "sourceDocument": {
    "type": "checklist",
    "id": "CL-2026-04-17-555"
  },
  "workOrderId": null,
  "workActId": null,
  "statusBefore": "detected",
  "statusAfter": "confirmed",
  "payload": {
    "fixedValue": 892,
    "unit": "MPa",
    "criticalMin": 19,
    "criticalMax": 25,
    "attentionMarker": true,
    "comment": "значение вне уставки"
  },
  "signature": {
    "type": "simple_ep",
    "signedBy": "EMP-145",
    "signedAt": "2026-04-17T03:22:20Z"
  },
  "audit": {
    "deviceId": "MOB-0091",
    "syncBatchId": "SYNC-2026-04-17-00077",
    "schemaVersion": "1.0.0",
    "hash": "sha256:7f0c..."
  }
}
