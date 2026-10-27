package com.apiforge.ai.viewmodel

import android.content.Context
import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.apiforge.ai.data.AnalysisResultDto
import com.apiforge.ai.data.NetworkModule
import com.apiforge.ai.data.ProjectCreateRequest
import com.apiforge.ai.data.ProjectDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.FileOutputStream

sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Error(val message: String) : UiState()
    data class Analyzed(val result: AnalysisResultDto) : UiState()
}

/**
 * Minimal end-to-end flow: create a project, upload the picked ZIP,
 * analyze it, and surface the real backend report. No step here is
 * simulated -- each stage only advances after the backend responds.
 */
class ProjectViewModel(
    private val backendUrl: String,
    private val apiKey: String,
) : ViewModel() {

    private val api = NetworkModule.create(backendUrl)

    private val _state = MutableStateFlow<UiState>(UiState.Idle)
    val state: StateFlow<UiState> = _state.asStateFlow()

    private val _currentProject = MutableStateFlow<ProjectDto?>(null)
    val currentProject: StateFlow<ProjectDto?> = _currentProject.asStateFlow()

    fun importAndAnalyze(context: Context, uri: Uri, projectName: String) {
        viewModelScope.launch {
            _state.value = UiState.Loading
            try {
                val createResponse = api.createProject(apiKey, ProjectCreateRequest(projectName))
                if (!createResponse.isSuccessful || createResponse.body() == null) {
                    _state.value = UiState.Error(
                        "Could not create project (HTTP ${createResponse.code()})."
                    )
                    return@launch
                }
                val project = createResponse.body()!!
                _currentProject.value = project

                val tempFile = copyUriToTempFile(context, uri)
                val requestBody = tempFile.asRequestBody("application/zip".toMediaTypeOrNull())
                val part = MultipartBody.Part.createFormData(
                    "file", tempFile.name, requestBody
                )

                val uploadResponse = api.uploadZip(apiKey, project.id, part)
                tempFile.delete()
                if (!uploadResponse.isSuccessful) {
                    _state.value = UiState.Error(
                        "Upload failed (HTTP ${uploadResponse.code()}): " +
                            "${uploadResponse.errorBody()?.string()}"
                    )
                    return@launch
                }

                val analyzeResponse = api.analyzeProject(apiKey, project.id)
                if (!analyzeResponse.isSuccessful || analyzeResponse.body() == null) {
                    _state.value = UiState.Error(
                        "Analysis failed (HTTP ${analyzeResponse.code()})."
                    )
                    return@launch
                }

                _state.value = UiState.Analyzed(analyzeResponse.body()!!)
            } catch (e: Exception) {
                _state.value = UiState.Error(e.message ?: "Unknown network error.")
            }
        }
    }

    private fun copyUriToTempFile(context: Context, uri: Uri): File {
        val tempFile = File.createTempFile("upload_", ".zip", context.cacheDir)
        context.contentResolver.openInputStream(uri).use { input ->
            FileOutputStream(tempFile).use { output ->
                input?.copyTo(output)
            }
        }
        return tempFile
    }
}
