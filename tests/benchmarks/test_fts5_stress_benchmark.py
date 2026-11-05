#!/usr/bin/env python3
"""
Empirical Benchmark & Multilingual Boundary Edge-Case Test Suite for Vyasa Mahabharata FTS5 Search.

Validates:
1. 1,000+ FTS5 queries executed across Latin, Devanagari, punctuation, numbers,
   special characters, unmatched quotes, single-character tokens, and large multi-word queries.
2. 95th and 99th percentile query latencies strictly under 15ms.
3. Unicode normalization (NFC vs NFD equivalence).
4. Diacritic stripping & accent insensitivity across Roman IAST and ASCII.
5. Partial prefix matches (*).
6. Sanitizer robustness and Indic vowel sign / virama preservation.
"""

import math
import os
import re
import sqlite3
import sys
import time
import unicodedata
import unittest
from typing import Dict, List, Tuple, Any

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DB_PATH = os.path.join(WORKSPACE_ROOT, "app/src/main/assets/mahabharata.db")


def worker_sanitize_fts5_query(raw: str) -> str:
    r"""
    Exact behavior of MahabharataRepositoryImpl.kt (lines 168-174):
    val cleaned = raw.replace(Regex("[^\\p{L}\\p{N}\\s]"), "").trim()
    val tokens = cleaned.split("\\s+".toRegex()).filter { it.isNotBlank() }
    return tokens.joinToString(" ") { "$it*" }
    """
    cleaned_chars = []
    for ch in raw:
        cat = unicodedata.category(ch)
        if cat.startswith("L") or cat.startswith("N") or ch.isspace():
            cleaned_chars.append(ch)
    cleaned = "".join(cleaned_chars).strip()
    if not cleaned:
        return ""
    tokens = [t for t in re.split(r"\s+", cleaned) if t]
    return " ".join(f"{t}*" for t in tokens)


def corrected_sanitize_fts5_query(raw: str) -> str:
    r"""
    Corrected sanitizer preserving Unicode Marks (\p{M}) for Indic vowel signs, halants/viramas, anusvaras,
    and wrapping tokens in double quotes to prevent syntax errors with FTS operators (AND/OR/NOT).
    """
    cleaned_chars = []
    for ch in raw:
        cat = unicodedata.category(ch)
        if cat.startswith("L") or cat.startswith("M") or cat.startswith("N") or ch.isspace():
            cleaned_chars.append(ch)
    cleaned = "".join(cleaned_chars).strip()
    if not cleaned:
        return ""
    raw_tokens = [t for t in re.split(r"\s+", cleaned) if t]
    if not raw_tokens:
        return ""
    processed = []
    for i, token in enumerate(raw_tokens):
        upper = token.upper()
        if upper == "OR":
            if i > 0 and i < len(raw_tokens) - 1 and processed and processed[-1] != "OR":
                processed.append("OR")
        elif upper in ("AND", "NOT"):
            continue
        else:
            processed.append(f'"{token}"*')
    while processed and processed[-1] == "OR":
        processed.pop()
    while processed and processed[0] == "OR":
        processed.pop(0)
    return " ".join(processed)


