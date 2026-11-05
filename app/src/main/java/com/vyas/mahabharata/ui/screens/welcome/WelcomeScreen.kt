package com.vyas.mahabharata.ui.screens.welcome

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.drawWithCache
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipPath
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vyas.mahabharata.ui.theme.AccentGold
import com.vyas.mahabharata.ui.theme.AccentSaffron
import com.vyas.mahabharata.ui.theme.ScriptureIASTStyle
import com.vyas.mahabharata.ui.theme.ScriptureSanskritDisplayStyle
import com.vyas.mahabharata.ui.theme.ScriptureSanskritStyle
import kotlinx.coroutines.delay
import kotlin.math.cos
import kotlin.math.exp
import kotlin.math.sqrt

/**
 * Procedural Harmonic Canvas Welcome Screen
 * Features damped spring harmonic ripples, calligraphic vector shader inscription, and instant tap-to-bypass.
 */
@Composable
fun WelcomeScreen(
    onEnterClick: () -> Unit
) {
    // Single tap idempotence guard: only trigger navigation once
    var bypassed by remember { mutableStateOf(false) }
    val handleBypass = {
        if (!bypassed) {
            bypassed = true
            onEnterClick()
        }
    }

    // Touch origin for interactive ripple physics
    var touchOrigin by remember { mutableStateOf<Offset?>(null) }

    // Phase 1: Procedural Harmonic Wave Expansion
    val infiniteTransition = rememberInfiniteTransition(label = "HarmonicWaves")
    val waveTime by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 4f,
        animationSpec = infiniteRepeatable(
            animation = tween(4000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "WaveTime"
    )

    // Phase 2: Calligraphic text dynamic stroke and reveal progress
    val textAlpha = remember { Animatable(0f) }
    val inscriptionSweep = remember { Animatable(0f) }
    val buttonAlpha = remember { Animatable(0f) }

    LaunchedEffect(Unit) {
        delay(400)
        // Progressive calligraphic stroke reveal
        inscriptionSweep.animateTo(
            targetValue = 1f,
            animationSpec = tween(2200, easing = FastOutSlowInEasing)
        )
        textAlpha.animateTo(
            targetValue = 1f,
            animationSpec = tween(1200, easing = FastOutSlowInEasing)
        )
        delay(300)
        buttonAlpha.animateTo(
            targetValue = 1f,
            animationSpec = tween(800, easing = FastOutSlowInEasing)
        )
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        MaterialTheme.colorScheme.surface,
                        MaterialTheme.colorScheme.surfaceContainerLow,
                        MaterialTheme.colorScheme.surfaceContainer
                    )
                )
            )
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { offset ->
                        touchOrigin = offset
                        handleBypass()
                    }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        val primaryColor = MaterialTheme.colorScheme.primary
        val saffronColor = AccentSaffron
        val goldColor = AccentGold

        // Damped Harmonic Physics Canvas:
        // y(t) = A_0 * exp(-zeta * omega * t) * cos(omega_d * t)
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = touchOrigin ?: Offset(size.width / 2f, size.height * 0.40f)
            val maxRadius = size.width * 0.85f

            // Wave parameters
            val zeta = 0.15f // Underdamped ratio
            val omega = 10f // Natural angular frequency
            val omegaD = omega * sqrt(1f - zeta * zeta) // Damped frequency
            val ringCount = 6

            for (i in 0 until ringCount) {
                val ringPhase = (waveTime + i * (4f / ringCount)) % 4f
                val t = ringPhase
                // Damped wave amplitude calculation
                val amplitude = (exp(-zeta * omega * (t * 0.25f)) * cos(omegaD * (t * 0.25f))).coerceIn(-1f, 1f)
                val normalizedRadius = (ringPhase / 4f) * maxRadius
                val dynamicAlpha = ((1f - (ringPhase / 4f)) * kotlin.math.abs(amplitude) * 0.35f).coerceIn(0f, 1f)

                if (normalizedRadius > 0f && dynamicAlpha > 0.01f) {
                    // Radiant glow ring
                    drawCircle(
                        brush = Brush.radialGradient(
                            colors = listOf(
                                saffronColor.copy(alpha = dynamicAlpha),
                                goldColor.copy(alpha = dynamicAlpha * 0.4f),
                                primaryColor.copy(alpha = 0f)
                            ),
                            center = center,
                            radius = normalizedRadius + 30f
                        ),
                        radius = normalizedRadius,
                        center = center
                    )

                    // Sharp concentric wave crest
                    drawCircle(
                        color = goldColor.copy(alpha = dynamicAlpha * 0.7f),
                        radius = normalizedRadius,
                        center = center,
                        style = Stroke(width = 1.8.dp.toPx())
                    )
                }
            }
        }

        // Calligraphic Invocation Content Column (Centered within 600dp reading measure)
        Column(
            modifier = Modifier
                .widthIn(max = 600.dp)
                .fillMaxWidth()
                .padding(horizontal = 28.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Sacred Emblem ॐ with pulsating gold aura
            Text(
                text = "ॐ",
                style = MaterialTheme.typography.displayLarge.copy(
                    fontSize = 56.sp,
                    lineHeight = 64.sp
                ),
                color = AccentGold,
                modifier = Modifier.alpha(textAlpha.value)
            )

            Spacer(modifier = Modifier.height(28.dp))

            // Dynamic Calligraphic Shloka (77 code points canonical text) with vector path clip shader
            // "नारायणं नमस्कृत्य नरं चैव नरोत्तमम् ।\nदेवीं सरस्वतीं व्यासं ततो जयमुदीरयेत् ॥"
            Box(
                modifier = Modifier
                    .padding(horizontal = 8.dp)
                    .drawWithCache {
                        val sweep = inscriptionSweep.value
                        val clipPath = Path().apply {
                            moveTo(0f, 0f)
                            lineTo(size.width * sweep, 0f)
                            lineTo(size.width * sweep, size.height)
                            lineTo(0f, size.height)
                            close()
                        }
                        onDrawWithContent {
                            clipPath(clipPath) {
                                this@onDrawWithContent.drawContent()
                            }
                            if (sweep in 0.01f..0.99f) {
                                // Dynamic calligraphic gold/saffron vector stroke at the inscription front
                                drawLine(
                                    brush = Brush.verticalGradient(
                                        listOf(
                                            saffronColor.copy(alpha = 0f),
                                            goldColor,
                                            saffronColor.copy(alpha = 0f)
                                        )
                                    ),
                                    start = Offset(size.width * sweep, 0f),
                                    end = Offset(size.width * sweep, size.height),
                                    strokeWidth = 2.5.dp.toPx()
                                )
                            }
                        }
                    }
            ) {
                Text(
                    text = "नारायणं नमस्कृत्य नरं चैव नरोत्तमम् ।\nदेवीं सरस्वतीं व्यासं ततो जयमुदीरयेत् ॥",
                    style = ScriptureSanskritDisplayStyle.copy(
                        textAlign = TextAlign.Center
                    ),
                    color = MaterialTheme.colorScheme.onSurface
                )
            }

            Spacer(modifier = Modifier.height(18.dp))

            // Roman IAST Transliteration (Italicized)
            Text(
                text = "nārāyaṇaṃ namaskṛtya naraṃ caiva narottamam |\ndevīṃ sarasvatīṃ vyāsaṃ tato jayamudīrayet ||",
                style = ScriptureIASTStyle.copy(
                    fontSize = 15.sp,
                    lineHeight = 24.sp,
                    textAlign = TextAlign.Center
                ),
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.85f),
                modifier = Modifier.alpha(textAlpha.value)
            )

            Spacer(modifier = Modifier.height(22.dp))

            // Sacred Epigraph Subtitle
            Text(
                text = "श्रीमद्भगवद्गीता एवं अष्टादशपर्व महाभारत",
                style = MaterialTheme.typography.titleMedium,
                color = AccentSaffron,
                textAlign = TextAlign.Center,
                modifier = Modifier.alpha(textAlpha.value)
            )

            Spacer(modifier = Modifier.height(44.dp))

            // Enter Scripture Button (Tapping button or tapping canvas anywhere invokes bypass)
            Button(
                onClick = handleBypass,
                shape = RoundedCornerShape(32.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    contentColor = MaterialTheme.colorScheme.onPrimary
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 4.dp),
                modifier = Modifier
                    .height(54.dp)
                    .alpha(buttonAlpha.value)
            ) {
                Text(
                    text = "शास्त्र प्रवेश • Enter Scripture",
                    style = MaterialTheme.typography.labelLarge.copy(fontSize = 16.sp),
                    modifier = Modifier.padding(horizontal = 16.dp)
                )
            }
        }
    }
}
