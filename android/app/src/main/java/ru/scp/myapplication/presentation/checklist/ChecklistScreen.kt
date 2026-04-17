package ru.scp.myapplication.presentation.checklist

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import ru.scp.myapplication.ToirApplication
import ru.scp.myapplication.domain.model.ChecklistTemplateItem
import ru.scp.myapplication.domain.model.RouteStepDetails
import ru.scp.myapplication.presentation.common.ChecklistStatusPill
import ru.scp.myapplication.presentation.common.FactRow
import ru.scp.myapplication.presentation.common.ResultStatusCard
import ru.scp.myapplication.presentation.common.RoundStatusPill
import ru.scp.myapplication.presentation.common.SectionCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChecklistScreen(
    roundId: String,
    onBack: () -> Unit
) {
    val appContainer = (LocalContext.current.applicationContext as ToirApplication).appContainer
    val viewModel: ChecklistViewModel = viewModel(
        key = roundId,
        factory = ChecklistViewModelFactory(appContainer, roundId)
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Карточка обхода") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Назад"
                        )
                    }
                },
                actions = {
                    TextButton(onClick = viewModel::refresh) {
                        Text("Обновить")
                    }
                }
            )
        }
    ) { innerPadding ->
        when {
            uiState.isLoading -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    CircularProgressIndicator()
                }
            }

            uiState.details == null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding)
                        .padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(uiState.errorMessage ?: "Карточка обхода недоступна")
                    Button(onClick = viewModel::refresh) {
                        Text("Повторить")
                    }
                }
            }

            else -> {
                val details = requireNotNull(uiState.details)
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        SectionCard(title = "Обход") {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                    Text(
                                        text = details.round.id,
                                        style = MaterialTheme.typography.titleMedium,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                    Text(
                                        text = details.route.name,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                                RoundStatusPill(details.round.status)
                            }
                            FactRow(label = "Маршрут", value = details.route.id)
                            FactRow(label = "Локация", value = details.route.location ?: "Не указана")
                            FactRow(label = "Сотрудник", value = details.round.employeeId)
                            FactRow(label = "Плановое начало", value = details.round.plannedStart)
                            FactRow(label = "Факт. начало", value = details.round.actualStart ?: "Ещё нет")
                            Button(
                                onClick = viewModel::startRound,
                                enabled = !uiState.isSubmitting && details.round.status == "planned",
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("Старт обхода")
                            }
                        }
                    }
                    item {
                        SectionCard(title = "Чек-лист") {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                    Text(
                                        text = details.checklistTemplate.name ?: details.checklistTemplate.id,
                                        style = MaterialTheme.typography.titleSmall,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                    Text(
                                        text = details.checklistInstance.id,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                                ChecklistStatusPill(uiState.checklistStatus)
                            }
                            FactRow(label = "Прогресс", value = "${uiState.checklistCompletionPct}%")
                            if (uiState.confirmedStep == null) {
                                Text(
                                    text = "Форма откроется после успешного подтверждения QR/NFC точки.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }
                    items(details.route.steps, key = { it.id }) { step ->
                        val equipment = details.equipment.firstOrNull { it.id == step.equipmentId }
                        StepConfirmationCard(
                            step = step,
                            equipmentName = equipment?.name ?: step.equipmentId,
                            qrTag = equipment?.qrTag,
                            nfcTag = equipment?.nfcTag,
                            isSubmitting = uiState.isSubmitting,
                            confirmedStepId = uiState.confirmedStep?.visit?.routeStepId,
                            onConfirm = { confirmBy, scannedValue ->
                                viewModel.confirmStep(step, confirmBy, scannedValue)
                            }
                        )
                    }
                    if (uiState.confirmedStep != null) {
                        item {
                            SectionCard(title = "Подтверждённая точка") {
                                val confirmation = requireNotNull(uiState.confirmedStep)
                                FactRow(label = "Оборудование", value = confirmation.equipment.name)
                                FactRow(label = "Способ", value = confirmation.visit.confirmedBy)
                                FactRow(label = "Значение", value = confirmation.visit.scannedValue)
                                FactRow(label = "Время", value = confirmation.visit.confirmedAt)
                            }
                        }
                        items(uiState.visibleChecklistItems, key = { it.id }) { item ->
                            val activeStep = details.route.steps.firstOrNull {
                                it.id == uiState.confirmedStep?.visit?.routeStepId
                            }
                            val equipmentId = uiState.confirmedStep?.equipment?.id.orEmpty()
                            when (item.answerType) {
                                "bool" -> BooleanChecklistItemCard(
                                    item = item,
                                    submittedValue = uiState.submittedItems[item.id],
                                    isSubmitting = uiState.isSubmitting,
                                    onSubmit = { checked, comment ->
                                        viewModel.submitBooleanResult(
                                            itemId = item.id,
                                            equipmentId = equipmentId,
                                            checked = checked,
                                            comment = comment
                                        )
                                    }
                                )

                                "number" -> NumericChecklistItemCard(
                                    item = item,
                                    step = activeStep,
                                    equipmentId = equipmentId,
                                    submittedValue = uiState.submittedItems[item.id],
                                    readingResponse = uiState.readingStatuses[item.id],
                                    isSubmitting = uiState.isSubmitting,
                                    onSubmitResult = { value, unit, comment ->
                                        viewModel.submitNumericResult(
                                            itemId = item.id,
                                            equipmentId = equipmentId,
                                            value = value,
                                            unit = unit,
                                            comment = comment
                                        )
                                    },
                                    onSubmitReading = { value ->
                                        activeStep?.let {
                                            viewModel.submitReading(
                                                step = it,
                                                equipmentId = equipmentId,
                                                itemId = item.id,
                                                normRef = item.normRef,
                                                value = value
                                            )
                                        }
                                    }
                                )

                                else -> SectionCard(title = "${item.seqNo}. ${item.question}") {
                                    Text("Тип ответа ${item.answerType} в этой итерации только отображается.")
                                }
                            }
                        }
                    }
                    item {
                        SectionCard(title = "Завершение") {
                            Text(
                                text = "Backend закроет обход только если обязательные пункты уже заполнены.",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            OutlinedButton(
                                onClick = viewModel::finishRound,
                                enabled = !uiState.isSubmitting && details.round.status != "completed",
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("Завершить обход")
                            }
                        }
                    }
                    uiState.infoMessage?.let { message ->
                        item {
                            Text(
                                text = message,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                    uiState.errorMessage?.let { message ->
                        item {
                            Text(
                                text = message,
                                color = MaterialTheme.colorScheme.error
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun StepConfirmationCard(
    step: RouteStepDetails,
    equipmentName: String,
    qrTag: String?,
    nfcTag: String?,
    isSubmitting: Boolean,
    confirmedStepId: String?,
    onConfirm: (String, String) -> Unit
) {
    var confirmBy by rememberSaveable(step.id) { mutableStateOf(step.confirmBy ?: "qr") }
    var scannedValue by rememberSaveable(step.id) {
        mutableStateOf(defaultScannedValue(confirmBy, qrTag, nfcTag))
    }

    SectionCard(title = "Точка ${step.seqNo}") {
        FactRow(label = "Оборудование", value = equipmentName)
        FactRow(label = "Checkpoint", value = step.checkpointId ?: "Не указан")
        FactRow(label = "Обязательно", value = if (step.mandatoryFlag) "Да" else "Нет")
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(
                onClick = {
                    confirmBy = "qr"
                    scannedValue = qrTag ?: scannedValue
                },
                enabled = !isSubmitting
            ) {
                Text("QR")
            }
            OutlinedButton(
                onClick = {
                    confirmBy = "nfc"
                    scannedValue = nfcTag ?: scannedValue
                },
                enabled = !isSubmitting
            ) {
                Text("NFC")
            }
        }
        OutlinedTextField(
            value = scannedValue,
            onValueChange = { scannedValue = it },
            label = { Text("Сканированное значение") },
            supportingText = {
                Text("Рекомендуется ${defaultScannedValue(confirmBy, qrTag, nfcTag)}")
            },
            enabled = !isSubmitting,
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            onClick = { onConfirm(confirmBy, scannedValue) },
            enabled = !isSubmitting && scannedValue.isNotBlank(),
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(if (confirmedStepId == step.id) "Подтвердить повторно" else "Подтвердить точку")
        }
    }
}

@Composable
private fun BooleanChecklistItemCard(
    item: ChecklistTemplateItem,
    submittedValue: ru.scp.myapplication.domain.model.SubmittedChecklistValue?,
    isSubmitting: Boolean,
    onSubmit: (Boolean, String) -> Unit
) {
    var comment by rememberSaveable(item.id) { mutableStateOf(submittedValue?.comment.orEmpty()) }

    SectionCard(title = "${item.seqNo}. ${item.question}") {
        Text(
            text = if (item.requiredFlag) "Обязательный пункт" else "Необязательный пункт",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        OutlinedTextField(
            value = comment,
            onValueChange = { comment = it },
            label = { Text("Комментарий") },
            enabled = !isSubmitting,
            modifier = Modifier.fillMaxWidth()
        )
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = { onSubmit(true, comment) },
                enabled = !isSubmitting,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Да")
            }
            OutlinedButton(
                onClick = { onSubmit(false, comment) },
                enabled = !isSubmitting,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Нет")
            }
        }
        submittedValue?.let {
            ResultStatusCard(
                status = it.status,
                message = "Последний ответ: ${it.displayValue}" +
                    if (it.comment.isNullOrBlank()) "" else "\n${it.comment}"
            )
        }
    }
}

@Composable
private fun NumericChecklistItemCard(
    item: ChecklistTemplateItem,
    step: RouteStepDetails?,
    equipmentId: String,
    submittedValue: ru.scp.myapplication.domain.model.SubmittedChecklistValue?,
    readingResponse: ru.scp.myapplication.domain.model.EquipmentReadingResponse?,
    isSubmitting: Boolean,
    onSubmitResult: (Double, String?, String) -> Unit,
    onSubmitReading: (Double) -> Unit
) {
    var valueText by rememberSaveable(item.id) { mutableStateOf("") }
    var comment by rememberSaveable("${item.id}-comment") { mutableStateOf(submittedValue?.comment.orEmpty()) }
    val unit = defaultUnitFor(item.normRef)
    val value = valueText.toDoubleOrNull()
    val parameterDefId = pressureParameterDefIdFor(item.normRef, item.id)

    SectionCard(title = "${item.seqNo}. ${item.question}") {
        FactRow(label = "Оборудование", value = equipmentId)
        FactRow(label = "Norm ref", value = item.normRef ?: "Не указан")
        OutlinedTextField(
            value = valueText,
            onValueChange = { valueText = it.replace(',', '.') },
            label = { Text("Значение${if (unit != null) ", $unit" else ""}") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            enabled = !isSubmitting,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = comment,
            onValueChange = { comment = it },
            label = { Text("Комментарий") },
            enabled = !isSubmitting,
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            onClick = { value?.let { onSubmitResult(it, unit, comment) } },
            enabled = !isSubmitting && value != null,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Отправить результат пункта")
        }
        OutlinedButton(
            onClick = { value?.let(onSubmitReading) },
            enabled = !isSubmitting && value != null && parameterDefId != null && step != null,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Отправить показание оборудования")
        }
        if (parameterDefId == null) {
            Text(
                text = "Для этого пункта не удалось определить parameter_def_id для endpoint readings.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.error
            )
        }
        submittedValue?.let {
            ResultStatusCard(
                status = it.status,
                message = "Последний результат: ${it.displayValue}" +
                    if (it.comment.isNullOrBlank()) "" else "\n${it.comment}"
            )
        }
        readingResponse?.let {
            ResultStatusCard(status = it.status, message = it.message)
        }
    }
}

private fun defaultScannedValue(confirmBy: String, qrTag: String?, nfcTag: String?): String =
    when (confirmBy) {
        "nfc" -> nfcTag ?: qrTag ?: ""
        else -> qrTag ?: nfcTag ?: ""
    }
