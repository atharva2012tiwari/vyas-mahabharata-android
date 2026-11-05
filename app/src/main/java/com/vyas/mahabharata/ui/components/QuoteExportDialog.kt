package com.vyas.mahabharata.ui.components

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Paint
import android.graphics.RectF
import android.graphics.Typeface
import android.net.Uri
import android.widget.Toast
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.core.content.FileProvider
import com.vyas.mahabharata.domain.model.Shloka
import com.vyas.mahabharata.ui.theme.AccentGold
import com.vyas.mahabharata.ui.theme.AccentSaffron
import com.vyas.mahabharata.ui.theme.ScriptureEnglishStyle
import com.vyas.mahabharata.ui.theme.ScriptureHindiStyle
import com.vyas.mahabharata.ui.theme.ScriptureIASTStyle
import com.vyas.mahabharata.ui.theme.ScriptureSanskritStyle
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream

// Geometry specifications matching authoritative invariants: 1080x1350 (4:5)
const val EXPORT_CARD_WIDTH = 1080
const val EXPORT_CARD_HEIGHT = 1350
const val EXPORT_CARD_ASPECT_RATIO = 0.8f

enum class QuoteExportTheme {
    WARM_PAPYRUS,
    DARK_ESPRESSO
}

/**
 * High-Resolution Verse Quote Card Image Exporter Dialog
 * Generates stylized 4:5 (1080x1350) scripture cards formatted for system sharing via FileProvider.
 */
