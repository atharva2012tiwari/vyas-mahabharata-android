package com.vyas.mahabharata.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateContentSize
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.spring
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.outlined.BookmarkBorder
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vyas.mahabharata.domain.model.Shloka
import com.vyas.mahabharata.ui.theme.AccentSaffron
import com.vyas.mahabharata.ui.theme.ScriptureEnglishStyle
import com.vyas.mahabharata.ui.theme.ScriptureHindiStyle
import com.vyas.mahabharata.ui.theme.ScriptureIASTStyle
import com.vyas.mahabharata.ui.theme.ScriptureSanskritLargeStyle
import com.vyas.mahabharata.ui.theme.ScriptureSanskritStyle
import com.vyas.mahabharata.ui.theme.SpeakerHeadingStyle

/**
 * Spacious Shloka Card Component
 * Formatted with 1.8x line-height ratio, zone isolation, and smooth visibility transitions.
 */
@Composable
fun ShlokaCard(
    shloka: Shloka,
    modifier: Modifier = Modifier,
    isLargeFont: Boolean = false,
    showSanskrit: Boolean = true,
    showIAST: Boolean = false,
    showHindi: Boolean = true,
    showEnglish: Boolean = true,
    onBookmarkToggle: () -> Unit = {},
    onShareClick: () -> Unit = {}
) {
    // Invariant: Guarantee at least one language is visible
    val effectiveShowSanskrit = showSanskrit || (!showIAST && !showHindi && !showEnglish)

    val sanskritStyle = if (isLargeFont) ScriptureSanskritLargeStyle else ScriptureSanskritStyle
    val iastStyle = if (isLargeFont) ScriptureIASTStyle.copy(fontSize = 17.sp, lineHeight = 28.sp) else ScriptureIASTStyle
    val hindiStyle = if (isLargeFont) ScriptureHindiStyle.copy(fontSize = 18.sp, lineHeight = 31.5.sp) else ScriptureHindiStyle
    val englishStyle = if (isLargeFont) ScriptureEnglishStyle.copy(fontSize = 18.sp, lineHeight = 29.25.sp) else ScriptureEnglishStyle

    Card(
        modifier = modifier
            .fillMaxWidth()
            .animateContentSize(
                animationSpec = spring(
                    dampingRatio = Spring.DampingRatioLowBouncy,
                    stiffness = Spring.StiffnessMediumLow
                )
            ),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainerLow
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp, pressedElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 22.dp, vertical = 20.dp)
        ) {
            // Header Row: Verse Tag, Speaker & Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Verse Indicator Pill
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(MaterialTheme.colorScheme.surfaceContainerHighest)
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "अध्याय ${shloka.chapterNumber} • श्लोक ${shloka.verseNumber}",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                // Action Icons
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(
                        onClick = onBookmarkToggle,
                        modifier = Modifier.size(36.dp)
                    ) {
                        Icon(
                            imageVector = if (shloka.isBookmarked) Icons.Filled.Bookmark else Icons.Outlined.BookmarkBorder,
                            contentDescription = "Bookmark",
                            tint = if (shloka.isBookmarked) AccentSaffron else MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(20.dp)
                        )
                    }

                    Spacer(modifier = Modifier.width(4.dp))

                    IconButton(
                        onClick = onShareClick,
                        modifier = Modifier.size(36.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Share,
                            contentDescription = "Share Quote",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }

            // Optional Speaker Attribution
            if (!shloka.speaker.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = shloka.speaker,
                    style = SpeakerHeadingStyle,
                    color = AccentSaffron
                )
            }

            // Layer 1: Sanskrit Original Shloka (1.8x Line-Height)
            AnimatedVisibility(
                visible = effectiveShowSanskrit,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column {
                    Spacer(modifier = Modifier.height(14.dp))
                    Text(
                        text = shloka.sanskritDevanagari,
                        style = sanskritStyle,
                        color = MaterialTheme.colorScheme.onSurface,
                        textAlign = TextAlign.Start,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            // Layer 2: Roman IAST Transliteration (Italicized)
            AnimatedVisibility(
                visible = showIAST,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column {
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = shloka.sanskritIast,
                        style = iastStyle,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            // Subtle Divider between Sanskrit and Translations with smooth animated collapse/expansion
            AnimatedVisibility(
                visible = (effectiveShowSanskrit || showIAST) && (showHindi || showEnglish),
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column {
                    Spacer(modifier = Modifier.height(16.dp))
                    HorizontalDivider(
                        thickness = 0.5.dp,
                        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.3f)
                    )
                }
            }

            // Layer 3: Hindi Translation
            AnimatedVisibility(
                visible = showHindi,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column {
                    Spacer(modifier = Modifier.height(14.dp))
                    Text(
                        text = shloka.translationHindi,
                        style = hindiStyle,
                        color = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            // Layer 4: English Translation
            AnimatedVisibility(
                visible = showEnglish,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column {
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = shloka.translationEnglish,
                        style = englishStyle,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        }
    }
}
