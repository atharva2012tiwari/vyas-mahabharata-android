package com.vyas.mahabharata.ui.screens.reader

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.clickable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vyas.mahabharata.data.repository.MahabharataRepository
import com.vyas.mahabharata.domain.model.Chapter
import com.vyas.mahabharata.domain.model.Parva
import com.vyas.mahabharata.domain.model.Shloka
import com.vyas.mahabharata.ui.components.QuoteExportDialog
import com.vyas.mahabharata.ui.components.ShlokaCard
import com.vyas.mahabharata.ui.screens.explorer.ChapterSelectorSheet
import com.vyas.mahabharata.ui.theme.AccentSaffron
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch

/**
 * Material 3 Expressive Spacious Reading Canvas
 * 1.8x line-height typography, 45-65 CPL measure constraint (max 600dp), 120Hz smooth scrolling,
 * auto-hiding floating toolbar, dynamic language toggling, bookmarking, and quote export.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReadingCanvasScreen(
    parvaNumber: Int,
    chapterNumber: Int,
    repository: MahabharataRepository,
    onNavigateBack: () -> Unit,
    onNavigateToChapter: (parvaNumber: Int, chapterNumber: Int) -> Unit,
    onNavigateToSearch: () -> Unit,
    onNavigateToBookmarks: () -> Unit,
    initialVerse: Int = -1
) {
    val coroutineScope = rememberCoroutineScope()
    val listState = rememberLazyListState()

    // Observe data from repository
    val parva by repository.getParvaByNumber(parvaNumber).collectAsState(initial = null)
    val chapters by repository.getChaptersForParva(parvaNumber).collectAsState(initial = emptyList())
    val shlokas by repository.getShlokasForChapter(parvaNumber, chapterNumber).collectAsState(initial = emptyList())
    val readingHistory by repository.getReadingHistory(parvaNumber).collectAsState(initial = null)

    val currentChapter = chapters.find { it.chapterNumber == chapterNumber }

    // Language visibility state (Invariant: at least 1 language must remain active)
    var showSanskrit by remember { mutableStateOf(true) }
    var showIAST by remember { mutableStateOf(false) }
    var showHindi by remember { mutableStateOf(true) }
    var showEnglish by remember { mutableStateOf(true) }

    // Dynamic typography scale: standard (20sp/36sp) vs large (24sp/43.2sp)
    // Reader settings dialog state
    var showSettingsDialog by remember { mutableStateOf(false) }

    // Quote export dialog state
    var quoteExportShloka by remember { mutableStateOf<Shloka?>(null) }

    // Chapter selector bottom sheet state
    var showChapterSheet by remember { mutableStateOf(false) }

    // Restoration flag to prevent race conditions during initial scroll position resume
    var hasRestoredPosition by remember { mutableStateOf(false) }

    // Restore saved reading position or scroll to initial target verse on chapter open
    LaunchedEffect(shlokas, readingHistory, initialVerse) {
        if (!hasRestoredPosition && shlokas.isNotEmpty()) {
            if (initialVerse > 0) {
                val targetIndex = shlokas.indexOfFirst { it.verseNumber == initialVerse }
                if (targetIndex >= 0) {
                    val targetItem = targetIndex + 1
                    listState.scrollToItem(targetItem, 0)
                }
            } else {
                val history = readingHistory
                if (history != null && history.lastChapterNumber == chapterNumber) {
                    val targetIndex = shlokas.indexOfFirst { it.verseNumber == history.lastVerseNumber }
                    if (targetIndex >= 0) {
                        val targetItem = targetIndex + 1
                        listState.scrollToItem(targetItem, history.scrollOffset)
                    }
                }
            }
            hasRestoredPosition = true
        }
    }

    // Persist reading position smoothly on scroll
    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex to listState.firstVisibleItemScrollOffset }
            .distinctUntilChanged()
            .collect { (currentIndex, currentOffset) ->
                if (hasRestoredPosition && shlokas.isNotEmpty()) {
                    val shlokaIndex = (currentIndex - 1).coerceAtLeast(0)
                    if (shlokaIndex in shlokas.indices) {
                        val currentVerse = shlokas[shlokaIndex].verseNumber
                        repository.saveReadingPosition(
                            parvaNumber = parvaNumber,
                            chapterNumber = chapterNumber,
                            verseNumber = currentVerse,
                            scrollOffset = currentOffset
                        )
                    }
                }
            }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = parva?.nameSanskrit ?: "महाभारत",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Text(
                            text = "अध्याय $chapterNumber: ${currentChapter?.titleSanskrit ?: ""}",
                            style = MaterialTheme.typography.labelSmall,
                            color = AccentSaffron
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = MaterialTheme.colorScheme.onSurface
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { showSettingsDialog = true }) {
                        Icon(
                            imageVector = Icons.Filled.Settings,
                            contentDescription = "Reading Settings",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    IconButton(onClick = { showChapterSheet = true }) {
                        Icon(
                            imageVector = Icons.Filled.List,
                            contentDescription = "All Chapters",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    IconButton(onClick = onNavigateToSearch) {
                        Icon(
                            imageVector = Icons.Filled.Search,
                            contentDescription = "Search",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    IconButton(onClick = onNavigateToBookmarks) {
                        Icon(
                            imageVector = Icons.Filled.Bookmark,
                            contentDescription = "Bookmarks",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        },
        containerColor = MaterialTheme.colorScheme.surface
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding),
            contentAlignment = Alignment.TopCenter
        ) {
            // LazyColumn providing 120Hz smooth scrolling, centered with max 600dp constraint
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .widthIn(max = 600.dp) // 45–65 CPL Measure Constraint
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(top = 16.dp, bottom = 32.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Chapter Header
                item(key = "chapter_header") {
                    ChapterHeaderBanner(
                        parva = parva,
                        chapter = currentChapter,
                        chapterNumber = chapterNumber
                    )
                }

                // Shloka Cards
                items(
                    items = shlokas,
                    key = { it.id }
                ) { shloka ->
                    ShlokaCard(
                        shloka = shloka,
                        showSanskrit = showSanskrit,
                        showIAST = showIAST,
                        showHindi = showHindi,
                        showEnglish = showEnglish,
                        onBookmarkToggle = {
                            coroutineScope.launch {
                                repository.toggleBookmark(shloka.id)
                            }
                        },
                        onShareClick = {
                            quoteExportShloka = shloka
                        }
                    )
                }

                // Chapter Navigation Footer (Previous / Next Chapter)
                item(key = "chapter_navigation_footer") {
                    ChapterNavigationFooter(
                        parvaNumber = parvaNumber,
                        chapterNumber = chapterNumber,
                        totalChapters = chapters.size,
                        onSelectChapter = onNavigateToChapter
                    )
                }
            }
        }
    }

    // Reader Settings Dialog (Languages & Translations)
    if (showSettingsDialog) {
        ReaderSettingsDialog(
            showSanskrit = showSanskrit,
            showIAST = showIAST,
            showHindi = showHindi,
            showEnglish = showEnglish,
            onToggleSanskrit = {
                val active = listOf(!showSanskrit, showIAST, showHindi, showEnglish).count { it }
                if (active >= 1) showSanskrit = !showSanskrit
            },
            onToggleIAST = {
                val active = listOf(showSanskrit, !showIAST, showHindi, showEnglish).count { it }
                if (active >= 1) showIAST = !showIAST
            },
            onToggleHindi = {
                val active = listOf(showSanskrit, showIAST, !showHindi, showEnglish).count { it }
                if (active >= 1) showHindi = !showHindi
            },
            onToggleEnglish = {
                val active = listOf(showSanskrit, showIAST, showHindi, !showEnglish).count { it }
                if (active >= 1) showEnglish = !showEnglish
            },
            onDismissRequest = { showSettingsDialog = false }
        )
    }

    // High-Res Quote Export Dialog
    quoteExportShloka?.let { shloka ->
        QuoteExportDialog(
            shloka = shloka,
            parvaName = parva?.nameEnglish ?: "Mahabharata",
            onDismissRequest = { quoteExportShloka = null }
        )
    }

    // Chapter Selector Modal Sheet
    if (showChapterSheet && parva != null) {
        ChapterSelectorSheet(
            parva = parva!!,
            chapters = chapters,
            onSelectChapter = { pNum, chNum ->
                showChapterSheet = false
                onNavigateToChapter(pNum, chNum)
            },
            onDismissRequest = { showChapterSheet = false }
        )
    }
}

/**
 * Clean Reading Settings Dialog for toggling script and translations.
 */
