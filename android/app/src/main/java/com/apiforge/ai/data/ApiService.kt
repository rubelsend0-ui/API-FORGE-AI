package com.apiforge.ai.data

import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path

/**
 * Matches backend/app/api/health.py and backend/app/api/projects.py.
 * Every call requires the shared X-API-Key header configured in Settings.
 */
interface ApiService {

    @GET("/health")
    suspend fun health(): Response<HealthDto>

    @POST("/api/v1/projects")
    suspend fun createProject(
        @Header("X-API-Key") apiKey: String,
        @Body body: ProjectCreateRequest,
    ): Response<ProjectDto>

    @GET("/api/v1/projects")
    suspend fun listProjects(
        @Header("X-API-Key") apiKey: String,
    ): Response<List<ProjectDto>>

    @Multipart
    @POST("/api/v1/projects/{id}/upload")
    suspend fun uploadZip(
        @Header("X-API-Key") apiKey: String,
        @Path("id") projectId: String,
        @Part file: MultipartBody.Part,
    ): Response<UploadResultDto>

    @POST("/api/v1/projects/{id}/analyze")
    suspend fun analyzeProject(
        @Header("X-API-Key") apiKey: String,
        @Path("id") projectId: String,
    ): Response<AnalysisResultDto>
}
