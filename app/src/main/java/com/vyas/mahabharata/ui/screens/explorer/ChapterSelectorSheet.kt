package com.vyas.mahabharata.ui.screens.explorer

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForwardIos
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.SheetState
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.vyas.mahabharata.domain.model.Chapter
import com.vyas.mahabharata.domain.model.Parva
import com.vyas.mahabharata.ui.theme.AccentPeacock
import com.vyas.mahabharata.ui.theme.AccentSaffron
import com.vyas.mahabharata.ui.theme.ExpressiveAsymmetricBadge

/**
 * Material 3 Expressive Chapter Selector Modal Sheet
 * Provides streamlined chapter discovery across all 18 Chapters of the Bhagavad Gita.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChapterSelectorSheet(
    parva: Parva,
    chapters: List<Chapter>,
    onSelectChapter: (parvaNumber: Int, chapterNumber: Int) -> Unit,
    onDismissRequest: () -> Unit,
    sheetState: SheetState = rememberModalBottomSheetState(skipPartiallyExpanded = false)
) {
    ModalBottomSheet(
        onDismissRequest = onDismissRequest,
        sheetState = sheetState,
        shape = RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp),
        containerColor = MaterialTheme.colorScheme.surfaceContainerLow,
        dragHandle = null
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 640.dp)
                .fillMaxWidth()
                .padding(top = 16.dp, bottom = 28.dp)
        ) {
            // Header: Gita metadata and close action
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "श्रीमद्भगवद्गीता • अध्याय सूची",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = "18 Chapters • 700 Verses",
                        style = MaterialTheme.typography.labelMedium,
                        color = AccentSaffron
                    )
                }

                IconButton(
                    onClick = onDismissRequest,
                    modifier = Modifier.size(38.dp)
                ) {
                    Icon(
                        imageVector = Icons.Filled.Close,
                        contentDescription = "Close Sheet",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            HorizontalDivider(
                thickness = 0.5.dp,
                color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f),
                modifier = Modifier.padding(vertical = 8.dp)
            )

            // Chapter items list
            LazyColumn(
                modifier = Modifier.fillMaxWidth()
            ) {
                items(chapters, key = { it.id }) { chapter ->
                    ChapterListItem(
                        chapter = chapter,
                        onClick = {
                            onSelectChapter(chapter.parvaNumber, chapter.chapterNumber)
                            onDismissRequest()
                        }
                    )
                }
            }
        }
    }
}

@Composable
private fun ChapterListItem(
    chapter: Chapter,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(horizontal = 24.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.weight(1f)
        ) {
            // Vivid Asymmetric Chapter Number Tag
            val formattedNumber = if (chapter.chapterNumber < 10) "0${chapter.chapterNumber}" else "${chapter.chapterNumber}"
            val isOdd = chapter.chapterNumber % 2 == 1
            Box(
                modifier = Modifier
                    .size(46.dp)
                    .clip(ExpressiveAsymmetricBadge)
                    .background(
                        if (isOdd) AccentSaffron.copy(alpha = 0.15f)
                        else AccentPeacock.copy(alpha = 0.15f)
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = formattedNumber,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.ExtraBold,
                    color = if (isOdd) AccentSaffron else AccentPeacock
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            // Chapter title and verse count
            Column {
                Text(
                    text = chapter.titleSanskrit,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                if (chapter.titleEnglish.isNotBlank() && chapter.titleEnglish != chapter.titleSanskrit) {
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = chapter.titleEnglish,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = "${chapter.shlokaCount} श्लोक (${chapter.shlokaCount} verses)",
                    style = MaterialTheme.typography.labelSmall,
                    color = if (isOdd) AccentSaffron else AccentPeacock
                )
            }
        }

        Icon(
            imageVector = Icons.AutoMirrored.Filled.ArrowForwardIos,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
            modifier = Modifier.size(14.dp)
        )
    }
}
