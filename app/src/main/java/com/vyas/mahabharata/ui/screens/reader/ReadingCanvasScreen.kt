package com.vyas.mahabharata.ui.screens.reader

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateContentSize
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.spring
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Translate
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
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
import androidx.compose.ui.draw.shadow
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
import com.vyas.mahabharata.ui.theme.AccentGold
import com.vyas.mahabharata.ui.theme.AccentPeacock
import com.vyas.mahabharata.ui.theme.AccentSaffron
import com.vyas.mahabharata.ui.theme.ExpressiveAsymmetricBadge
import com.vyas.mahabharata.ui.theme.ExpressivePillShape
import com.vyas.mahabharata.ui.theme.ExpressiveWisdomContainer
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.launch

/**
 * Pure Material 3 Expressive Bhagavad Gita Reading Canvas
 * Continuous editorial typography without boxy cards, 1.8x line-height Devanagari,
 * collapsible wisdom overview accordion, and tactile floating reader toolbar.
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

    // Dialog & bottom sheet states
    var showSettingsDialog by remember { mutableStateOf(false) }
    var quoteExportShloka by remember { mutableStateOf<Shloka?>(null) }
    var showChapterSheet by remember { mutableStateOf(false) }

    // Restoration flag to prevent scroll bounce on open
    var hasRestoredPosition by remember { mutableStateOf(false) }

    // Floating toolbar auto-hide state on scroll
    var isFloatingBarVisible by remember { mutableStateOf(true) }
    var previousIndex by remember { mutableIntStateOf(0) }
    var previousScrollOffset by remember { mutableIntStateOf(0) }

    // Restore saved reading position or scroll to initial target verse
    LaunchedEffect(shlokas, readingHistory, initialVerse) {
        if (!hasRestoredPosition && shlokas.isNotEmpty()) {
            if (initialVerse > 0) {
                val targetIndex = shlokas.indexOfFirst { it.verseNumber == initialVerse }
                if (targetIndex >= 0) {
                    val targetItem = targetIndex + 2 // +2 accounts for chapter header and wisdom accordion
                    listState.scrollToItem(targetItem, 0)
                }
            } else {
                val history = readingHistory
                if (history != null && history.lastChapterNumber == chapterNumber) {
                    val targetIndex = shlokas.indexOfFirst { it.verseNumber == history.lastVerseNumber }
                    if (targetIndex >= 0) {
                        val targetItem = targetIndex + 2
                        listState.scrollToItem(targetItem, history.scrollOffset)
                    }
                }
            }
            hasRestoredPosition = true
        }
    }

    // Persist reading position and calculate dynamic toolbar visibility
    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex to listState.firstVisibleItemScrollOffset }
            .distinctUntilChanged()
            .collect { (currentIndex, currentOffset) ->
                // Save position
                if (hasRestoredPosition && shlokas.isNotEmpty()) {
                    val shlokaIndex = (currentIndex - 2).coerceAtLeast(0)
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

                // Smooth toolbar auto-hide on downward scroll
                val isScrollingDown = when {
                    currentIndex > previousIndex -> true
                    currentIndex < previousIndex -> false
                    else -> currentOffset > previousScrollOffset + 12
                }
                val isScrollingUp = when {
                    currentIndex < previousIndex -> true
                    currentIndex > previousIndex -> false
                    else -> currentOffset < previousScrollOffset - 12
                }

                if (isScrollingDown && isFloatingBarVisible && currentIndex > 0) {
                    isFloatingBarVisible = false
                } else if (isScrollingUp && !isFloatingBarVisible) {
                    isFloatingBarVisible = true
                }

                previousIndex = currentIndex
                previousScrollOffset = currentOffset
            }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "श्रीमद्भगवद्गीता",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Text(
                            text = "अध्याय $chapterNumber : ${currentChapter?.titleSanskrit ?: parva?.nameSanskrit ?: ""}",
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
                            imageVector = Icons.Filled.Translate,
                            contentDescription = "Language Settings",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    IconButton(onClick = onNavigateToSearch) {
                        Icon(
                            imageVector = Icons.Filled.Search,
                            contentDescription = "Search Verses",
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
            // LazyColumn providing 120Hz smooth scrolling, centered with max 640dp constraint
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .widthIn(max = 640.dp)
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp),
                contentPadding = PaddingValues(top = 16.dp, bottom = 120.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // 1. CHAPTER HEADER BANNER
                item(key = "chapter_header") {
                    ChapterHeaderBanner(
                        chapter = currentChapter,
                        parva = parva,
                        chapterNumber = chapterNumber,
                        shlokaCount = shlokas.size
                    )
                }

                // 2. EXPANDABLE WISDOM ACCORDION (Chapter Overview & Context)
                item(key = "chapter_wisdom_accordion") {
                    ChapterWisdomAccordion(
                        summaryHindi = parva?.summaryHindi,
                        summaryEnglish = parva?.summaryEnglish
                    )
                }

                // 3. EDITORIAL SHLOKA PASSAGES (Expansive, clutter-free reading canvas)
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

                // 4. CHAPTER NAVIGATION FOOTER (Previous / Next Chapter Large CTAs)
                item(key = "chapter_navigation_footer") {
                    ChapterNavigationFooter(
                        chapterNumber = chapterNumber,
                        totalChapters = 18,
                        onSelectChapter = { nextChapter ->
                            onNavigateToChapter(nextChapter, nextChapter)
                        }
                    )
                }
            }

            // 5. TACTILE FLOATING BOTTOM PILL BAR
            AnimatedVisibility(
                visible = isFloatingBarVisible,
                enter = slideInVertically(
                    initialOffsetY = { it * 2 },
                    animationSpec = spring(stiffness = Spring.StiffnessMediumLow)
                ) + fadeIn(),
                exit = slideOutVertically(
                    targetOffsetY = { it * 2 },
                    animationSpec = spring(stiffness = Spring.StiffnessMediumLow)
                ) + fadeOut(),
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 20.dp)
            ) {
                FloatingReaderBar(
                    chapterNumber = chapterNumber,
                    totalChapters = 18,
                    onOpenSettings = { showSettingsDialog = true },
                    onOpenChapterSheet = { showChapterSheet = true },
                    onPreviousChapter = {
                        if (chapterNumber > 1) {
                            onNavigateToChapter(chapterNumber - 1, chapterNumber - 1)
                        }
                    },
                    onNextChapter = {
                        if (chapterNumber < 18) {
                            onNavigateToChapter(chapterNumber + 1, chapterNumber + 1)
                        }
                    }
                )
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
            parvaName = "श्रीमद्भगवद्गीता",
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
 * Expressive Collapsible Wisdom Accordion (Chapter Overview)
 */
