package ru.scp.myapplication.core.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import ru.scp.myapplication.presentation.checklist.ChecklistScreen
import ru.scp.myapplication.presentation.currentround.CurrentRoundScreen
import ru.scp.myapplication.presentation.printable.PrintableChecklistScreen
import ru.scp.myapplication.presentation.routesheet.RouteSheetScreen

@Composable
fun ToirApp() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = ToirDestination.CurrentRound.route
    ) {
        composable(ToirDestination.CurrentRound.route) {
            CurrentRoundScreen(
                onOpenRoute = { routeId ->
                    navController.navigate(ToirDestination.RouteSheet.createRoute(routeId))
                },
                onOpenChecklist = { roundId ->
                    navController.navigate(ToirDestination.Checklist.createRoute(roundId))
                },
                onOpenPrintable = { roundId ->
                    navController.navigate(ToirDestination.PrintableChecklist.createRoute(roundId))
                }
            )
        }
        composable(ToirDestination.RouteSheet.route) { backStackEntry ->
            RouteSheetScreen(
                routeId = backStackEntry.arguments?.getString("routeId").orEmpty(),
                onBack = { navController.popBackStack() }
            )
        }
        composable(ToirDestination.Checklist.route) { backStackEntry ->
            ChecklistScreen(
                roundId = backStackEntry.arguments?.getString("roundId").orEmpty(),
                onBack = { navController.popBackStack() },
                onOpenPrintable = { roundId ->
                    navController.navigate(ToirDestination.PrintableChecklist.createRoute(roundId))
                }
            )
        }
        composable(ToirDestination.PrintableChecklist.route) { backStackEntry ->
            PrintableChecklistScreen(
                roundId = backStackEntry.arguments?.getString("roundId").orEmpty(),
                onBack = { navController.popBackStack() }
            )
        }
    }
}
