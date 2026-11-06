package com.vyas.mahabharata.ui.screens.explorer

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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vyas.mahabharata.data.repository.MahabharataRepository
import com.vyas.mahabharata.domain.model.Parva
import com.vyas.mahabharata.domain.model.ReadingHistory
import com.vyas.mahabharata.ui.theme.AccentGold
import com.vyas.mahabharata.ui.theme.AccentPeacock
import com.vyas.mahabharata.ui.theme.AccentSaffron
import com.vyas.mahabharata.ui.theme.ExpressiveAsymmetricBadge
import com.vyas.mahabharata.ui.theme.ExpressiveAsymmetricCard
import com.vyas.mahabharata.ui.theme.ExpressivePillShape

/**
 * Pure Material 3 Expressive Bhagavad Gita Home Screen
 * Features Hero Reading Resume, Vivid Asymmetric Badges, and 18 Chapters with generous screen estate.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ParvaExplorerScreen(
    repository: MahabharataRepository,
    onNavigateToChapter: (chapterNumber: Int, verseNumber: Int) -> Unit,
    onNavigateToSearch: () -> Unit,
    onNavigateToBookmarks: () -> Unit
) {
    val chapters by repository.getAllParvas().collectAsState(initial = emptyList())
    val allHistory by repository.getAllReadingHistory().collectAsState(initial = emptyList())
    val historyMap = remember(allHistory) { allHistory.associateBy { it.parvaNumber } }

    // Identify last active chapter for Hero Resume
    val lastHistory = allHistory.maxByOrNull { it.updatedAt }
    val resumeChapterNumber = lastHistory?.parvaNumber ?: 1
    val resumeVerseNumber = lastHistory?.lastVerseNumber ?: 1
    val resumeChapter = chapters.find { it.number == resumeChapterNumber } ?: chapters.firstOrNull()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "श्रीमद्भगवद्गीता",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Text(
                            text = "18 Chapters • 700 Verses",
                            style = MaterialTheme.typography.labelSmall,
                            color = AccentSaffron
                        )
                    }
                },
                actions = {
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
            LazyColumn(
                modifier = Modifier
                    .widthIn(max = 640.dp)
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp),
                contentPadding = PaddingValues(top = 16.dp, bottom = 48.dp),
                verticalArrangement = Arrangement.spacedBy(18.dp)
            ) {
                // 1. HERO RESUME SECTION (Vivid Asymmetrical Card)
                item(key = "gita_hero_resume") {
                    GitaHeroResumeSection(
                        chapter = resumeChapter,
                        lastHistory = lastHistory,
                        onContinueClick = {
                            onNavigateToChapter(resumeChapterNumber, resumeVerseNumber)
                        }
                    )
                }

                // 2. SECTION HEADER
                item(key = "gita_section_header") {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 8.dp, bottom = 4.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "अध्याय सूची • All 18 Chapters",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Text(
                            text = "७०० श्लोक",
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.SemiBold,
                            color = AccentPeacock
                        )
                    }
                }

                // 3. 18 CHAPTER CARDS (Material 3 Expressive, Spacious & Vivid)
                items(chapters, key = { it.id }) { chapter ->
                    val history = historyMap[chapter.number]
                    GitaChapterCard(
                        chapter = chapter,
                        readingHistory = history,
                        onClick = {
                            val startVerse = history?.lastVerseNumber ?: 1
                            onNavigateToChapter(chapter.number, startVerse)
                        }
                    )
                }
            }
        }
    }
}

/**
 * Vivid Hero Section highlighting current reading journey with large 54dp CTA button.
 */
@Composable
private fun GitaHeroResumeSection(
    chapter: Parva?,
    lastHistory: ReadingHistory?,
    onContinueClick: () -> Unit
) {
    Card(
        shape = ExpressiveAsymmetricCard,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainerHigh
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .clip(ExpressivePillShape)
                        .background(AccentSaffron.copy(alpha = 0.15f))
                        .padding(horizontal = 14.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = if (lastHistory != null) "पठन जारी रखें • Current Reading" else "दैनिक गीता • Begin Gita",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = AccentSaffron
                    )
                }

                Text(
                    text = "ॐ",
                    fontSize = 24.sp,
                    color = AccentGold,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(14.dp))

            val titleSanskrit = chapter?.nameSanskrit ?: "अर्जुनविषादयोगः"
            val titleEnglish = chapter?.nameEnglish ?: "The Dilemma of Arjuna"
            val chapterNum = chapter?.number ?: 1
            val verseNum = lastHistory?.lastVerseNumber ?: 1

            Text(
                text = "अध्याय $chapterNum : $titleSanskrit",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )

            Text(
                text = "$titleEnglish — श्लोक $verseNum",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(20.dp))

            // Large 54dp Expressive Pill Action Button
            Button(
                onClick = onContinueClick,
                shape = ExpressivePillShape,
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    contentColor = MaterialTheme.colorScheme.onPrimary
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(54.dp)
            ) {
                Icon(
                    imageVector = Icons.Filled.PlayArrow,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = if (lastHistory != null) "आगे पढ़ें • Continue Chapter $chapterNum" else "अध्याय १ आरम्भ करें • Start Chapter 1",
                    style = MaterialTheme.typography.labelLarge.copy(fontSize = 16.sp),
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

/**
 * Spacious M3 Expressive Chapter Card with vivid asymmetric number badge and generous touch target.
 */
@Composable
private fun GitaChapterCard(
    chapter: Parva,
    readingHistory: ReadingHistory?,
    onClick: () -> Unit
) {
    Card(
        shape = ExpressiveAsymmetricBadge,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainerLow
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp, pressedElevation = 3.dp),
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp, vertical = 18.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Vivid Asymmetrical Number Badge
            val formattedNumber = if (chapter.number < 10) "0${chapter.number}" else "${chapter.number}"
            Box(
                modifier = Modifier
                    .size(54.dp)
                    .clip(ExpressiveAsymmetricBadge)
                    .background(
                        if (chapter.number % 2 == 1) AccentSaffron.copy(alpha = 0.15f)
                        else AccentPeacock.copy(alpha = 0.15f)
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = formattedNumber,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.ExtraBold,
                    color = if (chapter.number % 2 == 1) AccentSaffron else AccentPeacock
                )
            }

            Spacer(modifier = Modifier.width(18.dp))

            // Titles & Shloka Count
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = chapter.nameSanskrit,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = chapter.nameEnglish,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(6.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "${chapter.shlokaCount} श्लोक • ${chapter.shlokaCount} Verses",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.8f)
                    )
                    if (readingHistory != null && readingHistory.lastVerseNumber > 1) {
                        Text(
                            text = " • श्लोक ${readingHistory.lastVerseNumber} पढ़ा",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.SemiBold,
                            color = AccentSaffron
                        )
                    }
                }
            }

            Icon(
                imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                contentDescription = "Read Chapter",
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f),
                modifier = Modifier.size(20.dp)
            )
        }
    }
}
