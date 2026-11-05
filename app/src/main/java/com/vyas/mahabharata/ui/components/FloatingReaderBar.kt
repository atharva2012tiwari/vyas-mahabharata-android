package com.vyas.mahabharata.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.animateContentSize
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FormatSize
import androidx.compose.material.icons.filled.List
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * Material 3 Expressive Horizontal Floating Reader Toolbar
 * Dynamic scroll auto-hide with morphing ButtonGroup toggleable chips for instant language selection.
 * Invariant: At least one language must remain selected at all times.
 */
@Composable
fun FloatingReaderBar(
    isVisible: Boolean,
    showSanskrit: Boolean,
    showIAST: Boolean,
    showHindi: Boolean,
    showEnglish: Boolean,
    onToggleSanskrit: () -> Unit,
    onToggleIAST: () -> Unit,
    onToggleHindi: () -> Unit,
    onToggleEnglish: () -> Unit,
    onChapterIndexClick: () -> Unit,
    onFontSizeClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    // Count active languages to enforce minimum 1 active invariant
    val activeCount = listOf(showSanskrit, showIAST, showHindi, showEnglish).count { it }

    AnimatedVisibility(
        visible = isVisible,
        enter = slideInVertically(
            initialOffsetY = { it * 2 },
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessMediumLow
            )
        ),
        exit = slideOutVertically(
            targetOffsetY = { it * 2 },
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioNoBouncy,
                stiffness = Spring.StiffnessMedium
            )
        ),
        modifier = modifier
    ) {
        // Expressive Floating Toolbar Container
        Surface(
            shape = RoundedCornerShape(32.dp),
            color = MaterialTheme.colorScheme.surfaceContainerHighest,
            tonalElevation = 6.dp,
            shadowElevation = 8.dp,
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.35f)),
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)
        ) {
            Row(
                modifier = Modifier
                    .animateContentSize(
                        animationSpec = spring(
                            dampingRatio = 0.8f,
                            stiffness = 400f
                        )
                    )
                    .padding(horizontal = 10.dp, vertical = 6.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                // Morphing ButtonGroup with toggleable chips:
                // [संस्कृत]
                LanguageToggleChip(
                    text = "[संस्कृत]",
                    selected = showSanskrit,
                    canDeselect = activeCount > 1 || !showSanskrit,
                    onClick = {
                        if (activeCount > 1 || !showSanskrit) {
                            onToggleSanskrit()
                        }
                    }
                )

                // [IAST]
                LanguageToggleChip(
                    text = "[IAST]",
                    selected = showIAST,
                    canDeselect = activeCount > 1 || !showIAST,
                    onClick = {
                        if (activeCount > 1 || !showIAST) {
                            onToggleIAST()
                        }
                    }
                )

                // [हिन्दी]
                LanguageToggleChip(
                    text = "[हिन्दी]",
                    selected = showHindi,
                    canDeselect = activeCount > 1 || !showHindi,
                    onClick = {
                        if (activeCount > 1 || !showHindi) {
                            onToggleHindi()
                        }
                    }
                )

                // [English]
                LanguageToggleChip(
                    text = "[English]",
                    selected = showEnglish,
                    canDeselect = activeCount > 1 || !showEnglish,
                    onClick = {
                        if (activeCount > 1 || !showEnglish) {
                            onToggleEnglish()
                        }
                    }
                )

                Spacer(modifier = Modifier.width(4.dp))

                // Chapter Index Picker Action
                IconButton(
                    onClick = onChapterIndexClick,
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(
                        imageVector = Icons.Filled.List,
                        contentDescription = "Chapter Index",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(20.dp)
                    )
                }

                // Font Controls Action
                IconButton(
                    onClick = onFontSizeClick,
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(
                        imageVector = Icons.Filled.FormatSize,
                        contentDescription = "Font Controls",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }
    }
}

/**
 * Animated toggleable item chip with spring width morphing and soft-contrast color transitions.
 */
@Composable
private fun LanguageToggleChip(
    text: String,
    selected: Boolean,
    canDeselect: Boolean,
    onClick: () -> Unit
) {
    val hPadding by animateDpAsState(
        targetValue = if (selected) 12.dp else 8.dp,
        animationSpec = spring(dampingRatio = 0.8f, stiffness = 400f),
        label = "ChipPadding"
    )

    val bgColor by animateColorAsState(
        targetValue = if (selected) {
            MaterialTheme.colorScheme.primary
        } else {
            MaterialTheme.colorScheme.surfaceContainerLow
        },
        animationSpec = spring(stiffness = Spring.StiffnessMediumLow),
        label = "ChipBgColor"
    )

    val contentColor by animateColorAsState(
        targetValue = if (selected) {
            MaterialTheme.colorScheme.onPrimary
        } else {
            MaterialTheme.colorScheme.onSurfaceVariant
        },
        animationSpec = spring(stiffness = Spring.StiffnessMediumLow),
        label = "ChipTextColor"
    )

    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(16.dp))
            .background(bgColor)
            .clickable(
                enabled = canDeselect || !selected,
                interactionSource = remember { MutableInteractionSource() },
                indication = null,
                onClick = onClick
            )
            .padding(horizontal = hPadding, vertical = 6.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.labelSmall.copy(
                fontSize = 12.sp,
                fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal
            ),
            color = contentColor
        )
    }
}
