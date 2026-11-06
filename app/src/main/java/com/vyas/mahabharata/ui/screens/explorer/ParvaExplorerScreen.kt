package com.vyas.mahabharata.ui.screens.explorer

import androidx.compose.foundation.BorderStroke
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.Search
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
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vyas.mahabharata.data.repository.MahabharataRepository
import com.vyas.mahabharata.domain.model.Chapter
import com.vyas.mahabharata.domain.model.Parva
import com.vyas.mahabharata.domain.model.ReadingHistory
import com.vyas.mahabharata.ui.theme.AccentGold
import com.vyas.mahabharata.ui.theme.AccentSaffron
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch

/**
 * 18 Parvas Explorer Screen
 * Expansive visual overview of the entire epic with progress tracking, color seeds, and chapter selector modals.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ParvaExplorerScreen(
    repository: MahabharataRepository,
    onNavigateToChapter: (parvaNumber: Int, chapterNumber: Int) -> Unit,
    onNavigateToSearch: () -> Unit,
    onNavigateToBookmarks: () -> Unit
) {
    val parvas by repository.getAllParvas().collectAsState(initial = emptyList())
    val allHistory by repository.getAllReadingHistory().collectAsState(initial = emptyList())
    val historyMap = remember(allHistory) { allHistory.associateBy { it.parvaNumber } }
    val coroutineScope = rememberCoroutineScope()

    var selectedParvaForSheet by remember { mutableStateOf<Parva?>(null) }
    var sheetChapters by remember { mutableStateOf<List<Chapter>>(emptyList()) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "व्यास महाभारत",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Text(
                            text = "अष्टादशपर्व • 18 Books of the Epic",
                            style = MaterialTheme.typography.labelSmall,
                            color = AccentSaffron
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onNavigateToSearch) {
                        Icon(
                            imageVector = Icons.Filled.Search,
                            contentDescription = "Search Epic",
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
                    .widthIn(max = 600.dp) // Centered measure constraint
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(top = 12.dp, bottom = 32.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                items(parvas, key = { it.id }) { parva ->
                    ParvaCard(
                        parva = parva,
                        readingHistory = historyMap[parva.number],
                        onClick = {
                            selectedParvaForSheet = parva
                            coroutineScope.launch {
                                val chapters = repository.getChaptersForParva(parva.number).firstOrNull() ?: emptyList()
                                sheetChapters = chapters
                            }
                        }
                    )
                }
            }
        }
    }

    // Modal Chapter Selector Bottom Sheet
    selectedParvaForSheet?.let { parva ->
        ChapterSelectorSheet(
            parva = parva,
            chapters = sheetChapters,
            onSelectChapter = { pNum, chNum ->
                selectedParvaForSheet = null
                onNavigateToChapter(pNum, chNum)
            },
            onDismissRequest = {
                selectedParvaForSheet = null
            }
        )
    }
}

/**
 * Visual Parva Card component with canonical color seed, statistics, and progress pill.
 */
@Composable
fun ParvaCard(
    parva: Parva,
    readingHistory: ReadingHistory?,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val parsedColorSeed = try {
        Color(android.graphics.Color.parseColor(parva.colorSeed))
    } catch (e: Exception) {
        MaterialTheme.colorScheme.primary
    }

    Card(
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainerLow
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp, pressedElevation = 4.dp),
        border = BorderStroke(1.dp, parsedColorSeed.copy(alpha = 0.25f)),
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
        ) {
            // Header Row: Parva Tag, Number & Color Accent
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .clip(CircleShape)
                            .background(parsedColorSeed.copy(alpha = 0.15f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "${parva.number}",
                            style = MaterialTheme.typography.labelLarge,
                            fontWeight = FontWeight.Bold,
                            color = parsedColorSeed
                        )
                    }

                    Spacer(modifier = Modifier.width(10.dp))

                    Text(
                        text = "पर्व ${parva.number} • Book ${parva.number}",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                // Reading Progress Pill
                val progressText = if (readingHistory != null && readingHistory.lastChapterNumber > 0) {
                    val pct = if (parva.chapterCount > 0) {
                        ((readingHistory.lastChapterNumber.toFloat() / parva.chapterCount) * 100).toInt()
                    } else 0
                    "Ch. ${readingHistory.lastChapterNumber} • $pct%"
                } else {
                    "Unread"
                }

                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(
                            if (readingHistory != null && readingHistory.lastChapterNumber > 0) {
                                AccentSaffron.copy(alpha = 0.15f)
                            } else {
                                MaterialTheme.colorScheme.surfaceContainerHighest
                            }
                        )
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = progressText,
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Medium,
                        color = if (readingHistory != null && readingHistory.lastChapterNumber > 0) {
                            AccentSaffron
                        } else {
                            MaterialTheme.colorScheme.onSurfaceVariant
                        }
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Parva Titles
            Text(
                text = parva.nameSanskrit,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )

            Text(
                text = "${parva.nameEnglish} — ${parva.subTitle ?: ""}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Normal,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(10.dp))

            // Summary excerpt
            Text(
                text = parva.summaryEnglish ?: "",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.85f),
                maxLines = 2
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Footer Row: Statistics & Open Button
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "${parva.chapterCount} Chapters • ${parva.shlokaCount} Verses",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = "अध्याय चुनें",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = parsedColorSeed
                    )
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                        contentDescription = null,
                        tint = parsedColorSeed,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
        }
    }
}
