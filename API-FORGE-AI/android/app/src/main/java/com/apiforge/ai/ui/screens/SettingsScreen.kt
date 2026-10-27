package com.apiforge.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun SettingsScreen(
    initialBackendUrl: String,
    initialApiKey: String,
    onSave: (String, String) -> Unit,
) {
    var backendUrl by remember { mutableStateOf(initialBackendUrl) }
    var apiKey by remember { mutableStateOf(initialApiKey) }

    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        Text("Settings", style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(16.dp))

        OutlinedTextField(
            value = backendUrl,
            onValueChange = { backendUrl = it },
            label = { Text("Backend URL") },
            placeholder = { Text("http://10.0.2.2:8000 (emulator) or https://your-backend") },
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(Modifier.height(12.dp))
        OutlinedTextField(
            value = apiKey,
            onValueChange = { apiKey = it },
            label = { Text("API key (X-API-Key)") },
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(Modifier.height(24.dp))
        Button(onClick = { onSave(backendUrl, apiKey) }, modifier = Modifier.fillMaxWidth()) {
            Text("Save")
        }
    }
}
