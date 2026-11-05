package com.vyas.mahabharata.ui.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes
import androidx.compose.ui.unit.dp

val VyasShapes = Shapes(
    extraSmall = RoundedCornerShape(6.dp),
    small = RoundedCornerShape(10.dp),
    medium = RoundedCornerShape(16.dp),
    large = RoundedCornerShape(24.dp), // Spacious Shloka Cards
    extraLarge = RoundedCornerShape(32.dp) // Floating Toolbars & Dialogs
)
