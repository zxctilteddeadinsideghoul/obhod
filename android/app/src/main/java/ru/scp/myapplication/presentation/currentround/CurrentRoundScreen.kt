package ru.scp.myapplication.presentation.currentround

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import ru.scp.myapplication.ToirApplication
import ru.scp.myapplication.presentation.common.FactRow
import ru.scp.myapplication.presentation.common.RoundStatusPill
import ru.scp.myapplication.presentation.common.SectionCard
import ru.scp.myapplication.presentation.common.SyncChip

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CurrentRoundScreen(
    onOpenRoute: (String) -> Unit,
    onOpenChecklist: (String) -> Unit,
    onOpenPrintable: (String) -> Unit
) {
    val appContainer = (LocalContext.current.applicationContext as ToirApplication).appContainer
    val viewModel: CurrentRoundViewModel = viewModel(
        factory = CurrentRoundViewModelFactory(appContainer)
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Текущий обход") },
                actions = {
                    if (uiState.pendingSyncCount > 0) {
                        TextButton(onClick = viewModel::syncNow) {
                            Text("Отправить (${uiState.pendingSyncCount})")
                        }
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

            uiState.round == null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding)
                        .padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = uiState.errorMessage ?: "Нет доступного обходного листа",
                        style = MaterialTheme.typography.bodyLarge
                    )
                    Button(onClick = viewModel::refresh) {
                        Text("Повторить")
                    }
                }
            }

            else -> {
                val round = requireNotNull(uiState.round)
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        SectionCard(title = "Обходной лист") {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                    Text(
                                        text = round.id,
                                        style = MaterialTheme.typography.titleMedium,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                    Text(
                                        text = "Маршрут ${round.routeId}",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                                RoundStatusPill(status = round.status)
                            }
                            FactRow(label = "Плановое начало", value = round.plannedStart)
                            FactRow(label = "Плановое окончание", value = round.plannedEnd ?: "Не указано")
                            FactRow(label = "Сотрудник", value = round.employeeId)
                            FactRow(label = "Смена", value = round.shiftId)
                            SyncChip(syncState = round.syncState)
                        }
                    }
                    item {
                        SectionCard(title = "Действия") {
                            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                                Button(
                                    onClick = { onOpenChecklist(round.id) },
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Text("Открыть чек-лист")
                                }
                                OutlinedButton(
                                    onClick = { onOpenRoute(round.routeId) },
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Text("Открыть маршрутный лист")
                                }
                                OutlinedButton(
                                    onClick = { onOpenPrintable(round.id) },
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Text("Печатный вид чек-листа")
                                }
                            }
                        }
                    }
                    item {
                        SectionCard(title = "Очередь синхронизации") {
                            FactRow(
                                label = "Ожидают отправки",
                                value = uiState.pendingSyncCount.toString()
                            )
                            uiState.errorMessage?.let { message ->
                                Text(
                                    text = message,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.error
                                )
                            }
                        }
                    }
                    items(round.objects, key = { it.seqNo }) { roundObject ->
                        SectionCard(title = "Точка ${roundObject.seqNo}") {
                            FactRow(label = "Оборудование", value = roundObject.equipmentId)
                            FactRow(label = "Checkpoint", value = roundObject.checkpointId)
                            roundObject.parameterReadings.forEach { reading ->
                                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                    FactRow(
                                        label = reading.parameterCode,
                                        value = "${reading.value} ${reading.unit}"
                                    )
                                    Text(
                                        text = if (reading.withinLimits) {
                                            "В пределах допуска"
                                        } else {
                                            "Вне допуска"
                                        },
                                        style = MaterialTheme.typography.bodySmall,
                                        color = if (reading.withinLimits) {
                                            MaterialTheme.colorScheme.primary
                                        } else {
                                            MaterialTheme.colorScheme.error
                                        }
                                    )
                                    if (!reading.comment.isNullOrBlank()) {
                                        Text(
                                            text = reading.comment,
                                            style = MaterialTheme.typography.bodySmall,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
