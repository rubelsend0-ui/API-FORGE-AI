package com.apiforge.ai.ui.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

/** Native SAF file picker restricted to ZIP archives -- no custom file browser. */
@Composable
fun ProjectImportScreen(
    onZipPicked: (Uri, String) -> Unit,
) {
    var pickedUri by remember { mutableStateOf<Uri?>(null) }
    var projectName by remember { mutableStateOf("") }

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument(),
    ) { uri -> pickedUri = uri }

    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        Text("Import Project", style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(16.dp))

        OutlinedTextField(
            value = projectName,
            onValueChange = { projectName = it },
            label = { Text("Project name") },
            modifier = Modifier.fillMaxWidth(),
        )

        Spacer(Modifier.height(16.dp))

        OutlinedButton(
            onClick = { launcher.launch(arrayOf("application/zip")) },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(pickedUri?.lastPathSegment ?: "Choose ZIP file")
        }

        Spacer(Modifier.height(24.dp))

        Button(
            onClick = { pickedUri?.let { onZipPicked(it, projectName.ifBlank { "Untitled project" }) } },
            enabled = pickedUri != null,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("Upload & Analyze")
        }
    }
}
