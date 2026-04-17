package ru.scp.myapplication.core.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import ru.scp.myapplication.presentation.checklist.ChecklistScreen
import ru.scp.myapplication.presentation.currentround.CurrentRoundScreen

@Composable
fun ToirApp() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = ToirDestination.CurrentRound.route
    ) {
        composable(ToirDestination.CurrentRound.route) {
            CurrentRoundScreen(
                onOpenTask = { roundId ->
                    navController.navigate(ToirDestination.Checklist.createRoute(roundId))
                }
            )
        }
        composable(ToirDestination.Checklist.route) { backStackEntry ->
            ChecklistScreen(
                roundId = backStackEntry.arguments?.getString("roundId").orEmpty(),
                onBack = { navController.popBackStack() }
            )
        }
    }
}
