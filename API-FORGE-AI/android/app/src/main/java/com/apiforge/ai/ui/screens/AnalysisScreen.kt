package com.apiforge.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.apiforge.ai.viewmodel.UiState

@Composable
fun AnalysisScreen(state: UiState) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Text("Analysis", style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(16.dp))

        when (state) {
            is UiState.Idle -> Text("Import a project to see its analysis here.")
            is UiState.Loading -> Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                CircularProgressIndicator(modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(12.dp))
                Text("Uploading and analyzing…")
            }
            is UiState.Error -> Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
            ) {
                Text(state.message, modifier = Modifier.padding(16.dp))
            }
            is UiState.Analyzed -> {
                val report = state.result.report
                InfoRow("Valid archive", report["valid"].toString())
                InfoRow("Language", report["detected_language"]?.toString() ?: "Unknown")
                InfoRow("Framework", report["detected_framework"]?.toString() ?: "Unknown")
                InfoRow("Project type", report["project_type"]?.toString() ?: "Unknown")
                InfoRow("Has existing API", report["has_existing_api"].toString())
                InfoRow("File count", report["file_count"].toString())

                @Suppress("UNCHECKED_CAST")
                val warnings = report["warnings"] as? List<String> ?: emptyList()
                if (warnings.isNotEmpty()) {
                    Spacer(Modifier.height(12.dp))
                    Text("Warnings", style = MaterialTheme.typography.titleSmall)
                    warnings.forEach { Text("• $it") }
                }
            }
        }
    }
}

@Composable
private fun InfoRow(label: String, value: String) {
    Row(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Text(label, modifier = Modifier.weight(1f), style = MaterialTheme.typography.bodyMedium)
        Text(value, style = MaterialTheme.typography.bodyMedium)
    }
}
