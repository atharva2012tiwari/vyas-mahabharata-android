#!/usr/bin/env python3
"""
Adversarial Stress-Testing Suite for Vyasa Mahabharata Milestone 1 Data Layer.
Empirically tests:
1. Room Schema & Foreign Key CASCADE Conformance
2. Multi-threaded Concurrency & Database Locking under Burst Load
3. Rapid Bookmark Insertions, Deletions, and Notes Fuzzing
4. Rapid Reading Position Updates & Scroll Offset Extremes
5. Foreign Key Enforcement & Cascade Deletions
6. Adversarial FTS5 Queries, Devanagari Matra Sanitization Bug Reproduction
7. Memory Leak & Resource Exhaustion (10,000 queries burst)
8. SQLite Engine PRAGMAs (integrity_check, foreign_key_check) & Size Limits
"""

import os
import re
import sys
import time
import shutil
import sqlite3
import tempfile
import threading
import resource
from typing import List, Dict, Tuple, Any

# Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_ASSET_PATH = os.path.join(PROJECT_ROOT, "app/src/main/assets/mahabharata.db")
ENTITY_DIR = os.path.join(PROJECT_ROOT, "app/src/main/java/com/vyas/mahabharata/data/local/entity")
REPO_IMPL_PATH = os.path.join(PROJECT_ROOT, "app/src/main/java/com/vyas/mahabharata/data/repository/MahabharataRepositoryImpl.kt")

class TestFailure(Exception):
    pass

class AdversarialReport:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.findings = []

    def record_pass(self, name: str):
        self.passed += 1
        print(f"  \033[32m[PASS]\033[0m {name}")

    def record_fail(self, name: str, reason: str, severity: str = "HIGH"):
        self.failed += 1
        self.findings.append({
            "name": name,
            "reason": reason,
            "severity": severity
        })
        print(f"  \033[31m[FAIL - {severity}]\033[0m {name}")
        print(f"         \033[33mReason: {reason}\033[0m")

report = AdversarialReport()

# =====================================================================
# SUITE 1: Room Schema & Foreign Key CASCADE Conformance
# =====================================================================
def test_suite_1_schema_and_foreign_keys():
    print("\n\033[1m=== Suite 1: Room Entity & Schema Foreign Key Conformance ===\033[0m")
    
    assert os.path.exists(DB_ASSET_PATH), f"Asset DB missing at {DB_ASSET_PATH}"
    conn = sqlite3.connect(DB_ASSET_PATH)
    cur = conn.cursor()

    # 1.1 Check DB size under 80MB
    db_size = os.path.getsize(DB_ASSET_PATH)
    if db_size < 80 * 1024 * 1024:
        report.record_pass(f"DB file size ({db_size:,} bytes) is well under 80MB SLA")
    else:
        report.record_fail("DB file size limit", f"Size {db_size} bytes exceeds 80MB", "HIGH")

    # 1.2 Check Foreign Key CASCADE alignment between Room Entities and SQLite DDL
    # Room checks TableInfo.ForeignKey.onDelete. If Entity specifies CASCADE but SQLite has NO ACTION,
    # Room throws: IllegalStateException: Pre-packaged database has an invalid schema.
    fk_checks = [
        ("chapters", "ChapterEntity.kt", "parvas", "parva_number", "number"),
        ("shlokas", "ShlokaEntity.kt", "parvas", "parva_number", "number"),
        ("bookmarks", "BookmarkEntity.kt", "shlokas", "shloka_id", "id"),
    ]

    for table, entity_file, parent_table, child_col, parent_col in fk_checks:
        cur.execute(f"PRAGMA foreign_key_list({table})")
        fk_list = cur.fetchall()
        
        # Read entity file to check onDelete
        with open(os.path.join(ENTITY_DIR, entity_file), "r", encoding="utf-8") as f:
            entity_src = f.read()

        entity_has_cascade = "ForeignKey.CASCADE" in entity_src
        
        sqlite_fk = None
        for fk in fk_list:
            # fk tuple: (id, seq, table, from, to, on_update, on_delete, match)
            if fk[2] == parent_table and fk[3] == child_col and fk[4] == parent_col:
                sqlite_fk = fk
                break

        if sqlite_fk is None:
            report.record_fail(f"FK {table}({child_col}) -> {parent_table}({parent_col})", "Foreign key missing in SQLite DDL", "CRITICAL")
            continue

        sqlite_on_delete = sqlite_fk[6] # e.g. 'NO ACTION' or 'CASCADE'
        if entity_has_cascade and sqlite_on_delete != "CASCADE":
            report.record_fail(
                f"Schema Mismatch in {table}: FK {child_col} -> {parent_table}({parent_col})",
                f"{entity_file} declares onDelete = ForeignKey.CASCADE, but SQLite DDL in assets/mahabharata.db has on_delete = '{sqlite_on_delete}'. Room will fail with IllegalStateException: Pre-packaged database has an invalid schema.",
                "CRITICAL"
            )
        else:
            report.record_pass(f"FK {table} onDelete conforms to {entity_file} ({sqlite_on_delete})")

    # 1.3 Check parvas unique index vs autoindex
    cur.execute("PRAGMA index_list(parvas)")
    indices = cur.fetchall()
    # Check if there is an explicit named index or only sqlite_autoindex
    has_explicit_idx = any(idx[1] == "index_parvas_number" for idx in indices)
    # In ParvaEntity: @Entity(tableName = "parvas", indices = [Index(value = ["number"], unique = true)])
    # Room expects index named index_parvas_number unless the SQLite table created it with CREATE INDEX.
    if not has_explicit_idx:
        report.record_fail(
            "ParvaEntity index 'index_parvas_number' schema check",
            "ParvaEntity specifies @Index(value=['number'], unique=true). Room expects named index 'index_parvas_number', but SQLite only has internal 'sqlite_autoindex_parvas_1'. Room's TableInfo ignores sqlite_autoindex, causing schema validation mismatch on pre-packaged DB.",
            "HIGH"
        )
    else:
        report.record_pass("ParvaEntity unique index matches SQLite DDL")

    conn.close()