def generate_1000_plus_query_corpus() -> List[Tuple[str, str]]:
    """Generates 1,200+ structured benchmark queries across 8 categories."""
    corpus: List[Tuple[str, str]] = []

    # 1. Latin / English (220 queries)
    latin_words = [
        "Narayana", "Kurukshetra", "Duryodhana", "Arjuna", "Pandavas", "Kurus",
        "Drona", "Bhima", "Yudhishthira", "Sanjaya", "Dhritarashtra", "Vyasa",
        "Sarasvati", "Janamejaya", "sacrifice", "virtuous", "ascetics", "hermitage",
        "sacred", "history", "sovereign", "armies", "battle", "bowed", "divine",
        "disciple", "chariot", "arrows", "weapons", "conch", "glory", "warrior",
        "righteousness", "grief", "penance", "liberation", "wisdom", "counsel",
        "kingdom", "valiant", "monarch", "forefathers", "lineage", "majesty"
    ]
    for i, w in enumerate(latin_words):
        corpus.append(("Latin", w))
        corpus.append(("Latin", w.lower()))
        corpus.append(("Latin", w.upper()))
        corpus.append(("Latin", f"{w[:4]}*"))
        corpus.append(("Latin", f"{w} {latin_words[(i+3) % len(latin_words)]}"))

    # 2. Roman IAST Transliteration (210 queries)
    iast_words = [
        "dharmakṣetre", "kurukṣetre", "nārāyaṇaṃ", "namaskṛtya", "naraṃ", "caiva",
        "narottamam", "devīṃ", "sarasvatīṃ", "vyāsaṃ", "jayamudīrayet", "yuyutsavaḥ",
        "māmakāḥ", "pāṇḍavāścaiva", "kimakurvata", "sañjaya", "duryodhanaḥ", "ācāryam",
        "droṇa", "bhīma", "arjuna", "yuyudhāna", "virāṭa", "drupada", "dhṛṣṭaketu",
        "purujit", "kuntibhoja", "yudhiṣṭhira", "dharmaputra", "mahābhārata"
    ]
    for i, w in enumerate(iast_words):
        corpus.append(("IAST", w))
        plain = "".join(c for c in unicodedata.normalize("NFD", w) if unicodedata.category(c) != "Mn")
        corpus.append(("IAST", plain))
        corpus.append(("IAST", f"{w[:4]}*"))
        corpus.append(("IAST", f"{plain[:4]}*"))
        corpus.append(("IAST", f"{w} {iast_words[(i+2) % len(iast_words)]}"))
        corpus.append(("IAST", unicodedata.normalize("NFD", w)))
        corpus.append(("IAST", unicodedata.normalize("NFC", w)))

    # 3. Sanskrit Devanagari (264 queries)
    devanagari_words = [
        "धर्मक्षेत्रे", "कुरुक्षेत्रे", "समवेता", "युयुत्सवः", "मामकाः", "पाण्डवाश्चैव",
        "किमकुर्वत", "सञ्जय", "नारायणं", "नमस्कृत्य", "नरं", "नरोत्तमम्", "देवीं",
        "सरस्वतीं", "व्यासं", "जयमुदीरयेत्", "दृष्ट्वा", "पाण्डवानीकं", "दुर्योधनस्तदा",
        "आचार्यमुपसङ्गम्य", "राजा", "वचनमब्रवीत्", "पश्यैतां", "द्रुपदपुत्रेण", "तव",
        "शिष्येण", "धीमता", "शूरा", "महेष्वासा", "भीमार्जुनसमा", "युधि", "विराटश्च",
        "द्रुपदश्च", "महारथः", "धृष्टकेतुश्चेकितानः", "काशिराजश्च", "वीर्यवान्", "जनमेजयस्य",
        "सर्पसत्रे", "महात्मनः", "समीपे", "पार्थिवेन्द्रस्य", "वैशम्पायनेन", "युधिष्ठिरः"
    ]
    for i, w in enumerate(devanagari_words):
        corpus.append(("Devanagari", w))
        corpus.append(("Devanagari", f"{w}*"))
        corpus.append(("Devanagari", f"{w[:2]}*"))
        corpus.append(("Devanagari", f"{w} {devanagari_words[(i+1) % len(devanagari_words)]}"))
        corpus.append(("Devanagari", unicodedata.normalize("NFC", w)))
        corpus.append(("Devanagari", unicodedata.normalize("NFD", w)))

    # 4. Hindi Translation (145 queries)
    hindi_words = [
        "भगवान", "नारायण", "संजय", "कुरुक्षेत्र", "धर्मभूमि", "अर्जुन", "धृतराष्ट्र",
        "दुर्योधन", "द्रोणाचार्य", "पाण्डव", "सेना", "युद्ध", "पुत्र", "नमस्कार",
        "इतिहास", "ऋषि", "आश्रम", "तपस्या", "कथाएं", "तीर्थ", "राजा", "युधिष्ठिर",
        "वैशम्पायन", "व्यासजी", "सूतजी", "पवित्र", "संग्राम", "आचार्य", "शिष्य"
    ]
    for i, w in enumerate(hindi_words):
        corpus.append(("Hindi", w))
        corpus.append(("Hindi", f"{w}*"))
        corpus.append(("Hindi", f"{w} {hindi_words[(i+2) % len(hindi_words)]}"))
        corpus.append(("Hindi", f"{w[:3]}*"))
        corpus.append(("Hindi", f"हे {w}"))

    # 5. Single-Character Tokens (172 queries)
    single_chars = [
        "क", "ख", "ग", "घ", "च", "छ", "ज", "झ", "ट", "त", "द", "ध", "न", "प", "भ", "म", "य", "र", "ल", "व", "श", "ष", "स", "ह",
        "अ", "आ", "इ", "ई", "उ", "ऊ", "ए", "ऐ", "ओ", "औ",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
    ]
    for ch in single_chars:
        corpus.append(("SingleChar", ch))
        corpus.append(("SingleChar", f"{ch}*"))

    # 6. Large Multi-Word Queries (196 queries)
    multi_phrases = [
        "नारायणं नमस्कृत्य नरं चैव नरोत्तमम् देवीं सरस्वतीं व्यासं",
        "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय",
        "Having bowed down unto Narayana and unto Nara the foremost of male beings",
        "Dhritarashtra said Assembled together on the sacred plain of Kurukshetra",
        "dharmakṣetre kurukṣetre samavetā yuyutsavaḥ māmakāḥ pāṇḍavāścaiva",
        "भगवान नारायण नर श्रेष्ठ नर अर्जुन भगवती सरस्वती और महर्षि वेदव्यास",
        "Behold O teacher this mighty host of the sons of Pandu arrayed in battle",
        "दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा आचार्यमुपसङ्गम्य राजा वचनमब्रवीत्",
        "Ugrasrava the son of Lomaharshana surnamed Sauti well versed in Puranas",
        "सूतजी बोले महामना राजर्षि राजा जनमेजय जो परीक्षित के पुत्र हैं",
        "राज्यं वाऽपि श्रियं वाऽपि सर्वं त्यक्त्वा वने वसन् तपस्तप्स्यामि विपुलं",
        "Renouncing the kingdom and all wealth I shall dwell in the forest"
    ]
    for mp in multi_phrases:
        tokens = mp.split()
        for k in range(3, len(tokens) + 1):
            subphrase = " ".join(tokens[:k])
            corpus.append(("MultiWord", subphrase))
            corpus.append(("MultiWord", f"{subphrase}"))

    # 7. Numerical & Verse Tag Queries (81 queries)
    numerics = [
        "1", "2", "3", "4", "5", "6", "10", "12", "18", "25", "100", "8884", "100000",
        "1.1.1", "1.1.2", "1.1.12", "6.25.1", "6.25.2", "6.25.5", "12.1.1", "12.1.3",
        "1 1", "6 25", "12 1", "Parva 1", "Chapter 25", "Verse 1"
    ]
    for num in numerics:
        corpus.append(("Numeric", num))
        corpus.append(("Numeric", f"{num}*"))
        corpus.append(("Numeric", f"Chapter {num}"))

    # 8. Adversarial Punctuation, Quotes & Syntax Breakers (89 queries)
    adversarial = [
        "\"", "\"\"", "\"\"\"", "\"Narayana", "Narayana\"", "\"Narayana\"",
        "'", "''", "'''", "'Narayana'", "O'Reilly",
        "*", "**", "***", "*Narayana", "Narayana*", "*Narayana*",
        "-", "--", "---", "+", "++", "^", "^^", ":", "::",
        "AND", "OR", "NOT", "NEAR", "NEAR()", "AND OR NOT",
        "col:val", "shlokas:dharma", "shlokas_fts:dharma",
        "(", ")", "()", "(())", "(()", "())",
        "[", "]", "[]", "[[]]", "{", "}", "{}", "{{}}",
        "!", "!=", "@", "#", "$", "%", "&", "&&", "?", "???", "|", "||",
        "\\", "\\\\", "/", "//", "~", "~~", "`", "```",
        "   ", "\t", "\n", "\r\n", " \t \n ",
        "Narayana (Kurukshetra)", "Dharma & Kurukshetra", "Sanjaya: Gita",
        "Arjuna / Bhima", "100% sacred", "vyas#1", "tag@verse",
        "\"\"unclosed \"phrase with quotes", "धर्मक्षेत्रे! @कुरुक्षेत्रे #1",
        "\"धृतराष्ट्र उवाच\"", "'संजय उवाच'", "नारायणं; कुरुक्षेत्र:",
        "dharma AND (kuru OR pandu)", "NOT nonexistent", "(dharmaksetre)"
    ]
    for adv in adversarial:
        corpus.append(("Adversarial", adv))

    return corpus


