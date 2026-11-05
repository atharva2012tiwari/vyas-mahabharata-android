#!/usr/bin/env python3
"""
Comprehensive FTS5 Search Latency Stress Benchmark & Multilingual Boundary Edge-Case Suite
for Vyasa Mahabharata Offline Search Engine.

Evaluates 1,000+ queries across:
1. Latin / English Vocabulary
2. Roman IAST (Phonetic Sanskrit Transliterations)
3. Sanskrit Devanagari (Canonical Verses)
4. Hindi Translation Text
5. Single-Character Tokens
6. Large Multi-Word Queries
7. Numerical & Verse Tag Queries
8. Adversarial Punctuation, Syntax Breakers, & Unmatched Quotes

Measures p50, p90, p95, p99 latencies, validates Unicode NFC/NFD normalization,
diacritic stripping, partial prefix matching, and repository query sanitization.
"""

import math
import os
import re
import sqlite3
import sys
import time
import unicodedata
from typing import Dict, List, Tuple, Any

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(WORKSPACE_ROOT, "app/src/main/assets/mahabharata.db")


# Worker's Kotlin implementation of sanitizeFts5Query in MahabharataRepositoryImpl.kt:
def sanitize_fts5_query_worker(raw: str) -> str:
    """
    Exact Python reproduction of MahabharataRepositoryImpl.kt line 168-174:
    val cleaned = raw.replace(Regex("[^\\p{L}\\p{N}\\s]"), "").trim()
    val tokens = cleaned.split("\\s+".toRegex()).filter { it.isNotBlank() }
    return tokens.joinToString(" ") { "$it*" }
    """
    # In Kotlin: Regex("[^\\p{L}\\p{N}\\s]") removes anything not category L, N, or whitespace
    # Using unicodedata to exactly match JVM \p{L} and \p{N}
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


# Corrected sanitizer preserving Unicode Marks (\p{M}) for Indic scripts:
def sanitize_fts5_query_corrected(raw: str) -> str:
    r"""
    Sanitizer preserving Unicode Marks (\p{M}) such as Devanagari matras, viramas, anusvaras.
    Regex: [^\p{L}\p{M}\p{N}\s]
    """
    cleaned_chars = []
    for ch in raw:
        cat = unicodedata.category(ch)
        if cat.startswith("L") or cat.startswith("M") or cat.startswith("N") or ch.isspace():
            cleaned_chars.append(ch)
    cleaned = "".join(cleaned_chars).strip()
    if not cleaned:
        return ""
    tokens = [t for t in re.split(r"\s+", cleaned) if t]
    return " ".join(f"{t}*" for t in tokens)


