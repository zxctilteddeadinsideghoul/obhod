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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Print
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
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
import ru.scp.myapplication.domain.model.AnswerType
import ru.scp.myapplication.presentation.common.ChecklistStatusPill
import ru.scp.myapplication.presentation.common.FactRow
import ru.scp.myapplication.presentation.common.SectionCard
import ru.scp.myapplication.presentation.common.SyncChip

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChecklistScreen(
    roundId: String,
    onBack: () -> Unit,
    onOpenPrintable: (String) -> Unit
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
                title = { Text("Чек-лист") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Назад"
                        )
                    }
                },
                actions = {
                    uiState.checklist?.let { checklist ->
                        IconButton(onClick = { onOpenPrintable(checklist.entityId) }) {
                            Icon(
                                imageVector = Icons.Default.Print,
                                contentDescription = "Печатный вид"
                            )
                        }
                    }
                    if (uiState.pendingSyncCount > 0) {
                        TextButton(onClick = viewModel::syncNow) {
                            Text("Синхр.")
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

            uiState.checklist == null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding)
                        .padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(uiState.errorMessage ?: "Чек-лист недоступен")
                    Button(onClick = viewModel::refresh) {
                        Text("Повторить")
                    }
                }
            }

            else -> {
                val checklist = requireNotNull(uiState.checklist)
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        SectionCard(title = "Экземпляр чек-листа") {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                    Text(
                                        text = checklist.id,
                                        style = MaterialTheme.typography.titleMedium,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                    Text(
                                        text = checklist.templateId,
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                                ChecklistStatusPill(checklist.status)
                            }
                            FactRow(label = "Сущность", value = "${checklist.entityType}:${checklist.entityId}")
                            FactRow(label = "Начат", value = checklist.startedAt)
                            FactRow(label = "Завершен", value = checklist.finishedAt ?: "Еще нет")
                            FactRow(label = "Ожидают отправки", value = uiState.pendingSyncCount.toString())
                            SyncChip(checklist.syncState)
                        }
                    }
                    items(checklist.items, key = { it.id }) { item ->
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Column(
                                modifier = Modifier.padding(16.dp),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.Top
                                ) {
                                    Text(
                                        text = "${item.seqNo}. ${item.question}",
                                        style = MaterialTheme.typography.bodyLarge,
                                        modifier = Modifier.weight(1f)
                                    )
                                    if (item.answerType == AnswerType.BOOL) {
                                        Checkbox(
                                            checked = item.resultBoolean == true,
                                            onCheckedChange = { checked ->
                                                viewModel.toggleItem(item.checklistId, item.seqNo, checked)
                                            }
                                        )
                                    }
                                }

                                when (item.answerType) {
                                    AnswerType.BOOL -> {
                                        Text(
                                            text = if (item.resultBoolean == true) "Отмечено" else "Не отмечено",
                                            style = MaterialTheme.typography.bodyMedium
                                        )
                                    }

                                    AnswerType.NUMBER -> {
                                        Text(
                                            text = "Значение: ${item.resultNumber ?: "-"}",
                                            style = MaterialTheme.typography.bodyMedium
                                        )
                                    }

                                    else -> {
                                        Text(
                                            text = item.resultText ?: "Без результата",
                                            style = MaterialTheme.typography.bodyMedium
                                        )
                                    }
                                }

                                if (!item.comment.isNullOrBlank()) {
                                    Text(
                                        text = item.comment,
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                                SyncChip(item.syncState)
                            }
                        }
                    }
                    uiState.errorMessage?.let { message ->
                        item {
                            Text(
                                text = message,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.error
                            )
                        }
                    }
                }
            }
        }
    }
}