class Fts5StressBenchmarkTest(unittest.TestCase):
    """Rigorous empirical test suite for FTS5 search performance and correctness."""

    @classmethod
    def setUpClass(cls):
        cls.db = sqlite3.connect(DB_PATH)
        cls.db.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_execute_1000_plus_queries_and_measure_latency(self):
        """
        Benchmark: Execute 1,000+ FTS5 queries across Latin, Devanagari, IAST, Hindi,
        Single-Char, Multi-Word, Numeric, and Adversarial queries.
        Verify p95 < 15.0ms and p99 < 15.0ms.
        """
        corpus = generate_1000_plus_query_corpus()
        self.assertGreaterEqual(len(corpus), 1000, f"Expected >= 1000 queries, got {len(corpus)}")

        cur = self.db.cursor()
        latencies: List[float] = []

        for category, raw_query in corpus:
            safe_query = corrected_sanitize_fts5_query(raw_query)
            if not safe_query:
                t0 = time.perf_counter_ns()
                # Emulate application early return for empty sanitized queries
                _ = []
                t1 = time.perf_counter_ns()
            else:
                t0 = time.perf_counter_ns()
                cur.execute("""
                    SELECT s.id, s.verse_tag, s.sanskrit_devanagari, s.translation_english
                    FROM shlokas s
                    JOIN shlokas_fts fts ON s.id = fts.rowid
                    WHERE shlokas_fts MATCH ?
                    LIMIT 50
                """, (safe_query,))
                _ = cur.fetchall()
                t1 = time.perf_counter_ns()

            elapsed_ms = (t1 - t0) / 1_000_000.0
            latencies.append(elapsed_ms)

        sorted_lats = sorted(latencies)
        n = len(sorted_lats)

        def percentile(p: float) -> float:
            k = (n - 1) * (p / 100.0)
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_lats[int(k)]
            return sorted_lats[int(f)] * (c - k) + sorted_lats[int(c)] * (k - f)

        p50 = percentile(50.0)
        p90 = percentile(90.0)
        p95 = percentile(95.0)
        p99 = percentile(99.0)
        mean_lat = sum(sorted_lats) / n
        min_lat = sorted_lats[0]
        max_lat = sorted_lats[-1]

        print("\n" + "=" * 70)
        print(f"EMPIRICAL BENCHMARK RESULTS ({n} QUERIES EXECUTED)")
        print("=" * 70)
        print(f"Min:  {min_lat:.4f} ms | Mean: {mean_lat:.4f} ms | Median (p50): {p50:.4f} ms")
        print(f"p90:  {p90:.4f} ms | p95:  {p95:.4f} ms | p99:  {p99:.4f} ms | Max: {max_lat:.4f} ms")
        print("=" * 70)

        # STRICT VERIFICATION: p95 and p99 must strictly remain under 15ms
        self.assertLess(p95, 15.0, f"95th percentile latency {p95:.3f}ms exceeded 15.0ms SLA threshold")
        self.assertLess(p99, 15.0, f"99th percentile latency {p99:.3f}ms exceeded 15.0ms SLA threshold")

    def test_02_unicode_normalization_nfc_nfd(self):
        """
        Verify Unicode normalization: Both NFC and NFD representations of Sanskrit Devanagari
        and Roman IAST return identical hits in SQLite FTS5.
        """
        cur = self.db.cursor()
        test_words = ["धर्मक्षेत्रे", "नारायणं", "dharmakṣetre", "nārāyaṇaṃ", "duryodhana"]

        for word in test_words:
            nfc_form = unicodedata.normalize("NFC", word)
            nfd_form = unicodedata.normalize("NFD", word)

            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (f"{nfc_form}*",))
            hits_nfc = set(r[0] for r in cur.fetchall())

            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (f"{nfd_form}*",))
            hits_nfd = set(r[0] for r in cur.fetchall())

            self.assertEqual(hits_nfc, hits_nfd, f"NFC vs NFD divergence on word: '{word}'")
            self.assertGreater(len(hits_nfc), 0, f"Word '{word}' returned 0 hits in both forms")

    def test_03_diacritic_stripping_and_accent_insensitivity(self):
        """
        Verify diacritic stripping: Plain ASCII Latin queries match accented Roman IAST texts.
        E.g. 'dharmaksetre' matches 'dharmakṣetre', 'narayana' matches 'nārāyaṇaṃ'.
        """
        cur = self.db.cursor()
        pairs = [
            ("dharmaksetre*", "dharmakṣetre*"),
            ("narayana*", "nārāyaṇa*"),
            ("kuruksetre*", "kurukṣetre*")
        ]
        for plain_query, accented_query in pairs:
            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (plain_query,))
            plain_hits = set(r[0] for r in cur.fetchall())

            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (accented_query,))
            accented_hits = set(r[0] for r in cur.fetchall())

            self.assertGreater(len(plain_hits), 0, f"Plain query '{plain_query}' had 0 hits")
            self.assertGreater(len(accented_hits), 0, f"Accented query '{accented_query}' had 0 hits")
            self.assertEqual(plain_hits, accented_hits, f"Mismatch between '{plain_query}' and '{accented_query}'")

    def test_04_partial_prefix_matching(self):
        """
        Verify prefix wildcard search (*) returns expected matching shlokas.
        """
        cur = self.db.cursor()
        prefixes = [
            ("धर्म*", ["6.25.1", "12.1.1", "12.1.2"]),
            ("नारा*", ["1.1.1"]),
            ("kuru*", ["1.1.12", "6.25.1", "12.1.1"]),
            ("Duryo*", ["6.25.2"])
        ]
        for prefix, expected_tags in prefixes:
            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (prefix,))
            matched_tags = [r[0] for r in cur.fetchall()]
            for exp in expected_tags:
                self.assertIn(exp, matched_tags, f"Prefix '{prefix}' missing expected verse {exp}")

    def test_05_boundary_adversarial_syntax_breakers(self):
        """
        Verify adversarial edge cases (unmatched quotes, punctuation, operators, numbers)
        are safely handled without SQLite syntax crashes when properly sanitized.
        """
        cur = self.db.cursor()
        adversarial_inputs = [
            "\"unmatched quote",
            "Narayana\"",
            "\"\"\"",
            "***",
            "AND OR NOT",
            "NEAR()",
            ":::",
            "((()))",
            "tag:1.1.1",
            "!@#$%^&*()_+",
            "1.1.1",
            "   "
        ]
        for raw in adversarial_inputs:
            safe = corrected_sanitize_fts5_query(raw)
            if not safe:
                # Early return safe
                continue
            try:
                cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (safe,))
                _ = cur.fetchall()
            except sqlite3.OperationalError as e:
                self.fail(f"Adversarial input '{raw}' produced invalid FTS query '{safe}': {e}")

    def test_06_repository_sanitizer_defect_detection(self):
        """
        CRITICAL AUDIT: Validate that the worker's regex [^\\p{L}\\p{N}\\s] in MahabharataRepositoryImpl.kt
        causes critical false-negatives by stripping Indic vowel signs (matras) and viramas.
        Demonstrate that corrected regex [^\\p{L}\\p{M}\\p{N}\\s] resolves this failure.
        """
        cur = self.db.cursor()
        indic_queries = [
            ("धर्मक्षेत्रे", "6.25.1"),
            ("नारायणं", "1.1.1"),
            ("संजय", "6.25.1"),
            ("कुरुक्षेत्रे", "6.25.1"),
            ("अर्जुन", "1.1.1"), # in Hindi translation
            ("युधिष्ठिर", "12.1.1")
        ]

        defects_found = []
        for word, expected_tag in indic_queries:
            worker_q = worker_sanitize_fts5_query(word)
            corr_q = corrected_sanitize_fts5_query(word)

            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (worker_q,))
            worker_hits = [r[0] for r in cur.fetchall()]

            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (corr_q,))
            corr_hits = [r[0] for r in cur.fetchall()]

            # The worker's sanitized query yields 0 hits because matras/viramas were removed!
            if expected_tag not in worker_hits:
                defects_found.append({
                    "word": word,
                    "worker_query": worker_q,
                    "worker_hits": worker_hits,
                    "corrected_query": corr_q,
                    "corrected_hits": corr_hits,
                    "expected_tag": expected_tag
                })

        # We must confirm that this critical defect exists in worker's logic!
        self.assertGreater(
            len(defects_found), 0,
            "Sanitizer defect was expected but not detected: worker's regex should have stripped Indic matras"
        )
        print(f"\n[CRITICAL FINDING] Confirmed {len(defects_found)} Indic search failures in worker's sanitizer logic:")
        for d in defects_found:
            print(f"  - Input: '{d['word']}' -> Worker Query: '{d['worker_query']}' -> Hits: {d['worker_hits']} (Expected: {d['expected_tag']})")
            print(f"    Corrected Query: '{d['corrected_query']}' -> Hits: {d['corrected_hits']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
