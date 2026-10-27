package com.apiforge.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun HomeScreen(
    backendConfigured: Boolean,
    onImportProject: () -> Unit,
    onOpenSettings: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
    ) {
        Text("API Forge AI", style = MaterialTheme.typography.headlineMedium)
        Text(
            "Turn a ZIP project into a working REST API.",
            style = MaterialTheme.typography.bodyMedium,
        )

        Spacer(Modifier.height(16.dp))

        Card(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    if (backendConfigured) "Backend connected" else "Backend not configured",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Spacer(Modifier.weight(1f))
                TextButton(onClick = onOpenSettings) { Text("Settings") }
            }
        }

        Spacer(Modifier.height(24.dp))

        Button(
            onClick = onImportProject,
            modifier = Modifier.fillMaxWidth(),
            enabled = backendConfigured,
        ) {
            Text("Upload ZIP & Analyze")
        }

        if (!backendConfigured) {
            Spacer(Modifier.height(8.dp))
            Text(
                "Set a backend URL and API key in Settings first.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.secondary,
            )
        }
    }
}