@Composable
private fun ChapterWisdomAccordion(
    summaryHindi: String?,
    summaryEnglish: String?
) {
    if (summaryHindi.isNullOrBlank() && summaryEnglish.isNullOrBlank()) return

    var isExpanded by remember { mutableStateOf(false) }

    Card(
        shape = ExpressiveWisdomContainer,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainerLow
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 12.dp)
            .clip(ExpressiveWisdomContainer)
            .clickable { isExpanded = !isExpanded }
            .animateContentSize(
                animationSpec = spring(
                    dampingRatio = Spring.DampingRatioLowBouncy,
                    stiffness = Spring.StiffnessMediumLow
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp, vertical = 16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(34.dp)
                            .clip(CircleShape)
                            .background(AccentSaffron.copy(alpha = 0.15f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "ॐ",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            color = AccentSaffron
                        )
                    }

                    Spacer(modifier = Modifier.width(12.dp))

                    Column {
                        Text(
                            text = "अध्याय परिचय • Overview",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        if (!isExpanded) {
                            Text(
                                text = "अध्याय का सारांश पढ़ने के लिए स्पर्श करें",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }

                Icon(
                    imageVector = if (isExpanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                    contentDescription = if (isExpanded) "Collapse" else "Expand",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            AnimatedVisibility(
                visible = isExpanded,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column(modifier = Modifier.padding(top = 16.dp)) {
                    HorizontalDivider(
                        thickness = 0.5.dp,
                        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.3f)
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    if (!summaryHindi.isNullOrBlank()) {
                        Text(
                            text = summaryHindi,
                            style = MaterialTheme.typography.bodyMedium.copy(lineHeight = 26.sp),
                            color = MaterialTheme.colorScheme.onSurface
                        )
                    }

                    if (!summaryEnglish.isNullOrBlank()) {
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            text = summaryEnglish,
                            style = MaterialTheme.typography.bodySmall.copy(lineHeight = 22.sp),
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

/**
 * Tactile Floating Reader Bottom Pill Bar
 */
@Composable
private fun FloatingReaderBar(
    chapterNumber: Int,
    totalChapters: Int,
    onOpenSettings: () -> Unit,
    onOpenChapterSheet: () -> Unit,
    onPreviousChapter: () -> Unit,
    onNextChapter: () -> Unit
) {
    Surface(
        shape = ExpressivePillShape,
        color = MaterialTheme.colorScheme.surfaceContainerHigh,
        tonalElevation = 6.dp,
        shadowElevation = 8.dp,
        modifier = Modifier
            .shadow(10.dp, ExpressivePillShape)
            .clip(ExpressivePillShape)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            // Previous Chapter quick step
            IconButton(
                onClick = onPreviousChapter,
                enabled = chapterNumber > 1,
                modifier = Modifier.size(44.dp)
            ) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Previous Chapter",
                    tint = if (chapterNumber > 1) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f),
                    modifier = Modifier.size(20.dp)
                )
            }

            // Chapter Selector Pill
            Button(
                onClick = onOpenChapterSheet,
                shape = ExpressivePillShape,
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    contentColor = MaterialTheme.colorScheme.onPrimaryContainer
                ),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                modifier = Modifier.height(44.dp)
            ) {
                Icon(
                    imageVector = Icons.Filled.List,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "अध्याय $chapterNumber",
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold
                )
            }

            // Language Settings Pill
            IconButton(
                onClick = onOpenSettings,
                modifier = Modifier.size(44.dp)
            ) {
                Icon(
                    imageVector = Icons.Filled.Translate,
                    contentDescription = "Languages",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(20.dp)
                )
            }

            // Next Chapter quick step
            IconButton(
                onClick = onNextChapter,
                enabled = chapterNumber < totalChapters,
                modifier = Modifier.size(44.dp)
            ) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                    contentDescription = "Next Chapter",
                    tint = if (chapterNumber < totalChapters) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f),
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}

/**
 * Editorial Chapter Header Banner
 */
@Composable
private fun ChapterHeaderBanner(
    chapter: Chapter?,
    parva: Parva?,
    chapterNumber: Int,
    shlokaCount: Int
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 12.dp, bottom = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "॥ श्रीपरमात्मने नमः ॥",
            style = MaterialTheme.typography.labelMedium,
            color = AccentSaffron,
            letterSpacing = 3.sp,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(12.dp))

        Text(
            text = "अध्याय $chapterNumber",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.ExtraBold,
            color = MaterialTheme.colorScheme.onSurface
        )

        val titleSanskrit = chapter?.titleSanskrit ?: parva?.nameSanskrit ?: ""
        if (titleSanskrit.isNotBlank()) {
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = titleSanskrit,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
                textAlign = TextAlign.Center
            )
        }

        val titleEnglish = chapter?.titleEnglish ?: parva?.nameEnglish ?: ""
        if (titleEnglish.isNotBlank()) {
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "$titleEnglish • $shlokaCount श्लोक",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
        }
    }
}

/**
 * Chapter Navigation Footer with large 54dp Expressive Pill CTAs
 */
@Composable
private fun ChapterNavigationFooter(
    chapterNumber: Int,
    totalChapters: Int,
    onSelectChapter: (Int) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 32.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        if (chapterNumber > 1) {
            OutlinedButton(
                onClick = { onSelectChapter(chapterNumber - 1) },
                shape = ExpressivePillShape,
                modifier = Modifier
                    .weight(1f)
                    .height(52.dp)
            ) {
                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text("अध्याय ${chapterNumber - 1}", fontWeight = FontWeight.Bold)
            }
        } else {
            Spacer(modifier = Modifier.weight(1f))
        }

        Spacer(modifier = Modifier.width(16.dp))

        if (chapterNumber < totalChapters) {
            Button(
                onClick = { onSelectChapter(chapterNumber + 1) },
                shape = ExpressivePillShape,
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    contentColor = MaterialTheme.colorScheme.onPrimary
                ),
                modifier = Modifier
                    .weight(1f)
                    .height(52.dp)
            ) {
                Text("अध्याय ${chapterNumber + 1}", fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.width(8.dp))
                Icon(Icons.AutoMirrored.Filled.ArrowForward, contentDescription = null, modifier = Modifier.size(18.dp))
            }
        } else {
            Spacer(modifier = Modifier.weight(1f))
        }
    }
}

/**
 * Clean Reading Settings Dialog
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
        shape = RoundedCornerShape(28.dp),
        title = {
            Text(
                text = "पठन विन्यास • Reading Settings",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    text = "अनुवाद एवं भाषाएं (Languages & Translations):",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(6.dp))

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(enabled = activeCount > 1 || !showSanskrit, onClick = onToggleSanskrit)
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = showSanskrit,
                        onCheckedChange = { onToggleSanskrit() },
                        enabled = activeCount > 1 || !showSanskrit
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("संस्कृत श्लोक (Devanagari)", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(enabled = activeCount > 1 || !showIAST, onClick = onToggleIAST)
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
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
                    Checkbox(
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
                    Checkbox(
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
            Button(
                onClick = onDismissRequest,
                shape = ExpressivePillShape
            ) {
                Text("पूर्ण • Done")
            }
        }
    )
}
