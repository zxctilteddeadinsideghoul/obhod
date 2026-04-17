package ru.scp.myapplication.domain.model

import com.google.gson.annotations.SerializedName

data class WorkerProfile(
    val id: String,
    val role: String,
    val name: String
)

data class AssignedTask(
    val id: String,
    val status: String,
    @SerializedName("route_id") val routeId: String,
    @SerializedName("route_name") val routeName: String,
    @SerializedName("planned_start") val plannedStart: String,
    @SerializedName("planned_end") val plannedEnd: String?,
    @SerializedName("completion_pct") val completionPct: Int
)

data class TaskDetails(
    val round: RoundDetails,
    val route: RouteDetails,
    val equipment: List<EquipmentDetails>,
    @SerializedName("checklist_instance") val checklistInstance: ChecklistInstance,
    @SerializedName("checklist_template") val checklistTemplate: ChecklistTemplate
)

data class RoundDetails(
    val id: String,
    @SerializedName("org_id") val orgId: String?,
    @SerializedName("route_template_id") val routeTemplateId: String,
    @SerializedName("planned_start") val plannedStart: String,
    @SerializedName("planned_end") val plannedEnd: String?,
    @SerializedName("actual_start") val actualStart: String?,
    @SerializedName("actual_end") val actualEnd: String?,
    @SerializedName("shift_id") val shiftId: String?,
    @SerializedName("employee_id") val employeeId: String,
    val status: String,
    @SerializedName("qualification_id") val qualificationId: String?
)

data class RouteDetails(
    val id: String,
    val name: String,
    val location: String?,
    @SerializedName("duration_min") val durationMin: Int?,
    @SerializedName("planning_rule") val planningRule: String?,
    val version: String?,
    val steps: List<RouteStepDetails>
)

data class RouteStepDetails(
    val id: String,
    @SerializedName("seq_no") val seqNo: Int,
    @SerializedName("equipment_id") val equipmentId: String,
    @SerializedName("checkpoint_id") val checkpointId: String?,
    @SerializedName("mandatory_flag") val mandatoryFlag: Boolean,
    @SerializedName("confirm_by") val confirmBy: String?
)

data class EquipmentDetails(
    val id: String,
    val code: String?,
    val name: String,
    @SerializedName("tech_no") val techNo: String?,
    val location: String?,
    @SerializedName("qr_tag") val qrTag: String?,
    @SerializedName("nfc_tag") val nfcTag: String?
)

data class ChecklistInstance(
    val id: String,
    val status: String,
    @SerializedName("completion_pct") val completionPct: Int
)

data class ChecklistTemplate(
    val id: String,
    val name: String?,
    val items: List<ChecklistTemplateItem>
)

data class ChecklistTemplateItem(
    val id: String,
    @SerializedName("seq_no") val seqNo: Int,
    val question: String,
    @SerializedName("answer_type") val answerType: String,
    @SerializedName("required_flag") val requiredFlag: Boolean,
    @SerializedName("norm_ref") val normRef: String?
)

data class ConfirmStepRequest(
    @SerializedName("confirm_by") val confirmBy: String,
    @SerializedName("scanned_value") val scannedValue: String,
    @SerializedName("payload_json") val payloadJson: DevicePayload? = null
)

data class DevicePayload(
    val deviceId: String
)

data class ConfirmStepResponse(
    val status: String,
    val visit: StepVisit,
    val equipment: EquipmentDetails,
    @SerializedName("checklist_instance") val checklistInstance: ChecklistInstance,
    @SerializedName("checklist_template") val checklistTemplate: ChecklistTemplate
)

data class StepVisit(
    val id: String,
    @SerializedName("route_step_id") val routeStepId: String,
    @SerializedName("equipment_id") val equipmentId: String,
    @SerializedName("confirmed_by") val confirmedBy: String,
    @SerializedName("scanned_value") val scannedValue: String,
    @SerializedName("confirmed_at") val confirmedAt: String,
    val status: String
)

data class SubmitChecklistItemResultRequest(
    @SerializedName("equipment_id") val equipmentId: String,
    @SerializedName("result_code") val resultCode: String,
    @SerializedName("result_value") val resultValue: ResultValuePayload,
    val comment: String?
)

data class ResultValuePayload(
    val value: Any,
    val unit: String? = null
)

data class ChecklistItemResultResponse(
    val result: ChecklistItemResult,
    @SerializedName("checklist_instance") val checklistInstance: ChecklistInstance
)

data class ChecklistItemResult(
    val id: String,
    @SerializedName("item_template_id") val itemTemplateId: String,
    @SerializedName("equipment_id") val equipmentId: String,
    @SerializedName("result_code") val resultCode: String,
    val comment: String?,
    val status: String
)

data class SubmitEquipmentReadingRequest(
    @SerializedName("parameter_def_id") val parameterDefId: String,
    @SerializedName("value_num") val valueNum: Double,
    val source: String,
    @SerializedName("route_step_id") val routeStepId: String,
    @SerializedName("checklist_item_result_id") val checklistItemResultId: String?,
    @SerializedName("payload_json") val payloadJson: DevicePayload? = null
)

data class EquipmentReadingResponse(
    val reading: EquipmentReading,
    val status: String,
    val message: String
)

data class EquipmentReading(
    val id: String?,
    @SerializedName("equipment_id") val equipmentId: String,
    @SerializedName("parameter_def_id") val parameterDefId: String,
    @SerializedName("value_num") val valueNum: Double?,
    @SerializedName("within_limits") val withinLimits: Boolean?
)

data class RoundLifecycleResponse(
    val id: String,
    val status: String,
    @SerializedName("actual_start") val actualStart: String?,
    @SerializedName("actual_end") val actualEnd: String?
)

data class SubmittedChecklistValue(
    val resultId: String,
    val displayValue: String,
    val comment: String?,
    val status: String
)
