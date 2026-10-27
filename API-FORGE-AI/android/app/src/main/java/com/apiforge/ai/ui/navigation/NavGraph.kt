package com.apiforge.ai.ui.navigation

import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.apiforge.ai.ui.screens.AnalysisScreen
import com.apiforge.ai.ui.screens.HomeScreen
import com.apiforge.ai.ui.screens.ProjectImportScreen
import com.apiforge.ai.ui.screens.SettingsScreen
import com.apiforge.ai.viewmodel.ProjectViewModel

private object Routes {
    const val HOME = "home"
    const val IMPORT = "import"
    const val ANALYSIS = "analysis"
    const val SETTINGS = "settings"
}

/**
 * Settings are kept in memory for this MVP slice (reset on app
 * restart). androidx.datastore is already a dependency for when
 * persistent settings storage is added -- see docs/ANDROID.md.
 */
@Composable
fun ApiForgeNavGraph() {
    val navController: NavHostController = rememberNavController()
    val context = LocalContext.current

    var backendUrl by remember { mutableStateOf("http://10.0.2.2:8000") }
    var apiKey by remember { mutableStateOf("") }
    var viewModel by remember { mutableStateOf<ProjectViewModel?>(null) }

    NavHost(navController = navController, startDestination = Routes.HOME) {
        composable(Routes.HOME) {
            HomeScreen(
                backendConfigured = backendUrl.isNotBlank() && apiKey.isNotBlank(),
                onImportProject = { navController.navigate(Routes.IMPORT) },
                onOpenSettings = { navController.navigate(Routes.SETTINGS) },
            )
        }
        composable(Routes.IMPORT) {
            ProjectImportScreen(
                onZipPicked = { uri, name ->
                    val vm = ProjectViewModel(backendUrl, apiKey)
                    viewModel = vm
                    vm.importAndAnalyze(context, uri, name)
                    navController.navigate(Routes.ANALYSIS)
                },
            )
        }
        composable(Routes.ANALYSIS) {
            val activeViewModel = viewModel
            if (activeViewModel == null) {
                Text("No project import in progress.")
            } else {
                val state by activeViewModel.state.collectAsState()
                AnalysisScreen(state = state)
            }
        }
        composable(Routes.SETTINGS) {
            SettingsScreen(
                initialBackendUrl = backendUrl,
                initialApiKey = apiKey,
                onSave = { url, key ->
                    backendUrl = url
                    apiKey = key
                    navController.popBackStack()
                },
            )
        }
    }
}
