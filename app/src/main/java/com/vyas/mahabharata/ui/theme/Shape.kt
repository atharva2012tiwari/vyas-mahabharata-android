package com.vyas.mahabharata.ui.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes
import androidx.compose.ui.unit.dp

val VyasShapes = Shapes(
    extraSmall = RoundedCornerShape(6.dp),
    small = RoundedCornerShape(10.dp),
    medium = RoundedCornerShape(16.dp),
    large = RoundedCornerShape(24.dp),
    extraLarge = RoundedCornerShape(32.dp)
)

// Material 3 Expressive Vivid Geometry
val ExpressivePillShape = RoundedCornerShape(32.dp)
val ExpressiveAsymmetricBadge = RoundedCornerShape(topStart = 22.dp, bottomEnd = 22.dp, topEnd = 6.dp, bottomStart = 6.dp)
val ExpressiveAsymmetricCard = RoundedCornerShape(topStart = 28.dp, bottomEnd = 28.dp, topEnd = 12.dp, bottomStart = 12.dp)
val ExpressiveWisdomContainer = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp, bottomStart = 10.dp, bottomEnd = 10.dp)