@Composable
fun QuoteExportDialog(
    shloka: Shloka,
    parvaName: String,
    onDismissRequest: () -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    var selectedTheme by remember { mutableStateOf(QuoteExportTheme.WARM_PAPYRUS) }
    var includeIAST by remember { mutableStateOf(true) }
    var includeHindi by remember { mutableStateOf(true) }
    var includeEnglish by remember { mutableStateOf(true) }
    var isExporting by remember { mutableStateOf(false) }

    val attribution = "Mahabharata — $parvaName (${shloka.chapterNumber}.${shloka.verseNumber})"

    Dialog(onDismissRequest = onDismissRequest) {
        Surface(
            shape = RoundedCornerShape(28.dp),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 8.dp,
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp)
                    .verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Header with Title & Dismiss
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "श्लोक पत्र • Share Quote Card",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    IconButton(onClick = onDismissRequest, modifier = Modifier.size(32.dp)) {
                        Icon(Icons.Filled.Close, contentDescription = "Close")
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Interactive 4:5 Preview Card
                val previewBg = if (selectedTheme == QuoteExportTheme.WARM_PAPYRUS) {
                    Color(0xFFFBF8F2)
                } else {
                    Color(0xFF1B1917)
                }
                val previewText = if (selectedTheme == QuoteExportTheme.WARM_PAPYRUS) {
                    Color(0xFF252528)
                } else {
                    Color(0xFFEAE4DC)
                }
                val previewAccent = if (selectedTheme == QuoteExportTheme.WARM_PAPYRUS) {
                    Color(0xFF8F4C1B)
                } else {
                    Color(0xFFE08A42)
                }

                Card(
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = previewBg),
                    border = BorderStroke(1.dp, previewAccent.copy(alpha = 0.3f)),
                    modifier = Modifier
                        .fillMaxWidth(0.92f)
                        .aspectRatio(EXPORT_CARD_ASPECT_RATIO)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.SpaceBetween
                    ) {
                        // Top Emblem
                        Text(
                            text = "ॐ",
                            fontSize = 24.sp,
                            color = AccentGold,
                            fontWeight = FontWeight.Bold
                        )

                        // Speaker
                        if (!shloka.speaker.isNullOrBlank()) {
                            Text(
                                text = shloka.speaker,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = AccentSaffron
                            )
                        }

                        // Sanskrit Text (1.8x line height)
                        Text(
                            text = shloka.sanskritDevanagari,
                            style = ScriptureSanskritStyle.copy(
                                fontSize = 15.sp,
                                lineHeight = 27.sp,
                                textAlign = TextAlign.Center
                            ),
                            color = previewText
                        )

                        // Optional IAST
                        if (includeIAST && shloka.sanskritIast.isNotBlank()) {
                            Text(
                                text = shloka.sanskritIast,
                                style = ScriptureIASTStyle.copy(
                                    fontSize = 11.sp,
                                    lineHeight = 16.sp,
                                    textAlign = TextAlign.Center
                                ),
                                color = previewText.copy(alpha = 0.75f)
                            )
                        }

                        // Optional Translations
                        if (includeHindi && shloka.translationHindi.isNotBlank()) {
                            Text(
                                text = shloka.translationHindi,
                                style = ScriptureHindiStyle.copy(
                                    fontSize = 11.sp,
                                    lineHeight = 15.sp,
                                    textAlign = TextAlign.Center
                                ),
                                maxLines = if (includeEnglish && shloka.translationEnglish.isNotBlank()) 2 else 4,
                                color = previewText
                            )
                        }
                        if (includeEnglish && shloka.translationEnglish.isNotBlank()) {
                            Text(
                                text = shloka.translationEnglish,
                                style = ScriptureEnglishStyle.copy(
                                    fontSize = 11.sp,
                                    lineHeight = 15.sp,
                                    textAlign = TextAlign.Center
                                ),
                                maxLines = if (includeHindi && shloka.translationHindi.isNotBlank()) 2 else 4,
                                color = previewText.copy(alpha = 0.85f)
                            )
                        }

                        // Attribution Footer
                        Text(
                            text = attribution,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Medium,
                            color = previewAccent,
                            textAlign = TextAlign.Center
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Theme Selection Chips
                Text(
                    text = "कार्ड का स्वरूप • Theme Style",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(6.dp))
                Row(
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    FilterChip(
                        selected = selectedTheme == QuoteExportTheme.WARM_PAPYRUS,
                        onClick = { selectedTheme = QuoteExportTheme.WARM_PAPYRUS },
                        label = { Text("Sacred Papyrus") }
                    )
                    FilterChip(
                        selected = selectedTheme == QuoteExportTheme.DARK_ESPRESSO,
                        onClick = { selectedTheme = QuoteExportTheme.DARK_ESPRESSO },
                        label = { Text("Dark Espresso") }
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Content Toggles
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    FilterChip(
                        selected = includeIAST,
                        onClick = { includeIAST = !includeIAST },
                        label = { Text("IAST") }
                    )
                    FilterChip(
                        selected = includeHindi,
                        onClick = { includeHindi = !includeHindi },
                        label = { Text("हिन्दी") }
                    )
                    FilterChip(
                        selected = includeEnglish,
                        onClick = { includeEnglish = !includeEnglish },
                        label = { Text("English") }
                    )
                }

                Spacer(modifier = Modifier.height(20.dp))

                // Export & Share Button
                Button(
                    onClick = {
                        if (!isExporting) {
                            isExporting = true
                            coroutineScope.launch {
                                try {
                                    val bitmap = renderQuoteCardBitmap(
                                        shloka = shloka,
                                        parvaName = parvaName,
                                        theme = selectedTheme,
                                        includeIAST = includeIAST,
                                        includeHindi = includeHindi,
                                        includeEnglish = includeEnglish
                                    )
                                    try {
                                        val uri = saveBitmapToCacheAndGetUri(context, bitmap, shloka)
                                        shareQuoteCard(context, uri, attribution)
                                        onDismissRequest()
                                    } finally {
                                        bitmap.recycle()
                                    }
                                } catch (e: Exception) {
                                    Toast.makeText(context, "Export error: ${e.message}", Toast.LENGTH_SHORT).show()
                                } finally {
                                    isExporting = false
                                }
                            }
                        }
                    },
                    shape = RoundedCornerShape(24.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary,
                        contentColor = MaterialTheme.colorScheme.onPrimary
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp)
                ) {
                    Icon(Icons.Filled.Share, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = if (isExporting) "Generating Card..." else "चित्र साझा करें • Share Quote Card",
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }
    }
}

/**
 * Renders the 1080x1350 High-Resolution styled Papyrus Quote Card Bitmap.
 */
suspend fun renderQuoteCardBitmap(
    shloka: Shloka,
    parvaName: String,
    theme: QuoteExportTheme,
    includeIAST: Boolean,
    includeHindi: Boolean,
    includeEnglish: Boolean
): Bitmap = withContext(Dispatchers.Default) {
    val width = EXPORT_CARD_WIDTH
    val height = EXPORT_CARD_HEIGHT
    val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    val canvas = android.graphics.Canvas(bitmap)

    // Palette Resolution
    val bgColor = if (theme == QuoteExportTheme.WARM_PAPYRUS) 0xFFFBF8F2.toInt() else 0xFF1B1917.toInt()
    val textColor = if (theme == QuoteExportTheme.WARM_PAPYRUS) 0xFF252528.toInt() else 0xFFEAE4DC.toInt()
    val secondaryTextColor = if (theme == QuoteExportTheme.WARM_PAPYRUS) 0xFF5A5754.toInt() else 0xFFCCC4BC.toInt()
    val primaryColor = if (theme == QuoteExportTheme.WARM_PAPYRUS) 0xFF8F4C1B.toInt() else 0xFFE08A42.toInt()
    val goldColor = 0xFFD97706.toInt()

    // 1. Background Fill
    val bgPaint = Paint().apply {
        color = bgColor
        style = Paint.Style.FILL
    }
    canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), bgPaint)

    // 2. Ornamental Papyrus Double Border
    val borderPaint = Paint().apply {
        color = primaryColor
        style = Paint.Style.STROKE
        strokeWidth = 4f
        isAntiAlias = true
    }
    canvas.drawRoundRect(RectF(32f, 32f, width - 32f, height - 32f), 24f, 24f, borderPaint)

    val innerBorderPaint = Paint().apply {
        color = goldColor
        style = Paint.Style.STROKE
        strokeWidth = 1.5f
        alpha = 140
        isAntiAlias = true
    }
    canvas.drawRoundRect(RectF(48f, 48f, width - 48f, height - 48f), 16f, 16f, innerBorderPaint)

    // 3. Sacred Emblem ॐ
    val omPaint = Paint().apply {
        color = goldColor
        textSize = 72f
        typeface = Typeface.create(Typeface.SERIF, Typeface.BOLD)
        textAlign = Paint.Align.CENTER
        isAntiAlias = true
    }
    canvas.drawText("ॐ", width / 2f, 150f, omPaint)

    // Current Y layout coordinate
    var currentY = 220f

    // 4. Speaker Attribution
    if (!shloka.speaker.isNullOrBlank()) {
        val speakerPaint = Paint().apply {
            color = goldColor
            textSize = 34f
            typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD)
            textAlign = Paint.Align.CENTER
            isAntiAlias = true
        }
        canvas.drawText(shloka.speaker, width / 2f, currentY, speakerPaint)
        currentY += 60f
    }

    // 5. Sanskrit Shloka (Enforcing 1.8x Line-Height and Auto-Wrapping)
    val sanskritTextSize = 44f
    val sanskritLineHeight = sanskritTextSize * 1.8f // 79.2px line-height
    val sanskritPaint = Paint().apply {
        color = textColor
        textSize = sanskritTextSize
        typeface = Typeface.create(Typeface.SERIF, Typeface.BOLD)
        textAlign = Paint.Align.CENTER
        isAntiAlias = true
    }

    val wrappedSanskrit = wrapText(shloka.sanskritDevanagari, sanskritPaint, width - 160)
    for (line in wrappedSanskrit) {
        canvas.drawText(line, width / 2f, currentY, sanskritPaint)
        currentY += sanskritLineHeight
    }
    currentY += 20f

    // 6. Roman IAST Transliteration (Italicized and Auto-Wrapping)
    if (includeIAST && shloka.sanskritIast.isNotBlank()) {
        val iastTextSize = 28f
        val iastLineHeight = iastTextSize * 1.625f
        val iastPaint = Paint().apply {
            color = secondaryTextColor
            textSize = iastTextSize
            typeface = Typeface.create(Typeface.SERIF, Typeface.ITALIC)
            textAlign = Paint.Align.CENTER
            isAntiAlias = true
        }

        val wrappedIAST = wrapText(shloka.sanskritIast, iastPaint, width - 160)
        for (line in wrappedIAST) {
            canvas.drawText(line, width / 2f, currentY, iastPaint)
            currentY += iastLineHeight
        }
        currentY += 24f
    }

    // Divider
    val dividerPaint = Paint().apply {
        color = primaryColor
        strokeWidth = 1f
        alpha = 80
        isAntiAlias = true
    }
    canvas.drawLine(200f, currentY, width - 200f, currentY, dividerPaint)
    currentY += 40f

    // 7. Hindi Translation
    if (includeHindi && shloka.translationHindi.isNotBlank()) {
        val hindiPaint = Paint().apply {
            color = textColor
            textSize = 28f
            typeface = Typeface.create(Typeface.SANS_SERIF, Typeface.NORMAL)
            textAlign = Paint.Align.CENTER
            isAntiAlias = true
        }
        val wrappedHindi = wrapText(shloka.translationHindi, hindiPaint, width - 160)
        val hindiLines = if (wrappedHindi.size > 5) {
            wrappedHindi.take(4) + listOf(wrappedHindi[4] + "…")
        } else {
            wrappedHindi
        }
        for (line in hindiLines) {
            if (currentY + 44f > height - 140f) {
                canvas.drawText("…", width / 2f, currentY, hindiPaint)
                currentY += 44f
                break
            }
            canvas.drawText(line, width / 2f, currentY, hindiPaint)
            currentY += 44f
        }
        currentY += 16f
    }

    // 8. English Translation
    if (includeEnglish && shloka.translationEnglish.isNotBlank()) {
        val englishPaint = Paint().apply {
            color = secondaryTextColor
            textSize = 26f
            typeface = Typeface.create(Typeface.SERIF, Typeface.NORMAL)
            textAlign = Paint.Align.CENTER
            isAntiAlias = true
        }
        val wrappedEnglish = wrapText(shloka.translationEnglish, englishPaint, width - 160)
        val englishLines = if (wrappedEnglish.size > 5) {
            wrappedEnglish.take(4) + listOf(wrappedEnglish[4] + "…")
        } else {
            wrappedEnglish
        }
        for (line in englishLines) {
            if (currentY + 40f > height - 120f) {
                canvas.drawText("…", width / 2f, currentY, englishPaint)
                break
            }
            canvas.drawText(line, width / 2f, currentY, englishPaint)
            currentY += 40f
        }
    }

    // 9. Canonical Attribution Footer
    val attribution = "Mahabharata — $parvaName (${shloka.chapterNumber}.${shloka.verseNumber})"
    val attrPaint = Paint().apply {
        color = primaryColor
        textSize = 28f
        typeface = Typeface.create(Typeface.SERIF, Typeface.BOLD)
        textAlign = Paint.Align.CENTER
        isAntiAlias = true
    }
    canvas.drawText(attribution, width / 2f, height - 80f, attrPaint)

    bitmap
}

/**
 * Splits text into wrapped lines fitting within max-width.
 */
private fun wrapText(text: String, paint: Paint, maxWidth: Int): List<String> {
    val paragraphs = text.split("\n")
    val lines = mutableListOf<String>()

    for (paragraph in paragraphs) {
        if (paragraph.isBlank()) continue
        val words = paragraph.split("\\s+".toRegex()).filter { it.isNotBlank() }
        var currentLine = StringBuilder()

        for (word in words) {
            val testLine = if (currentLine.isEmpty()) word else "$currentLine $word"
            val measured = paint.measureText(testLine)
            if (measured <= maxWidth) {
                currentLine.append(if (currentLine.isEmpty()) word else " $word")
            } else {
                if (currentLine.isNotEmpty()) {
                    lines.add(currentLine.toString())
                    currentLine = StringBuilder()
                }
                if (paint.measureText(word) > maxWidth) {
                    var remaining = word
                    while (paint.measureText(remaining) > maxWidth && remaining.length > 1) {
                        var splitIdx = remaining.length - 1
                        while (splitIdx > 1 && paint.measureText(remaining.substring(0, splitIdx) + "-") > maxWidth) {
                            splitIdx--
                        }
                        lines.add(remaining.substring(0, splitIdx) + "-")
                        remaining = remaining.substring(splitIdx)
                    }
                    currentLine.append(remaining)
                } else {
                    currentLine = StringBuilder(word)
                }
            }
        }
        if (currentLine.isNotEmpty()) {
            lines.add(currentLine.toString())
        }
    }
    return lines
}

/**
 * Saves generated bitmap to application cache and returns FileProvider sharing Uri.
 */
suspend fun saveBitmapToCacheAndGetUri(
    context: Context,
    bitmap: Bitmap,
    shloka: Shloka
): Uri = withContext(Dispatchers.IO) {
    val quoteCardsDir = File(context.cacheDir, "quote_cards")
    if (!quoteCardsDir.exists()) {
        quoteCardsDir.mkdirs()
    }

    val fileName = "mahabharata_quote_${shloka.parvaNumber}_${shloka.chapterNumber}_${shloka.verseNumber}.png"
    val file = File(quoteCardsDir, fileName)

    FileOutputStream(file).use { out ->
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
        out.flush()
    }

    val authority = "${context.packageName}.fileprovider"
    FileProvider.getUriForFile(context, authority, file)
}

/**
 * Launches system share chooser for the generated quote card image.
 */
fun shareQuoteCard(context: Context, uri: Uri, attribution: String) {
    val shareIntent = Intent(Intent.ACTION_SEND).apply {
        type = "image/png"
        putExtra(Intent.EXTRA_STREAM, uri)
        putExtra(Intent.EXTRA_SUBJECT, attribution)
        putExtra(Intent.EXTRA_TEXT, "$attribution\nShared from Vyasa Mahabharata")
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    val chooser = Intent.createChooser(shareIntent, "Share Mahabharata Quote").apply {
        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }
    context.startActivity(chooser)
}