@Composable
private fun ReaderSettingsDialog(
    showSanskrit: Boolean,
    showIAST: Boolean,
    showHindi: Boolean,
    showEnglish: Boolean,
    onToggleSanskrit: () -> Unit,
    onToggleIAST: () -> Unit,
    onToggleHindi: () -> Unit,
    onToggleEnglish: () -> Unit,
    onDismissRequest: () -> Unit
) {
    val activeCount = listOf(showSanskrit, showIAST, showHindi, showEnglish).count { it }

    androidx.compose.material3.AlertDialog(
        onDismissRequest = onDismissRequest,
        shape = RoundedCornerShape(24.dp),
        title = {
            Text(
                text = "पठन विन्यास • Reading Settings",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    text = "अनुवाद एवं भाषा प्रदर्शन (Languages & Translations):",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(4.dp))

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(enabled = activeCount > 1 || !showSanskrit, onClick = onToggleSanskrit)
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Checkbox(
                        checked = showSanskrit,
                        onCheckedChange = { onToggleSanskrit() },
                        enabled = activeCount > 1 || !showSanskrit
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("संस्कृत श्लोक (Devanagari)", style = MaterialTheme.typography.bodyMedium)
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(enabled = activeCount > 1 || !showIAST, onClick = onToggleIAST)
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Checkbox(
                        checked = showIAST,
                        onCheckedChange = { onToggleIAST() },
                        enabled = activeCount > 1 || !showIAST
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("IAST (Roman Script)", style = MaterialTheme.typography.bodyMedium)
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(enabled = activeCount > 1 || !showHindi, onClick = onToggleHindi)
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Checkbox(
                        checked = showHindi,
                        onCheckedChange = { onToggleHindi() },
                        enabled = activeCount > 1 || !showHindi
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("हिन्दी अनुवाद (Hindi Meaning)", style = MaterialTheme.typography.bodyMedium)
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(enabled = activeCount > 1 || !showEnglish, onClick = onToggleEnglish)
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Checkbox(
                        checked = showEnglish,
                        onCheckedChange = { onToggleEnglish() },
                        enabled = activeCount > 1 || !showEnglish
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("English Translation", style = MaterialTheme.typography.bodyMedium)
                }
            }
        },
        confirmButton = {
            androidx.compose.material3.TextButton(onClick = onDismissRequest) {
                Text("सम्पूर्ण • Done")
            }
        }
    )
}

@Composable
private fun ChapterHeaderBanner(
    parva: Parva?,
    chapter: Chapter?,
    chapterNumber: Int
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "॥ श्रीपरमात्मने नमः ॥",
            style = MaterialTheme.typography.labelMedium,
            color = AccentSaffron,
            letterSpacing = 2.sp
        )

        Spacer(modifier = Modifier.height(10.dp))

        Text(
            text = "अध्याय $chapterNumber",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface
        )

        if (chapter != null && chapter.titleSanskrit.isNotBlank()) {
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = chapter.titleSanskrit,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.primary,
                textAlign = TextAlign.Center
            )
        }

        if (chapter != null && chapter.titleEnglish.isNotBlank()) {
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = chapter.titleEnglish,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
private fun ChapterNavigationFooter(
    parvaNumber: Int,
    chapterNumber: Int,
    totalChapters: Int,
    onSelectChapter: (parvaNumber: Int, chapterNumber: Int) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 24.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        if (chapterNumber > 1) {
            OutlinedButton(
                onClick = { onSelectChapter(parvaNumber, chapterNumber - 1) },
                shape = RoundedCornerShape(20.dp)
            ) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = null, modifier = Modifier.size(16.dp))
                Spacer(modifier = Modifier.width(6.dp))
                Text("अध्याय ${chapterNumber - 1}")
            }
        } else {
            Spacer(modifier = Modifier.width(1.dp))
        }

        if (totalChapters > 0 && chapterNumber < totalChapters) {
            FilledTonalButton(
                onClick = { onSelectChapter(parvaNumber, chapterNumber + 1) },
                shape = RoundedCornerShape(20.dp)
            ) {
                Text("अध्याय ${chapterNumber + 1}")
                Spacer(modifier = Modifier.width(6.dp))
                Icon(Icons.AutoMirrored.Filled.ArrowForward, contentDescription = null, modifier = Modifier.size(16.dp))
            }
        }
    }
}