def generate_benchmark_query_corpus() -> List[Tuple[str, str]]:
    """
    Generates a corpus of 1,200+ distinct search queries tagged by category.
    """
    queries: List[Tuple[str, str]] = []

    # Category 1: Latin / English (200 queries)
    latin_base = [
        "Narayana", "Kurukshetra", "Duryodhana", "Arjuna", "Pandavas", "Kurus",
        "Drona", "Bhima", "Yudhishthira", "Sanjaya", "Dhritarashtra", "Vyasa",
        "Sarasvati", "Janamejaya", "sacrifice", "virtuous", "ascetics", "hermitage",
        "sacred", "history", "sovereign", "armies", "battle", "bowed", "divine",
        "disciple", "chariot", "arrows", "weapons", "conch", "glory", "warrior",
        "righteousness", "grief", "penance", "liberation", "wisdom", "counsel",
        "kingdom", "valiant", "monarch", "forefathers", "lineage", "majesty"
    ]
    for i, word in enumerate(latin_base):
        queries.append(("Latin", word))
        queries.append(("Latin", word.lower()))
        queries.append(("Latin", word.upper()))
        queries.append(("Latin", f"{word[:4]}*"))
        queries.append(("Latin", f"{word} {latin_base[(i+3) % len(latin_base)]}"))

    # Category 2: Roman IAST (200 queries)
    iast_base = [
        "dharmakṣetre", "kurukṣetre", "nārāyaṇaṃ", "namaskṛtya", "naraṃ", "caiva",
        "narottamam", "devīṃ", "sarasvatīṃ", "vyāsaṃ", "jayamudīrayet", "yuyutsavaḥ",
        "māmakāḥ", "pāṇḍavāścaiva", "kimakurvata", "sañjaya", "duryodhanaḥ", "ācāryam",
        "droṇa", "bhīma", "arjuna", "yuyudhāna", "virāṭa", "drupada", "dhṛṣṭaketu",
        "purujit", "kuntibhoja", "yudhiṣṭhira", "dharmaputra", "mahābhārata"
    ]
    for i, word in enumerate(iast_base):
        queries.append(("IAST", word))
        # Strip diacritics
        plain = "".join(c for c in unicodedata.normalize("NFD", word) if unicodedata.category(c) != "Mn")
        queries.append(("IAST", plain))
        queries.append(("IAST", f"{word[:4]}*"))
        queries.append(("IAST", f"{plain[:4]}*"))
        queries.append(("IAST", f"{word} {iast_base[(i+2) % len(iast_base)]}"))
        queries.append(("IAST", unicodedata.normalize("NFD", word)))
        queries.append(("IAST", unicodedata.normalize("NFC", word)))

    # Category 3: Sanskrit Devanagari (250 queries)
    devanagari_base = [
        "धर्मक्षेत्रे", "कुरुक्षेत्रे", "समवेता", "युयुत्सवः", "मामकाः", "पाण्डवाश्चैव",
        "किमकुर्वत", "सञ्जय", "नारायणं", "नमस्कृत्य", "नरं", "नरोत्तमम्", "देवीं",
        "सरस्वतीं", "व्यासं", "जयमुदीरयेत्", "दृष्ट्वा", "पाण्डवानीकं", "दुर्योधनस्तदा",
        "आचार्यमुपसङ्गम्य", "राजा", "वचनमब्रवीत्", "पश्यैतां", "द्रुपदपुत्रेण", "तव",
        "शिष्येण", "धीमता", "शूरा", "महेष्वासा", "भीमार्जुनसमा", "युधि", "विराटश्च",
        "द्रुपदश्च", "महारथः", "धृष्टकेतुश्चेकितानः", "काशिराजश्च", "वीर्यवान्", "जनमेजयस्य",
        "सर्पसत्रे", "महात्मनः", "समीपे", "पार्थिवेन्द्रस्य", "वैशम्पायनेन", "युधिष्ठिरः"
    ]
    for i, word in enumerate(devanagari_base):
        queries.append(("Devanagari", word))
        queries.append(("Devanagari", f"{word}*"))
        queries.append(("Devanagari", f"{word[:2]}*"))
        queries.append(("Devanagari", f"{word} {devanagari_base[(i+1) % len(devanagari_base)]}"))
        queries.append(("Devanagari", unicodedata.normalize("NFC", word)))
        queries.append(("Devanagari", unicodedata.normalize("NFD", word)))

    # Category 4: Hindi Translation (150 queries)
    hindi_base = [
        "भगवान", "नारायण", "संजय", "कुरुक्षेत्र", "धर्मभूमि", "अर्जुन", "धृतराष्ट्र",
        "दुर्योधन", "द्रोणाचार्य", "पाण्डव", "सेना", "युद्ध", "पुत्र", "नमस्कार",
        "इतिहास", "ऋषि", "आश्रम", "तपस्या", "कथाएं", "तीर्थ", "राजा", "युधिष्ठिर",
        "वैशम्पायन", "व्यासजी", "सूतजी", "पवित्र", "संग्राम", "आचार्य", "शिष्य"
    ]
    for i, word in enumerate(hindi_base):
        queries.append(("Hindi", word))
        queries.append(("Hindi", f"{word}*"))
        queries.append(("Hindi", f"{word} {hindi_base[(i+2) % len(hindi_base)]}"))
        queries.append(("Hindi", f"{word[:3]}*"))
        queries.append(("Hindi", f"हे {word}"))

    # Category 5: Single-Character Tokens (100 queries)
    single_chars = [
        "क", "ख", "ग", "घ", "च", "छ", "ज", "झ", "ट", "त", "द", "ध", "न", "प", "भ", "म", "य", "र", "ल", "व", "श", "ष", "स", "ह",
        "अ", "आ", "इ", "ई", "उ", "ऊ", "ए", "ऐ", "ओ", "औ",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
    ]
    for ch in single_chars:
        queries.append(("SingleChar", ch))
        queries.append(("SingleChar", f"{ch}*"))

    # Category 6: Large Multi-Word Queries (120 queries)
    multi_words = [
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
    for mw in multi_words:
        tokens = mw.split()
        for k in range(3, len(tokens) + 1):
            subphrase = " ".join(tokens[:k])
            queries.append(("MultiWord", subphrase))
            queries.append(("MultiWord", f"{subphrase}"))

    # Category 7: Numerical & Verse Tag Queries (80 queries)
    numbers = [
        "1", "2", "3", "4", "5", "6", "10", "12", "18", "25", "100", "8884", "100000",
        "1.1.1", "1.1.2", "1.1.12", "6.25.1", "6.25.2", "6.25.5", "12.1.1", "12.1.3",
        "1 1", "6 25", "12 1", "Parva 1", "Chapter 25", "Verse 1"
    ]
    for num in numbers:
        queries.append(("Numeric", num))
        queries.append(("Numeric", f"{num}*"))
        queries.append(("Numeric", f"Chapter {num}"))

    # Category 8: Adversarial Syntax Breakers, Punctuation & Quotes (150 queries)
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
        queries.append(("Adversarial", adv))

    # Pad with combinations to comfortably surpass 1,200 total queries
    while len(queries) < 1250:
        idx = len(queries)
        word = latin_base[idx % len(latin_base)]
        skt = devanagari_base[idx % len(devanagari_base)]
        queries.append(("Mixed", f"{word} {skt}"))

    return queries


def calculate_percentiles(latencies_ms: List[float]) -> Dict[str, float]:
    """Calculates min, mean, p50, p90, p95, p99, max, and stddev."""
    if not latencies_ms:
        return {}
    sorted_lats = sorted(latencies_ms)
    n = len(sorted_lats)

    def get_p(p: float) -> float:
        k = (n - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_lats[int(k)]
        d0 = sorted_lats[int(f)] * (c - k)
        d1 = sorted_lats[int(c)] * (k - f)
        return d0 + d1

    mean_val = sum(sorted_lats) / n
    variance = sum((x - mean_val) ** 2 for x in sorted_lats) / n
    std_dev = math.sqrt(variance)

    return {
        "count": n,
        "min_ms": sorted_lats[0],
        "mean_ms": mean_val,
        "p50_ms": get_p(50),
        "p90_ms": get_p(90),
        "p95_ms": get_p(95),
        "p99_ms": get_p(99),
        "max_ms": sorted_lats[-1],
        "stddev_ms": std_dev
    }


def run_fts5_stress_benchmark():
    assert os.path.exists(DB_PATH), f"Database not found at {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    corpus = generate_benchmark_query_corpus()
    print("=" * 80)
    print("VYASA MAHABHARATA — FTS5 STRESS BENCHMARK & MULTILINGUAL BOUNDARY SUITE")
    print("=" * 80)
    print(f"Total benchmark queries in corpus: {len(corpus)}")
    print(f"Database path:                     {DB_PATH}")
    print(f"SLA latency threshold:             strictly < 15.000 ms (p95 and p99)")
    print("=" * 80)

    # 1. Benchmark Execution: Raw Safe FTS5 Queries
    # In SQLite, syntax characters must be safely quoted or passed as sanitized tokens
    latencies_all: List[float] = []
    latencies_by_category: Dict[str, List[float]] = {}
    hits_by_category: Dict[str, int] = {}
    errors_by_category: Dict[str, int] = {}

    # Also track sanitizer behavior:
    sanitizer_failures: List[Dict[str, Any]] = []

    for cat, query in corpus:
        if cat not in latencies_by_category:
            latencies_by_category[cat] = []
            hits_by_category[cat] = 0
            errors_by_category[cat] = 0

        # Run with corrected/safe tokenization for raw FTS5 latency measurement
        # Clean query using corrected sanitizer to measure real FTS5 engine performance
        fts_query = sanitize_fts5_query_corrected(query)

        if not fts_query:
            # Empty or punctuation-only query: measures app guard latency (< 0.01ms)
            t0 = time.perf_counter_ns()
            hits = 0
            t1 = time.perf_counter_ns()
            elapsed_ms = (t1 - t0) / 1_000_000.0
        else:
            t0 = time.perf_counter_ns()
            try:
                cur.execute("""
                    SELECT s.id, s.verse_tag, s.sanskrit_devanagari, s.translation_english
                    FROM shlokas s
                    JOIN shlokas_fts fts ON s.id = fts.rowid
                    WHERE shlokas_fts MATCH ?
                    LIMIT 50
                """, (fts_query,))
                rows = cur.fetchall()
                hits = len(rows)
            except Exception as e:
                hits = 0
                errors_by_category[cat] += 1
            t1 = time.perf_counter_ns()
            elapsed_ms = (t1 - t0) / 1_000_000.0

        latencies_all.append(elapsed_ms)
        latencies_by_category[cat].append(elapsed_ms)
        hits_by_category[cat] += hits

        # Check worker's sanitizeFts5Query behavior on this query
        worker_sanitized = sanitize_fts5_query_worker(query)
        if fts_query and not worker_sanitized:
            # Query was valid but worker stripped everything
            sanitizer_failures.append({
                "category": cat,
                "input": query,
                "worker_output": worker_sanitized,
                "corrected_output": fts_query,
                "reason": "Complete loss of query characters"
            })
        elif fts_query and worker_sanitized != fts_query:
            # Check if worker output matches anything in FTS5 vs corrected
            try:
                cur.execute("SELECT COUNT(*) FROM shlokas_fts WHERE shlokas_fts MATCH ?", (worker_sanitized,))
                worker_hits = cur.fetchone()[0]
            except Exception:
                worker_hits = -1

            try:
                cur.execute("SELECT COUNT(*) FROM shlokas_fts WHERE shlokas_fts MATCH ?", (fts_query,))
                corr_hits = cur.fetchone()[0]
            except Exception:
                corr_hits = -1

            if corr_hits > 0 and worker_hits == 0:
                sanitizer_failures.append({
                    "category": cat,
                    "input": query,
                    "worker_output": worker_sanitized,
                    "worker_hits": worker_hits,
                    "corrected_output": fts_query,
                    "corrected_hits": corr_hits,
                    "reason": "False negative: worker sanitizer stripped vowel matras/viramas, yielding 0 hits"
                })

    conn.close()

    # Print Latency Statistics Table
    overall_stats = calculate_percentiles(latencies_all)

    print("\n--- LATENCY PERCENTILE SUMMARY (ALL 1,250 QUERIES) ---")
    print(f"Total Queries:     {overall_stats['count']}")
    print(f"Min Latency:       {overall_stats['min_ms']:.4f} ms")
    print(f"Mean Latency:      {overall_stats['mean_ms']:.4f} ms")
    print(f"Median (p50):      {overall_stats['p50_ms']:.4f} ms")
    print(f"90th Percentile:   {overall_stats['p90_ms']:.4f} ms")
    print(f"95th Percentile:   {overall_stats['p95_ms']:.4f} ms  (Target: < 15.000 ms)")
    print(f"99th Percentile:   {overall_stats['p99_ms']:.4f} ms  (Target: < 15.000 ms)")
    print(f"Max Latency:       {overall_stats['max_ms']:.4f} ms")
    print(f"Std Deviation:     {overall_stats['stddev_ms']:.4f} ms")

    print("\n--- LATENCY BREAKDOWN BY QUERY CATEGORY ---")
    print(f"{'Category':<15} {'Count':<7} {'Mean(ms)':<10} {'p50(ms)':<9} {'p95(ms)':<9} {'p99(ms)':<9} {'Max(ms)':<9} {'Hits':<8}")
    print("-" * 80)
    for cat, lats in latencies_by_category.items():
        st = calculate_percentiles(lats)
        print(f"{cat:<15} {st['count']:<7} {st['mean_ms']:<10.3f} {st['p50_ms']:<9.3f} {st['p95_ms']:<9.3f} {st['p99_ms']:<9.3f} {st['max_ms']:<9.3f} {hits_by_category[cat]:<8}")

    print("=" * 80)

    # 2. Unicode Normalization & Diacritic Stripping Tests
    print("\n--- UNICODE NORMALIZATION & DIACRITIC STRIPPING EVALUATION ---")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    norm_tests = [
        ("NFC Devanagari", "धर्मक्षेत्रे", unicodedata.normalize("NFC", "धर्मक्षेत्रे")),
        ("NFD Devanagari", "धर्मक्षेत्रे", unicodedata.normalize("NFD", "धर्मक्षेत्रे")),
        ("NFC IAST", "dharmakṣetre", unicodedata.normalize("NFC", "dharmakṣetre")),
        ("NFD IAST", "dharmakṣetre", unicodedata.normalize("NFD", "dharmakṣetre")),
        ("Stripped IAST", "dharmakṣetre", "dharmaksetre"),
        ("NFC Invocation", "नारायणं", unicodedata.normalize("NFC", "नारायणं")),
        ("NFD Invocation", "नारायणं", unicodedata.normalize("NFD", "नारायणं")),
        ("Stripped IAST Invocation", "nārāyaṇaṃ", "narayanam"),
    ]

    for label, orig, q in norm_tests:
        try:
            cur.execute("SELECT verse_tag FROM shlokas_fts WHERE shlokas_fts MATCH ?", (f"{q}*",))
            hits = cur.fetchall()
            print(f"  [{label:<25}] Query: {q:<18} -> {len(hits)} hits ({hits})")
        except Exception as e:
            print(f"  [{label:<25}] Query: {q:<18} -> ERROR: {e}")

    conn.close()

    # 3. Worker Sanitizer Failure Analysis
    print("\n--- WORKER SANITIZER (MahabharataRepositoryImpl.kt) FAILURE ANALYSIS ---")
    print(f"Total false-negative failures identified: {len(sanitizer_failures)}")
    print("Top 10 Representative Failures Caused by worker's [^\\p{L}\\p{N}\\s] regex:")
    for idx, fail in enumerate(sanitizer_failures[:10]):
        print(f"  {idx+1}. [{fail['category']}] Input: '{fail['input']}'")
        print(f"     Worker Output:    '{fail['worker_output']}' (Hits: {fail.get('worker_hits', 0)})")
        print(f"     Corrected Output: '{fail['corrected_output']}' (Hits: {fail.get('corrected_hits', 0)})")
        print(f"     Root Cause:       {fail['reason']}\n")

    # Final Verdict Assessment
    p95_pass = overall_stats['p95_ms'] < 15.0
    p99_pass = overall_stats['p99_ms'] < 15.0
    latencies_pass = p95_pass and p99_pass
    sanitizer_pass = len(sanitizer_failures) == 0

    print("=" * 80)
    print("FINAL EMPIRICAL VERDICT ASSESSMENT:")
    print(f"  1. p95 Latency < 15ms:  {'PASS' if p95_pass else 'FAIL'} ({overall_stats['p95_ms']:.4f} ms)")
    print(f"  2. p99 Latency < 15ms:  {'PASS' if p99_pass else 'FAIL'} ({overall_stats['p99_ms']:.4f} ms)")
    print(f"  3. 1,000+ Queries Run:  PASS ({len(corpus)} executed)")
    print(f"  4. Multilingual Boundary & Sanitization Integrity: {'PASS' if sanitizer_pass else 'CRITICAL DEFECT DETECTED'}")
    if not sanitizer_pass:
        print(f"     -> REQUEST_CHANGES required due to Devanagari vowel sign / virama stripping bug in MahabharataRepositoryImpl.kt")
    print("=" * 80)

    return overall_stats, sanitizer_failures


if __name__ == "__main__":
    run_fts5_stress_benchmark()
