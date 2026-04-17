package ru.scp.myapplication.presentation.currentround

import androidx.compose.foundation.clickable
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
import ru.scp.myapplication.domain.model.AssignedTask
import ru.scp.myapplication.presentation.common.FactRow
import ru.scp.myapplication.presentation.common.ProgressFactRow
import ru.scp.myapplication.presentation.common.RoundStatusPill
import ru.scp.myapplication.presentation.common.SectionCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CurrentRoundScreen(
    onOpenTask: (String) -> Unit
) {
    val appContainer = (LocalContext.current.applicationContext as ToirApplication).appContainer
    val viewModel: CurrentRoundViewModel = viewModel(
        factory = CurrentRoundViewModelFactory(appContainer)
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Назначенные обходы") },
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

            uiState.worker == null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding)
                        .padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(uiState.errorMessage ?: "Профиль работника не получен")
                    Button(onClick = viewModel::refresh) {
                        Text("Повторить")
                    }
                }
            }

            else -> {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        SectionCard(title = "Подключение") {
                            FactRow(label = "Base URL", value = uiState.baseUrl)
                            uiState.errorMessage?.let { message ->
                                Text(
                                    text = message,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.error
                                )
                            }
                        }
                    }
                    item {
                        val worker = requireNotNull(uiState.worker)
                        SectionCard(title = "Текущий работник") {
                            FactRow(label = "Имя", value = worker.name)
                            FactRow(label = "ID", value = worker.id)
                            FactRow(label = "Роль", value = worker.role)
                        }
                    }
                    if (uiState.tasks.isEmpty()) {
                        item {
                            SectionCard(title = "Задания") {
                                Text("Backend не вернул назначенных обходов")
                            }
                        }
                    } else {
                        items(uiState.tasks, key = { it.id }) { task ->
                            TaskCard(task = task, onOpenTask = onOpenTask)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun TaskCard(task: AssignedTask, onOpenTask: (String) -> Unit) {
    SectionCard(
        title = task.routeName.ifBlank { task.routeId },
        modifier = Modifier.clickable { onOpenTask(task.id) }
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = task.id,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = task.routeId,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            RoundStatusPill(task.status)
        }
        FactRow(label = "Плановое начало", value = task.plannedStart)
        FactRow(label = "Плановое окончание", value = task.plannedEnd ?: "Не указано")
        ProgressFactRow(progressPercent = task.completionPct)
        Button(
            onClick = { onOpenTask(task.id) },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Открыть обход")
        }
    }
}
