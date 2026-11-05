package com.vyas.mahabharata.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// Light: Sacred Warm Papyrus
val WarmPapyrusColorScheme = lightColorScheme(
    primary = PapyrusPrimary,
    onPrimary = PapyrusOnPrimary,
    primaryContainer = PapyrusPrimaryContainer,
    onPrimaryContainer = PapyrusOnPrimaryContainer,
    secondary = PapyrusSecondary,
    onSecondary = PapyrusOnSecondary,
    secondaryContainer = PapyrusSecondaryContainer,
    onSecondaryContainer = PapyrusOnSecondaryContainer,
    surface = PapyrusSurface,
    onSurface = PapyrusOnSurface,
    onSurfaceVariant = PapyrusOnSurfaceVariant,
    background = PapyrusSurface,
    onBackground = PapyrusOnSurface,
    surfaceContainerLowest = PapyrusContainerLowest,
    surfaceContainerLow = PapyrusContainerLow,
    surfaceContainer = PapyrusContainer,
    surfaceContainerHigh = PapyrusContainerHigh,
    surfaceContainerHighest = PapyrusContainerHighest,
    outline = PapyrusSecondary,
    outlineVariant = Color(0xFFD8D0C5)
)

// Dark: Deep Espresso Amber
val DarkEspressoColorScheme = darkColorScheme(
    primary = EspressoPrimary,
    onPrimary = EspressoOnPrimary,
    primaryContainer = EspressoPrimaryContainer,
    onPrimaryContainer = EspressoOnPrimaryContainer,
    secondary = EspressoSecondary,
    onSecondary = EspressoOnSecondary,
    secondaryContainer = EspressoSecondaryContainer,
    onSecondaryContainer = EspressoOnSecondaryContainer,
    surface = EspressoSurface,
    onSurface = EspressoOnSurface,
    onSurfaceVariant = EspressoOnSurfaceVariant,
    background = EspressoSurface,
    onBackground = EspressoOnSurface,
    surfaceContainerLowest = EspressoContainerLowest,
    surfaceContainerLow = EspressoContainerLow,
    surfaceContainer = EspressoContainer,
    surfaceContainerHigh = EspressoContainerHigh,
    surfaceContainerHighest = EspressoContainerHighest,
    outline = EspressoSecondary,
    outlineVariant = Color(0xFF4E473F)
)

@Composable
fun VyasTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false, // Default false to preserve Sacred Papyrus/Espresso tranquility
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkEspressoColorScheme
        else -> WarmPapyrusColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as? Activity)?.window ?: return@SideEffect
            window.statusBarColor = colorScheme.surface.toArgb()
            window.navigationBarColor = colorScheme.surface.toArgb()
            val windowInsetsController = WindowCompat.getInsetsController(window, view)
            windowInsetsController.isAppearanceLightStatusBars = !darkTheme
            windowInsetsController.isAppearanceLightNavigationBars = !darkTheme
        }
    }

    CompositionLocalProvider(LocalExpressiveTypography provides ExpressiveTypography) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = VyasTypography,
            shapes = VyasShapes,
            content = content
        )
    }
}
