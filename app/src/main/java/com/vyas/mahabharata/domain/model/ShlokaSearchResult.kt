package com.vyas.mahabharata.domain.model

/**
 * Domain model representing a matched search result from SQLite FTS5 search.
 */
data class ShlokaSearchResult(
    val shloka: Shloka,
    val matchSnippet: String? = null,
    val matchedField: String? = null
)