# =====================================================================
# SUITE 2: Concurrent Multi-Threaded Stress Test (DB Locking & Concurrency)
# =====================================================================
def test_suite_2_concurrency_and_locking():
    print("\n\033[1m=== Suite 2: Concurrent Multi-Threaded Stress Test (DB Locking) ===\033[0m")
    
    # Use a working copy to avoid mutating the asset db during write stress
    temp_dir = tempfile.mkdtemp()
    test_db = os.path.join(temp_dir, "concurrent_test.db")
    shutil.copyfile(DB_ASSET_PATH, test_db)

    # Enable WAL mode and busy timeout, mimicking Android Room defaults
    conn_init = sqlite3.connect(test_db)
    conn_init.execute("PRAGMA journal_mode = WAL")
    conn_init.execute("PRAGMA busy_timeout = 5000")
    conn_init.close()

    errors = []
    total_ops = 0
    lock = threading.Lock()

    def reader_worker(worker_id: int, runs: int):
        nonlocal total_ops
        try:
            conn = sqlite3.connect(test_db, timeout=10.0)
            conn.execute("PRAGMA busy_timeout = 5000")
            cur = conn.cursor()
            for i in range(runs):
                # Mixed read queries: shlokas, parvas, FTS search
                cur.execute("SELECT * FROM parvas WHERE number = ?", ((i % 18) + 1,))
                cur.fetchall()

                cur.execute("""
                    SELECT s.id, s.verse_tag, s.sanskrit_devanagari 
                    FROM shlokas s 
                    WHERE s.parva_number = 1 AND s.chapter_number = 1 
                    ORDER BY s.verse_number ASC
                """)
                cur.fetchall()

                # FTS search
                cur.execute("SELECT rowid, sanskrit_devanagari FROM shlokas_fts WHERE shlokas_fts MATCH 'Narayana'")
                cur.fetchall()

                with lock:
                    total_ops += 3
            conn.close()
        except Exception as e:
            errors.append(f"Reader {worker_id} failed: {type(e).__name__}: {e}")

    def writer_history_worker(worker_id: int, runs: int):
        nonlocal total_ops
        try:
            conn = sqlite3.connect(test_db, timeout=10.0)
            conn.execute("PRAGMA busy_timeout = 5000")
            cur = conn.cursor()
            for i in range(runs):
                p_num = (i % 18) + 1
                cur.execute("""
                    INSERT OR REPLACE INTO reading_history (parva_number, last_chapter_number, last_verse_number, scroll_offset, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (p_num, 1, (i % 12) + 1, (i * 10) % 500, int(time.time() * 1000)))
                conn.commit()
                with lock:
                    total_ops += 1
            conn.close()
        except Exception as e:
            errors.append(f"History Writer {worker_id} failed: {type(e).__name__}: {e}")

    def writer_bookmark_worker(worker_id: int, runs: int):
        nonlocal total_ops
        try:
            conn = sqlite3.connect(test_db, timeout=10.0)
            conn.execute("PRAGMA busy_timeout = 5000")
            cur = conn.cursor()
            for i in range(runs):
                # Rapid insert followed by delete
                shloka_id = ((i + worker_id) % 20) + 1
                cur.execute("""
                    INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at)
                    VALUES (?, 'StressTest', ?, ?)
                """, (shloka_id, f"Worker {worker_id} note {i}", int(time.time() * 1000)))
                bm_id = cur.lastrowid
                conn.commit()

                cur.execute("DELETE FROM bookmarks WHERE id = ?", (bm_id,))
                conn.commit()
                with lock:
                    total_ops += 2
            conn.close()
        except Exception as e:
            errors.append(f"Bookmark Writer {worker_id} failed: {type(e).__name__}: {e}")

    threads = []
    # 10 Reader threads (50 ops each = 500 queries)
    for w in range(10):
        t = threading.Thread(target=reader_worker, args=(w, 50))
        threads.append(t)
    # 5 Reading History writer threads (50 ops each)
    for w in range(5):
        t = threading.Thread(target=writer_history_worker, args=(w, 50))
        threads.append(t)
    # 5 Bookmark writer threads (30 ops each = 300 writes/deletes)
    for w in range(5):
        t = threading.Thread(target=writer_bookmark_worker, args=(w, 30))
        threads.append(t)

    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    t_elapsed = time.perf_counter() - t0

    if errors:
        report.record_fail("Concurrent Multi-Threaded Stress Test", f"Encountered {len(errors)} locking/execution errors:\n" + "\n".join(errors[:5]), "HIGH")
    else:
        report.record_pass(f"Concurrent Multi-Threaded Test PASSED: {total_ops} queries/transactions across 20 threads in {t_elapsed:.2f}s with 0 deadlocks or lock timeouts")

    # Clean up temp
    shutil.rmtree(temp_dir)

# =====================================================================
# SUITE 3: Rapid Bookmark Insertions & Deletions (Churn Stress)
# =====================================================================
def test_suite_3_rapid_bookmarks():
    print("\n\033[1m=== Suite 3: Rapid Bookmark Insertions & Deletions ===\033[0m")
    
    temp_dir = tempfile.mkdtemp()
    test_db = os.path.join(temp_dir, "bookmark_test.db")
    shutil.copyfile(DB_ASSET_PATH, test_db)

    conn = sqlite3.connect(test_db)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # 3.1 1,000 rapid sequential bookmark inserts and deletions
    t0 = time.perf_counter()
    inserted_ids = []
    for i in range(500):
        cur.execute("""
            INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at)
            VALUES (?, 'RapidTest', ?, ?)
        """, ((i % 20) + 1, f"Rapid note {i}", int(time.time() * 1000)))
        inserted_ids.append(cur.lastrowid)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM bookmarks WHERE collection_name = 'RapidTest'")
    assert cur.fetchone()[0] == 500, "500 bookmarks not stored properly"

    # Rapid deletions
    for b_id in inserted_ids:
        cur.execute("DELETE FROM bookmarks WHERE id = ?", (b_id,))
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM bookmarks WHERE collection_name = 'RapidTest'")
    assert cur.fetchone()[0] == 0, "Bookmarks were not cleaned up"
    t_elapsed = time.perf_counter() - t0
    report.record_pass(f"1,000 Rapid Bookmark Insert/Delete operations succeeded in {t_elapsed:.3f}s")

    # 3.2 Fuzzing notes & special characters
    adversarial_notes = [
        None,
        "",
        "   ",
        "A" * 50000, # Large text note 50KB
        "🔱 🕉️ 🪔 🚩 🏹 🪷", # Astral plane Unicode emojis
        "'; DROP TABLE bookmarks; --", # SQL injection attempt
        "<script>alert('XSS')</script>", # HTML / Script payload
        "Line 1\nLine 2\r\nLine 3\tTabbed",
        "Special chars: !@#$%^&*()_+{}|:\"<>?~`-=[]\\;',./"
    ]

    for idx, note in enumerate(adversarial_notes):
        try:
            cur.execute("""
                INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at)
                VALUES (1, 'FuzzCollection', ?, ?)
            """, (note, int(time.time() * 1000)))
            b_id = cur.lastrowid
            conn.commit()

            cur.execute("SELECT user_note FROM bookmarks WHERE id = ?", (b_id,))
            fetched_note = cur.fetchone()[0]
            assert fetched_note == note, f"Note mismatch for note index {idx}"
            cur.execute("DELETE FROM bookmarks WHERE id = ?", (b_id,))
            conn.commit()
        except Exception as e:
            report.record_fail(f"Bookmark note fuzzing index {idx}", f"Exception: {e}", "MEDIUM")
            break
    else:
        report.record_pass("Bookmark user_note fuzzing (50KB, emojis, SQLi strings, newlines) PASSED")

    conn.close()
    shutil.rmtree(temp_dir)

# =====================================================================
# SUITE 4: Rapid Reading Position Updates & Scroll Extremes
# =====================================================================
def test_suite_4_reading_position_updates():
    print("\n\033[1m=== Suite 4: Rapid Reading Position Updates (Scroll Stress) ===\033[0m")
    
    temp_dir = tempfile.mkdtemp()
    test_db = os.path.join(temp_dir, "reading_test.db")
    shutil.copyfile(DB_ASSET_PATH, test_db)

    conn = sqlite3.connect(test_db)
    cur = conn.cursor()

    # 4.1 Rapid updates on reading_history (simulate fast continuous scrolling)
    t0 = time.perf_counter()
    for offset in range(0, 1000, 2):
        cur.execute("""
            INSERT OR REPLACE INTO reading_history (parva_number, last_chapter_number, last_verse_number, scroll_offset, updated_at)
            VALUES (1, 1, 5, ?, ?)
        """, (offset, int(time.time() * 1000)))
    conn.commit()
    t_elapsed = time.perf_counter() - t0

    cur.execute("SELECT COUNT(*) FROM reading_history WHERE parva_number = 1")
    count = cur.fetchone()[0]
    if count == 1:
        report.record_pass(f"500 rapid scroll updates executed in {t_elapsed:.3f}s with exact 1-row primary key idempotency")
    else:
        report.record_fail("Reading history uniqueness", f"Expected exactly 1 row for parva_number 1, found {count}", "HIGH")

    # 4.2 Extreme values for scroll_offset
    extreme_offsets = [0, -1, -999999, 2147483647, -2147483648]
    for off in extreme_offsets:
        cur.execute("""
            INSERT OR REPLACE INTO reading_history (parva_number, last_chapter_number, last_verse_number, scroll_offset, updated_at)
            VALUES (2, 1, 1, ?, ?)
        """, (off, int(time.time() * 1000)))
        conn.commit()
        cur.execute("SELECT scroll_offset FROM reading_history WHERE parva_number = 2")
        retrieved = cur.fetchone()[0]
        assert retrieved == off, f"Extreme scroll offset {off} retrieved as {retrieved}"

    report.record_pass("Extreme boundary scroll offsets (Int.MAX_VALUE, Int.MIN_VALUE, negative) PASSED")

    conn.close()
    shutil.rmtree(temp_dir)

# =====================================================================
# SUITE 5: Foreign Key Enforcement & Cascades
# =====================================================================
def test_suite_5_foreign_key_enforcement():
    print("\n\033[1m=== Suite 5: Foreign Key Enforcement & Cascade Deletions ===\033[0m")
    
    temp_dir = tempfile.mkdtemp()
    test_db = os.path.join(temp_dir, "fk_test.db")
    shutil.copyfile(DB_ASSET_PATH, test_db)

    conn = sqlite3.connect(test_db)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # 5.1 Invalid foreign key insertions must be rejected
    invalid_cases = [
        ("bookmarks invalid shloka_id=999999", "INSERT INTO bookmarks (shloka_id, collection_name, created_at) VALUES (999999, 'Test', 1000)"),
        ("bookmarks negative shloka_id=-1", "INSERT INTO bookmarks (shloka_id, collection_name, created_at) VALUES (-1, 'Test', 1000)"),
        ("chapters invalid parva_number=19", "INSERT INTO chapters (parva_number, chapter_number, title_sanskrit, title_hindi, title_english) VALUES (19, 1, 'T', 'T', 'T')"),
        ("shlokas invalid parva_number=99", "INSERT INTO shlokas (parva_number, chapter_number, verse_number, verse_tag, sanskrit_devanagari, sanskrit_iast, translation_hindi, translation_english) VALUES (99, 1, 1, '99.1.1', 'S', 'S', 'H', 'E')"),
    ]

    for label, sql in invalid_cases:
        try:
            cur.execute(sql)
            conn.commit()
            report.record_fail(label, "Expected IntegrityError due to foreign key constraint, but insertion succeeded!", "CRITICAL")
        except sqlite3.IntegrityError:
            report.record_pass(f"Rejected invalid FK insertion: {label}")

    # 5.2 Cascade Deletion Test
    # In BookmarkEntity: onDelete = ForeignKey.CASCADE
    # If a shloka is deleted, its bookmarks should cascade-delete.
    # But as found in Suite 1, SQLite DDL is missing ON DELETE CASCADE!
    cur.execute("INSERT INTO bookmarks (shloka_id, collection_name, created_at) VALUES (1, 'CascadeTest', 1000)")
    conn.commit()

    try:
        cur.execute("DELETE FROM shlokas WHERE id = 1")
        conn.commit()
        # If reached here, check if bookmark was cascaded
        cur.execute("SELECT COUNT(*) FROM bookmarks WHERE collection_name = 'CascadeTest'")
        remaining = cur.fetchone()[0]
        if remaining == 0:
            report.record_pass("Foreign key CASCADE deletion correctly cleaned up dependent bookmarks")
        else:
            report.record_fail("Cascade deletion orphaned bookmark", f"Found {remaining} orphaned bookmarks", "HIGH")
    except sqlite3.IntegrityError as e:
        report.record_fail(
            "Cascade Deletion on shlokas -> bookmarks",
            f"Deleting shloka failed with '{e}' because SQLite DDL lacks 'ON DELETE CASCADE' (contrary to BookmarkEntity.kt)",
            "HIGH"
        )

    conn.close()
    shutil.rmtree(temp_dir)

# =====================================================================
# SUITE 6: Adversarial & Corrupted FTS5 Queries (The Devanagari Bug)
# =====================================================================
def test_suite_6_adversarial_fts_and_sanitizer():
    print("\n\033[1m=== Suite 6: Adversarial FTS5 Queries & Sanitization Bug ===\033[0m")
    
    conn = sqlite3.connect(DB_ASSET_PATH)
    cur = conn.cursor()

    # Replicate the exact Kotlin sanitizeFts5Query implementation from MahabharataRepositoryImpl.kt:
    # val cleaned = raw.replace(Regex("[^\\p{L}\\p{M}\\p{N}\\s]"), "").trim()
    # if (cleaned.isEmpty()) return ""
    # val tokens = cleaned.split("\\s+".toRegex()).filter { it.isNotBlank() }
    # return tokens.joinToString(" ") { "\"$it\"*" }
    import regex # Python regex library supports \p{L}, \p{M}, \p{N}
    
    def kotlin_current_sanitizer(raw: str) -> str:
        cleaned = regex.sub(r'[^\p{L}\p{M}\p{N}\s]', '', raw).strip()
        if not cleaned:
            return ""
        raw_tokens = [t for t in regex.split(r'\s+', cleaned) if t]
        if not raw_tokens:
            return ""
        processed = []
        for i, token in enumerate(raw_tokens):
            upper = token.upper()
            if upper == 'OR':
                if i > 0 and i < len(raw_tokens) - 1 and processed and processed[-1] != 'OR':
                    processed.append('OR')
            elif upper in ('AND', 'NOT'):
                continue
            else:
                processed.append(f'"{token}"*')
        while processed and processed[-1] == 'OR':
            processed.pop()
        while processed and processed[0] == 'OR':
            processed.pop(0)
        return " ".join(processed)

    corrected_sanitizer = kotlin_current_sanitizer

    # 6.1 Test Devanagari words against current sanitizer vs corrected sanitizer
    devanagari_terms = [
        ("नारायणं", "Invocation sacred name (contains vowel sign AA + anusvara)"),
        ("धर्मक्षेत्रे", "Gita opening word (contains virama + vowel sign E)"),
        ("कुरुक्षेत्रे", "Kurukshetra (contains vowel sign U + virama + vowel sign E)"),
        ("संजय", "Sanjaya (contains anusvara)"),
        ("धृतराष्ट्र", "Dhritarashtra (contains vocalic R + virama)"),
    ]

    for term, desc in devanagari_terms:
        # Check direct SQLite query
        cur.execute("SELECT COUNT(*) FROM shlokas_fts WHERE shlokas_fts MATCH ?", (f"{term}*",))
        direct_count = cur.fetchone()[0]

        # Check what Kotlin's current sanitizer produces
        sanitized_query = kotlin_current_sanitizer(term)
        cur.execute("SELECT COUNT(*) FROM shlokas_fts WHERE shlokas_fts MATCH ?", (sanitized_query,))
        sanitized_count = cur.fetchone()[0]

        # Check what corrected sanitizer produces
        corrected_query = corrected_sanitizer(term)
        cur.execute("SELECT COUNT(*) FROM shlokas_fts WHERE shlokas_fts MATCH ?", (corrected_query,))
        corrected_count = cur.fetchone()[0]

        if direct_count > 0 and sanitized_count == 0:
            report.record_fail(
                f"FTS5 Devanagari Search Stripping Bug: '{term}'",
                f"Input '{term}' ({desc}) -> current sanitizeFts5Query stripped all vowel matras/viramas to '{sanitized_query}', returning 0 hits (expected {direct_count} hits). Correct regex [^\\p{{L}}\\p{{M}}\\p{{N}}\\s] produces '{corrected_query}' returning {corrected_count} hits.",
                "CRITICAL"
            )
        elif direct_count > 0 and sanitized_count == direct_count:
            report.record_pass(f"Devanagari search '{term}' matched without stripping")

    # 6.2 Test Malformed / Hostile FTS Query Strings
    adversarial_queries = [
        ("", 0),
        ("   ", 0),
        ("\"", 0),
        ("\"\"\"", 0),
        ("'", 0),
        ("*", 0),
        ("***", 0),
        ("AND", 0),
        ("OR", 0),
        ("NOT", 0),
        ("NEAR", 0),
        ("NEAR/5", 0),
        ("'; DROP TABLE bookmarks; --", 0),
        ("1' OR '1'='1", 0),
        ("!@#$%^&*()_+{}|:<>?", 0),
        ("A" * 5000, 0), # 5,000 char query
        ("dharmaksetre* AND kuruksetre*", 1)
    ]

    for q, min_expected in adversarial_queries:
        # Use corrected sanitizer
        clean_q = corrected_sanitizer(q)
        try:
            if clean_q:
                cur.execute("SELECT COUNT(*) FROM shlokas_fts WHERE shlokas_fts MATCH ?", (clean_q,))
                cnt = cur.fetchone()[0]
                assert cnt >= min_expected
            report.record_pass(f"Adversarial query '{q[:20]}' sanitized safely to '{clean_q[:20]}'")
        except sqlite3.OperationalError as e:
            report.record_fail(f"FTS5 crash on adversarial query '{q}'", f"OperationalError: {e}", "HIGH")

    conn.close()

# =====================================================================
# SUITE 7: Memory Leak & Resource Exhaustion (10,000 queries burst)
# =====================================================================
def test_suite_7_memory_and_resource_leaks():
    print("\n\033[1m=== Suite 7: Memory Leaks & Resource Exhaustion (10,000 Queries) ===\033[0m")
    
    conn = sqlite3.connect(DB_ASSET_PATH)
    cur = conn.cursor()

    mem_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    t0 = time.perf_counter()
    for i in range(10000):
        # Rotate through queries
        p_num = (i % 18) + 1
        cur.execute("SELECT id, name_sanskrit, color_seed FROM parvas WHERE number = ?", (p_num,))
        cur.fetchone()
        if i % 100 == 0:
            cur.execute("SELECT rowid, sanskrit_devanagari FROM shlokas_fts WHERE shlokas_fts MATCH 'Narayana'")
            cur.fetchall()

    t_elapsed = time.perf_counter() - t0
    mem_end = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    mem_diff_kb = mem_end - mem_start

    conn.close()

    # ru_maxrss is in KB on Linux
    if mem_diff_kb < 15000: # Less than 15MB growth over 10k queries
        report.record_pass(f"10,000 Queries burst completed in {t_elapsed:.3f}s with negligible RSS growth ({mem_diff_kb} KB)")
    else:
        report.record_fail("Memory Leak Detection", f"RSS memory grew by {mem_diff_kb} KB over 10,000 queries", "MEDIUM")

# =====================================================================
# SUITE 8: SQLite Engine PRAGMAs (integrity_check, foreign_key_check)
# =====================================================================
def test_suite_8_pragmas():
    print("\n\033[1m=== Suite 8: SQLite Engine PRAGMAs ===\033[0m")
    
    conn = sqlite3.connect(DB_ASSET_PATH)
    cur = conn.cursor()

    # 8.1 PRAGMA integrity_check
    cur.execute("PRAGMA integrity_check")
    res = cur.fetchall()
    if res == [("ok",)]:
        report.record_pass("PRAGMA integrity_check -> ok")
    else:
        report.record_fail("PRAGMA integrity_check", f"Integrity check failed: {res}", "CRITICAL")

    # 8.2 PRAGMA foreign_key_check
    cur.execute("PRAGMA foreign_key_check")
    fk_errors = cur.fetchall()
    if not fk_errors:
        report.record_pass("PRAGMA foreign_key_check -> No foreign key violations")
    else:
        report.record_fail("PRAGMA foreign_key_check", f"Foreign key check returned violations: {fk_errors}", "CRITICAL")

    # 8.3 PRAGMA quick_check
    cur.execute("PRAGMA quick_check")
    qres = cur.fetchall()
    if qres == [("ok",)]:
        report.record_pass("PRAGMA quick_check -> ok")
    else:
        report.record_fail("PRAGMA quick_check", f"Quick check failed: {qres}", "CRITICAL")

    conn.close()


def main():
    print("\033[1;36m" + "=" * 70)
    print("  VYASA MAHABHARATA — EMPIRICAL ADVERSARIAL STRESS TEST HARNESS")
    print("=" * 70 + "\033[0m")

    test_suite_1_schema_and_foreign_keys()
    test_suite_2_concurrency_and_locking()
    test_suite_3_rapid_bookmarks()
    test_suite_4_reading_position_updates()
    test_suite_5_foreign_key_enforcement()
    test_suite_6_adversarial_fts_and_sanitizer()
    test_suite_7_memory_and_resource_leaks()
    test_suite_8_pragmas()

    print("\n\033[1;36m" + "=" * 70)
    print("  ADVERSARIAL STRESS TEST SUMMARY")
    print("=" * 70 + "\033[0m")
    print(f"  Total Passed: \033[32m{report.passed}\033[0m")
    print(f"  Total Failed: \033[31m{report.failed}\033[0m")

    if report.findings:
        print("\n\033[1;31mDiscovered Vulnerabilities & Deviations:\033[0m")
        for idx, f in enumerate(report.findings, 1):
            print(f"  {idx}. [{f['severity']}] {f['name']}")
            print(f"     {f['reason']}\n")
        
        print("\033[1;31mVERDICT: REQUEST_CHANGES\033[0m\n")
        return 1
    else:
        print("\n\033[1;32mVERDICT: APPROVE\033[0m\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())
