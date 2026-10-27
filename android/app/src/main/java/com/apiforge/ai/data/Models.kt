package com.apiforge.ai.data

import com.google.gson.annotations.SerializedName

// These mirror backend/app/schemas.py exactly. Keep in sync by hand
// until a shared schema generator is added.

data class ProjectCreateRequest(
    val name: String,
)

data class ProjectDto(
    val id: String,
    val name: String,
    val owner: String,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("zip_filename") val zipFilename: String?,
    @SerializedName("zip_size_bytes") val zipSizeBytes: Long?,
    @SerializedName("analysis_report") val analysisReport: Map<String, Any?>?,
    @SerializedName("analyzed_at") val analyzedAt: String?,
)

data class UploadResultDto(
    val project: ProjectDto,
    val message: String,
)

data class AnalysisResultDto(
    val project: ProjectDto,
    val report: Map<String, Any?>,
)

data class HealthDto(
    val status: String,
    val service: String,
    val environment: String,
)
