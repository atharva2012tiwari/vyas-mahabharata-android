package com.vyas.mahabharata

import com.vyas.mahabharata.data.local.entity.BookmarkEntity
import com.vyas.mahabharata.data.local.entity.ChapterEntity
import com.vyas.mahabharata.data.local.entity.ParvaEntity
import com.vyas.mahabharata.data.local.entity.ReadingHistoryEntity
import com.vyas.mahabharata.data.local.entity.ShlokaEntity
import com.vyas.mahabharata.domain.model.Bookmark
import com.vyas.mahabharata.domain.model.Chapter
import com.vyas.mahabharata.domain.model.Parva
import com.vyas.mahabharata.domain.model.ReadingHistory
import com.vyas.mahabharata.domain.model.Shloka
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Unit tests verifying Milestone 1 domain models, entity-to-domain mappers, and data integrity.
 */
class Milestone1DataLayerTest {

    @Test
    fun testParvaEntityToDomainMapping() {
        val entity = ParvaEntity(
            id = 1,
            number = 1,
            nameSanskrit = "आदिपर्व",
            nameHindi = "आदि पर्व",
            nameEnglish = "Adi Parva",
            subTitle = "The Book of the Beginning",
            summaryEnglish = "Origins of Kuru dynasty",
            summaryHindi = "कुरु वंश की उत्पत्ति",
            colorSeed = "#8F4C1B",
            chapterCount = 236,
            shlokaCount = 8884
        )

        val domain: Parva = entity.toDomain()

        assertEquals(1L, domain.id)
        assertEquals(1, domain.number)
        assertEquals("आदिपर्व", domain.nameSanskrit)
        assertEquals("आदि पर्व", domain.nameHindi)
        assertEquals("Adi Parva", domain.nameEnglish)
        assertEquals("The Book of the Beginning", domain.subTitle)
        assertEquals("#8F4C1B", domain.colorSeed)
        assertEquals(236, domain.chapterCount)
        assertEquals(8884, domain.shlokaCount)
    }

    @Test
    fun testChapterEntityToDomainMapping() {
        val entity = ChapterEntity(
            id = 101,
            parvaNumber = 6,
            chapterNumber = 25,
            titleSanskrit = "अर्जुनविषादयोग",
            titleHindi = "अर्जुन विषाद योग",
            titleEnglish = "The Grief of Arjuna",
            shlokaCount = 47
        )

        val domain: Chapter = entity.toDomain()

        assertEquals(101L, domain.id)
        assertEquals(6, domain.parvaNumber)
        assertEquals(25, domain.chapterNumber)
        assertEquals("अर्जुनविषादयोग", domain.titleSanskrit)
        assertEquals("अर्जुन विषाद योग", domain.titleHindi)
        assertEquals("The Grief of Arjuna", domain.titleEnglish)
        assertEquals(47, domain.shlokaCount)
    }

    @Test
    fun testShlokaEntityToDomainMappingWithBookmarkState() {
        val entity = ShlokaEntity(
            id = 1,
            parvaNumber = 1,
            chapterNumber = 1,
            verseNumber = 1,
            verseTag = "1.1.1",
            speaker = "व्यास उवाच",
            sanskritDevanagari = "नारायणं नमस्कृत्य नरं चैव नरोत्तमम् ।",
            sanskritIast = "nārāyaṇaṃ namaskṛtya naraṃ caiva narottamam |",
            translationHindi = "भगवान नारायण, नर-श्रेष्ठ नर (अर्जुन)...",
            translationEnglish = "Having bowed down unto Narayana..."
        )

        val domainUnbookmarked: Shloka = entity.toDomain(isBookmarked = false)
        assertFalse(domainUnbookmarked.isBookmarked)
        assertEquals("1.1.1", domainUnbookmarked.verseTag)
        assertEquals("व्यास उवाच", domainUnbookmarked.speaker)

        val domainBookmarked: Shloka = entity.toDomain(isBookmarked = true)
        assertTrue(domainBookmarked.isBookmarked)
    }

    @Test
    fun testBookmarkEntityToDomainMapping() {
        val entity = BookmarkEntity(
            id = 10,
            shlokaId = 1,
            collectionName = "Sacred Invocations",
            userNote = "Opening verse of the Mahabharata",
            createdAt = 1700000000000L
        )

        val domain: Bookmark = entity.toDomain()

        assertEquals(10L, domain.id)
        assertEquals(1L, domain.shlokaId)
        assertEquals("Sacred Invocations", domain.collectionName)
        assertEquals("Opening verse of the Mahabharata", domain.userNote)
        assertEquals(1700000000000L, domain.createdAt)
    }

    @Test
    fun testReadingHistoryEntityToDomainMapping() {
        val entity = ReadingHistoryEntity(
            parvaNumber = 6,
            lastChapterNumber = 25,
            lastVerseNumber = 1,
            scrollOffset = 120,
            updatedAt = 1700000000000L
        )

        val domain: ReadingHistory = entity.toDomain()

        assertEquals(6, domain.parvaNumber)
        assertEquals(25, domain.lastChapterNumber)
        assertEquals(1, domain.lastVerseNumber)
        assertEquals(120, domain.scrollOffset)
        assertEquals(1700000000000L, domain.updatedAt)
    }
}
