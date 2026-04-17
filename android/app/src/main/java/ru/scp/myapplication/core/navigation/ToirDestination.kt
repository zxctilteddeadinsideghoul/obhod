package ru.scp.myapplication.core.navigation

sealed class ToirDestination(val route: String) {
    data object CurrentRound : ToirDestination("current_round")
    data object RouteSheet : ToirDestination("route_sheet/{routeId}") {
        fun createRoute(routeId: String): String = "route_sheet/$routeId"
    }

    data object Checklist : ToirDestination("checklist/{roundId}") {
        fun createRoute(roundId: String): String = "checklist/$roundId"
    }

    data object PrintableChecklist : ToirDestination("printable/{roundId}") {
        fun createRoute(roundId: String): String = "printable/$roundId"
    }
}
