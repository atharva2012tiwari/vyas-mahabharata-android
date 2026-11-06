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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.outlined.BookmarkBorder
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vyas.mahabharata.domain.model.Shloka
import com.vyas.mahabharata.ui.theme.AccentGold
import com.vyas.mahabharata.ui.theme.AccentPeacock
import com.vyas.mahabharata.ui.theme.AccentSaffron
import com.vyas.mahabharata.ui.theme.ExpressiveAsymmetricBadge
import com.vyas.mahabharata.ui.theme.ExpressivePillShape
import com.vyas.mahabharata.ui.theme.ScriptureEnglishStyle
import com.vyas.mahabharata.ui.theme.ScriptureHindiStyle
import com.vyas.mahabharata.ui.theme.ScriptureIASTStyle
import com.vyas.mahabharata.ui.theme.ScriptureSanskritLargeStyle
import com.vyas.mahabharata.ui.theme.ScriptureSanskritStyle
import com.vyas.mahabharata.ui.theme.SpeakerHeadingStyle

/**
 * Pure Material 3 Expressive Editorial Shloka Presentation
 * Eliminates container clutter, provides expansive editorial reading canvas with 1.8x line-height Devanagari,
 * vivid asymmetric speaker badges, accessible 48dp touch targets, and strict LTR scripture layout isolation.
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

    // Strict LTR Layout Direction Isolation (Protects Sanskrit & English against RTL system flipping)
    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
        Column(
            modifier = modifier
                .fillMaxWidth()
                .padding(horizontal = 4.dp, vertical = 8.dp)
                .animateContentSize(
                    animationSpec = spring(
                        dampingRatio = Spring.DampingRatioLowBouncy,
                        stiffness = Spring.StiffnessMediumLow
                    )
                )
        ) {
            // 1. Header: Classical Verse Tag & Inline Actions (Bookmark & Share)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Verse Indicator Pill
                Box(
                    modifier = Modifier
                        .clip(ExpressivePillShape)
                        .background(MaterialTheme.colorScheme.surfaceContainerHigh)
                        .padding(horizontal = 12.dp, vertical = 5.dp)
                ) {
                    Text(
                        text = "॥ अध्याय ${shloka.chapterNumber} • श्लोक ${shloka.verseNumber} ॥",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                }

                // Accessible 44dp Touch Target Action Icons
                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(
                        onClick = onBookmarkToggle,
                        modifier = Modifier.size(44.dp)
                    ) {
                        Icon(
                            imageVector = if (shloka.isBookmarked) Icons.Filled.Bookmark else Icons.Outlined.BookmarkBorder,
                            contentDescription = if (shloka.isBookmarked) "Remove Bookmark" else "Save Bookmark",
                            tint = if (shloka.isBookmarked) AccentSaffron else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f),
                            modifier = Modifier.size(22.dp)
                        )
                    }

                    Spacer(modifier = Modifier.width(2.dp))

                    IconButton(
                        onClick = onShareClick,
                        modifier = Modifier.size(44.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Filled.Share,
                            contentDescription = "Share Quote Card",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f),
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }

            // 2. Vivid Asymmetric Speaker Badge (e.g. श्रीभगवानुवाच, अर्जुन उवाच, सञ्जय उवाच)
            if (!shloka.speaker.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(10.dp))
                val isBhagavan = shloka.speaker.contains("भगवान") || shloka.speaker.contains("श्रीभगवान")
                Box(
                    modifier = Modifier
                        .clip(ExpressiveAsymmetricBadge)
                        .background(
                            if (isBhagavan) AccentSaffron.copy(alpha = 0.16f)
                            else AccentPeacock.copy(alpha = 0.14f)
                        )
                        .padding(horizontal = 14.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = shloka.speaker,
                        style = SpeakerHeadingStyle,
                        color = if (isBhagavan) AccentSaffron else AccentPeacock,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            // 3. Layer 1: Sanskrit Original Shloka (1.8x Line-Height, Serif)
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

            // 4. Layer 2: Roman IAST Transliteration (Italicized)
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

            // Subtle divider between Sanskrit and translations
            AnimatedVisibility(
                visible = (effectiveShowSanskrit || showIAST) && (showHindi || showEnglish),
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column {
                    Spacer(modifier = Modifier.height(16.dp))
                    HorizontalDivider(
                        thickness = 0.5.dp,
                        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.25f)
                    )
                }
            }

            // 5. Layer 3: Hindi Translation
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

            // 6. Layer 4: English Translation
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

            // 7. Expansive Editorial Verse Spacer & Subtle Divider
            Spacer(modifier = Modifier.height(28.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                HorizontalDivider(
                    modifier = Modifier.weight(1f),
                    thickness = 0.5.dp,
                    color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.25f)
                )
                Box(
                    modifier = Modifier
                        .padding(horizontal = 12.dp)
                        .size(5.dp)
                        .clip(ExpressivePillShape)
                        .background(AccentGold.copy(alpha = 0.5f))
                )
                HorizontalDivider(
                    modifier = Modifier.weight(1f),
                    thickness = 0.5.dp,
                    color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.25f)
                )
            }
        }
    }
}
