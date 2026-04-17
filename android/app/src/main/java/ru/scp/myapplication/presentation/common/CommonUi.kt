package ru.scp.myapplication.presentation.common

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AssistChip
import androidx.compose.material3.AssistChipDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ru.scp.myapplication.domain.model.ChecklistStatus
import ru.scp.myapplication.domain.model.RoundStatus
import ru.scp.myapplication.domain.model.SyncState

@Composable
fun SectionCard(
    title: String,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Card(
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            content()
        }
    }
}

@Composable
fun FactRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun ProgressFactRow(
    progressPercent: Int,
    label: String = "Прогресс",
    modifier: Modifier = Modifier
) {
    val normalizedPercent = progressPercent.coerceIn(0, 100)

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = "$normalizedPercent%",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
        }
        LinearProgressIndicator(
            progress = { normalizedPercent / 100f },
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp),
            color = MaterialTheme.colorScheme.primary,
            trackColor = MaterialTheme.colorScheme.surfaceVariant
        )
    }
}

@Composable
fun SyncChip(syncState: SyncState) {
    val colors = when (syncState) {
        SyncState.SYNCED -> AssistChipDefaults.assistChipColors(
            containerColor = Color(0xFFD9F2E6),
            labelColor = Color(0xFF0B5D3B)
        )
        SyncState.PENDING -> AssistChipDefaults.assistChipColors(
            containerColor = Color(0xFFFFE8C2),
            labelColor = Color(0xFF7A4B00)
        )
        SyncState.FAILED -> AssistChipDefaults.assistChipColors(
            containerColor = Color(0xFFFAD7D7),
            labelColor = Color(0xFF8F2020)
        )
    }

    AssistChip(
        onClick = {},
        enabled = false,
        label = {
            Text(
                text = when (syncState) {
                    SyncState.SYNCED -> "Синхронизировано"
                    SyncState.PENDING -> "Ожидает отправки"
                    SyncState.FAILED -> "Ошибка синхронизации"
                }
            )
        },
        colors = colors
    )
}

@Composable
fun StatusPill(text: String, background: Color, foreground: Color) {
    Box(
        modifier = Modifier
            .background(background, RoundedCornerShape(50))
            .padding(horizontal = 12.dp, vertical = 6.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            color = foreground,
            style = MaterialTheme.typography.labelLarge
        )
    }
}

@Composable
fun RoundStatusPill(status: RoundStatus) {
    val (background, foreground, text) = when (status) {
        RoundStatus.PLANNED -> Triple(Color(0xFFE0E7FF), Color(0xFF22438A), "Запланирован")
        RoundStatus.SENT -> Triple(Color(0xFFE8F1FF), Color(0xFF1F518C), "Отправлен")
        RoundStatus.IN_PROGRESS -> Triple(Color(0xFFDCEBFF), Color(0xFF0F4674), "В работе")
        RoundStatus.PAUSED -> Triple(Color(0xFFFFE8C2), Color(0xFF7A4B00), "Пауза")
        RoundStatus.DONE -> Triple(Color(0xFFD9F2E6), Color(0xFF0B5D3B), "Завершен")
        RoundStatus.DONE_WITH_REMARKS -> Triple(Color(0xFFF7E0B9), Color(0xFF7A4B00), "С замечаниями")
        RoundStatus.CANCELLED -> Triple(Color(0xFFFAD7D7), Color(0xFF8F2020), "Отменен")
    }
    StatusPill(text = text, background = background, foreground = foreground)
}

@Composable
fun RoundStatusPill(status: String) {
    val normalized = status.lowercase()
    val (background, foreground, text) = when (normalized) {
        "planned" -> Triple(Color(0xFFE0E7FF), Color(0xFF22438A), "Запланирован")
        "in_progress" -> Triple(Color(0xFFDCEBFF), Color(0xFF0F4674), "В работе")
        "completed" -> Triple(Color(0xFFD9F2E6), Color(0xFF0B5D3B), "Завершен")
        else -> Triple(Color(0xFFE5E7EB), Color(0xFF334155), status)
    }
    StatusPill(text = text, background = background, foreground = foreground)
}

@Composable
fun ChecklistStatusPill(status: ChecklistStatus) {
    val (background, foreground, text) = when (status) {
        ChecklistStatus.DRAFT -> Triple(Color(0xFFE5E7EB), Color(0xFF334155), "Черновик")
        ChecklistStatus.RUNNING -> Triple(Color(0xFFDCEBFF), Color(0xFF0F4674), "Выполняется")
        ChecklistStatus.PAUSED -> Triple(Color(0xFFFFE8C2), Color(0xFF7A4B00), "Пауза")
        ChecklistStatus.COMPLETED -> Triple(Color(0xFFD9F2E6), Color(0xFF0B5D3B), "Завершен")
        ChecklistStatus.SIGNED -> Triple(Color(0xFFE0E7FF), Color(0xFF22438A), "Подписан")
    }
    StatusPill(text = text, background = background, foreground = foreground)
}

@Composable
fun ChecklistStatusPill(status: String) {
    val normalized = status.lowercase()
    val (background, foreground, text) = when (normalized) {
        "draft" -> Triple(Color(0xFFE5E7EB), Color(0xFF334155), "Черновик")
        "in_progress" -> Triple(Color(0xFFDCEBFF), Color(0xFF0F4674), "Выполняется")
        "completed" -> Triple(Color(0xFFD9F2E6), Color(0xFF0B5D3B), "Завершен")
        else -> Triple(Color(0xFFE5E7EB), Color(0xFF334155), status)
    }
    StatusPill(text = text, background = background, foreground = foreground)
}

@Composable
fun ResultStatusCard(status: String, message: String, modifier: Modifier = Modifier) {
    val normalized = status.lowercase()
    val containerColor = when (normalized) {
        "critical" -> Color(0xFFFDE2E1)
        "warning" -> Color(0xFFFFE8C2)
        "normal" -> Color(0xFFD9F2E6)
        else -> MaterialTheme.colorScheme.surfaceVariant
    }
    val contentColor = when (normalized) {
        "critical" -> Color(0xFF8F2020)
        "warning" -> Color(0xFF7A4B00)
        "normal" -> Color(0xFF0B5D3B)
        else -> MaterialTheme.colorScheme.onSurfaceVariant
    }

    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = containerColor)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = status.replaceFirstChar { it.uppercase() },
                color = contentColor,
                fontWeight = FontWeight.SemiBold
            )
            Text(
                text = message,
                color = contentColor,
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}
