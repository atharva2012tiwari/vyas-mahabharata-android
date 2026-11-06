package com.vyas.mahabharata.ui.navigation

import androidx.compose.animation.AnimatedContentTransitionScope
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.vyas.mahabharata.data.repository.MahabharataRepository
import com.vyas.mahabharata.ui.screens.bookmarks.BookmarksScreen
import com.vyas.mahabharata.ui.screens.explorer.ParvaExplorerScreen
import com.vyas.mahabharata.ui.screens.reader.ReadingCanvasScreen
import com.vyas.mahabharata.ui.screens.search.SearchScreen
import com.vyas.mahabharata.ui.screens.welcome.WelcomeScreen

sealed class Screen(val route: String) {
    data object Welcome : Screen("welcome")
    data object Explorer : Screen("explorer")
    data object Reader : Screen("reader/{parvaNumber}/{chapterNumber}?initialVerse={initialVerse}") {
        fun createRoute(parvaNumber: Int, chapterNumber: Int, initialVerse: Int? = null): String {
            return if (initialVerse != null && initialVerse > 0) {
                "reader/$parvaNumber/$chapterNumber?initialVerse=$initialVerse"
            } else {
                "reader/$parvaNumber/$chapterNumber"
            }
        }
    }
    data object Search : Screen("search")
    data object Bookmarks : Screen("bookmarks")
}

@Composable
fun VyasNavHost(
    navController: NavHostController,
    repository: MahabharataRepository,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Explorer.route,
        modifier = modifier
    ) {
        // Welcome Screen with Procedural Ripples
        composable(
            route = Screen.Welcome.route,
            enterTransition = { fadeIn(animationSpec = tween(500)) },
            exitTransition = { fadeOut(animationSpec = tween(500)) }
        ) {
            WelcomeScreen(
                onEnterClick = {
                    navController.navigate(Screen.Explorer.route) {
                        popUpTo(Screen.Welcome.route) { inclusive = true }
                    }
                }
            )
        }

        // 18 Parvas Explorer Screen
        composable(
            route = Screen.Explorer.route,
            enterTransition = { fadeIn(animationSpec = tween(400)) },
            exitTransition = { fadeOut(animationSpec = tween(400)) }
        ) {
            ParvaExplorerScreen(
                repository = repository,
                onNavigateToChapter = { chapterNum, verseNum ->
                    navController.navigate(Screen.Reader.createRoute(chapterNum, chapterNum, verseNum))
                },
                onNavigateToSearch = {
                    navController.navigate(Screen.Search.route)
                },
                onNavigateToBookmarks = {
                    navController.navigate(Screen.Bookmarks.route)
                }
            )
        }

        // Reading Canvas Screen
        composable(
            route = Screen.Reader.route,
            arguments = listOf(
                navArgument("parvaNumber") { type = NavType.IntType },
                navArgument("chapterNumber") { type = NavType.IntType },
                navArgument("initialVerse") {
                    type = NavType.IntType
                    defaultValue = -1
                }
            ),
            enterTransition = {
                slideIntoContainer(
                    AnimatedContentTransitionScope.SlideDirection.Left,
                    animationSpec = tween(400)
                ) + fadeIn(animationSpec = tween(400))
            },
            exitTransition = {
                slideOutOfContainer(
                    AnimatedContentTransitionScope.SlideDirection.Right,
                    animationSpec = tween(400)
                ) + fadeOut(animationSpec = tween(400))
            }
        ) { backStackEntry ->
            val parvaNumber = backStackEntry.arguments?.getInt("parvaNumber") ?: 1
            val chapterNumber = backStackEntry.arguments?.getInt("chapterNumber") ?: 1
            val initialVerse = backStackEntry.arguments?.getInt("initialVerse") ?: -1

            ReadingCanvasScreen(
                parvaNumber = parvaNumber,
                chapterNumber = chapterNumber,
                repository = repository,
                initialVerse = initialVerse,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToChapter = { pNum, chNum ->
                    navController.navigate(Screen.Reader.createRoute(pNum, chNum)) {
                        popUpTo(Screen.Reader.route) { inclusive = true }
                    }
                },
                onNavigateToSearch = {
                    navController.navigate(Screen.Search.route)
                },
                onNavigateToBookmarks = {
                    navController.navigate(Screen.Bookmarks.route)
                }
            )
        }

        // Multilingual Search Screen
        composable(
            route = Screen.Search.route,
            enterTransition = { fadeIn(animationSpec = tween(300)) },
            exitTransition = { fadeOut(animationSpec = tween(300)) }
        ) {
            SearchScreen(
                repository = repository,
                onNavigateBack = { navController.popBackStack() },
                onNavigateToShloka = { pNum, chNum, vNum ->
                    navController.navigate(Screen.Reader.createRoute(pNum, chNum, vNum))
                }
            )
        }

        // Bookmarks Screen
        composable(
            route = Screen.Bookmarks.route,
            enterTransition = { fadeIn(animationSpec = tween(300)) },
            exitTransition = { fadeOut(animationSpec = tween(300)) }
        ) {
            BookmarksScreen(
                repository = repository,
                onNavigateBack = { navController.popBackStack() },
                onNavigateToShlokaTag = { tag ->
                    val parts = tag.split(".")
                    if (parts.size >= 3) {
                        val p = parts[0].toIntOrNull() ?: 1
                        val c = parts[1].toIntOrNull() ?: 1
                        val v = parts[2].toIntOrNull() ?: -1
                        navController.navigate(Screen.Reader.createRoute(p, c, v))
                    } else if (parts.size >= 2) {
                        val p = parts[0].toIntOrNull() ?: 1
                        val c = parts[1].toIntOrNull() ?: 1
                        navController.navigate(Screen.Reader.createRoute(p, c))
                    }
                }
            )
        }
    }
}
