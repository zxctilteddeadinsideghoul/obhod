package ru.scp.myapplication.presentation.routesheet

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import ru.scp.myapplication.ToirApplication
import ru.scp.myapplication.presentation.common.FactRow
import ru.scp.myapplication.presentation.common.SectionCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RouteSheetScreen(
    routeId: String,
    onBack: () -> Unit
) {
    val appContainer = (LocalContext.current.applicationContext as ToirApplication).appContainer
    val viewModel: RouteSheetViewModel = viewModel(
        key = routeId,
        factory = RouteSheetViewModelFactory(appContainer, routeId)
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Маршрутный лист") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Назад"
                        )
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

            uiState.route == null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding)
                        .padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically)
                ) {
                    Text(uiState.errorMessage ?: "Маршрут недоступен")
                }
            }

            else -> {
                val route = requireNotNull(uiState.route)
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(innerPadding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        SectionCard(title = route.name) {
                            FactRow(label = "ИД", value = route.id)
                            FactRow(label = "Локация", value = route.location ?: "Не указана")
                            FactRow(label = "Длительность", value = "${route.durationMin} мин")
                            FactRow(label = "Правило", value = route.planningRule)
                            FactRow(label = "Версия", value = route.version)
                        }
                    }
                    items(route.steps, key = { it.seqNo }) { step ->
                        SectionCard(title = "Шаг ${step.seqNo}") {
                            FactRow(label = "Оборудование", value = step.equipmentId)
                            FactRow(label = "Checkpoint", value = step.checkpointId ?: "Не указан")
                            FactRow(
                                label = "Обязательный визит",
                                value = if (step.mandatoryVisit) "Да" else "Нет"
                            )
                            FactRow(label = "Подтверждение", value = step.confirmBy ?: "manual")
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
