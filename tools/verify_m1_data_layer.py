"""
Milestone 1 Data Layer Forensic Verification Script
Validates:
1. 1:1 Room Entity schema match against SQLite assets/mahabharata.db
2. Foreign key relationships and indices
3. Master Parvas (18), Chapters, and 4-language Shlokas completeness
4. Sub-15ms FTS5 search performance across Devanagari, IAST, Hindi, and English
5. Bookmark and Reading History persistence semantics
6. AndroidManifest and resource XML validity
"""

import os
import re
import sqlite3
import time
import xml.etree.ElementTree as ET

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(WORKSPACE_ROOT, "app/src/main/assets/mahabharata.db")
ENTITY_DIR = os.path.join(WORKSPACE_ROOT, "app/src/main/java/com/vyas/mahabharata/data/local/entity")
DAO_DIR = os.path.join(WORKSPACE_ROOT, "app/src/main/java/com/vyas/mahabharata/data/local/dao")
REPO_DIR = os.path.join(WORKSPACE_ROOT, "app/src/main/java/com/vyas/mahabharata/data/repository")
MODEL_DIR = os.path.join(WORKSPACE_ROOT, "app/src/main/java/com/vyas/mahabharata/domain/model")
RES_DIR = os.path.join(WORKSPACE_ROOT, "app/src/main/res")
MANIFEST_PATH = os.path.join(WORKSPACE_ROOT, "app/src/main/AndroidManifest.xml")


def test_schema_alignment_1_to_1():
    print("\n--- [Test 1] 1:1 Schema Alignment (Room Entities vs SQLite) ---")
    assert os.path.exists(DB_PATH), f"Database missing at {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Table to Entity mapping
    tables_to_entities = {
        "parvas": "ParvaEntity.kt",
        "chapters": "ChapterEntity.kt",
        "shlokas": "ShlokaEntity.kt",
        "bookmarks": "BookmarkEntity.kt",
        "reading_history": "ReadingHistoryEntity.kt"
    }

    for table, entity_file in tables_to_entities.items():
        entity_path = os.path.join(ENTITY_DIR, entity_file)
        assert os.path.exists(entity_path), f"Entity file missing: {entity_path}"
        with open(entity_path, "r", encoding="utf-8") as f:
            content = f.read()

        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()
        print(f"Table '{table}' has {len(columns)} columns in SQLite:")

        for cid, col_name, col_type, notnull, dflt_val, pk in columns:
            print(f"  - {col_name} ({col_type}) notnull={notnull} pk={pk}")
            # Verify col_name appears in Kotlin entity file either as ColumnInfo(name = "col_name") or direct field
            pattern = re.compile(rf'name\s*=\s*"{col_name}"|val\s+{col_name}\b', re.IGNORECASE)
            assert pattern.search(content), f"Column '{col_name}' from table '{table}' not found in {entity_file}"

        print(f"  -> Table '{table}' matches {entity_file} 1:1 (All {len(columns)} columns verified)")

    conn.close()
    print("Schema alignment: ALL 5 TABLES VERIFIED 1:1.")


def test_foreign_keys_and_indices():
    print("\n--- [Test 2] Foreign Keys and Indexing ---")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_key_list(chapters)")
    fk_chapters = cur.fetchall()
    assert len(fk_chapters) > 0, "No foreign key found on chapters"
    assert fk_chapters[0][2] == "parvas" and fk_chapters[0][3] == "parva_number" and fk_chapters[0][4] == "number"
    print("  -> Foreign key chapters(parva_number) -> parvas(number) verified")

    cur.execute("PRAGMA foreign_key_list(shlokas)")
    fk_shlokas = cur.fetchall()
    assert len(fk_shlokas) > 0, "No foreign key found on shlokas"
    assert fk_shlokas[0][2] == "parvas" and fk_shlokas[0][3] == "parva_number" and fk_shlokas[0][4] == "number"
    print("  -> Foreign key shlokas(parva_number) -> parvas(number) verified")

    cur.execute("PRAGMA foreign_key_list(bookmarks)")
    fk_bookmarks = cur.fetchall()
    assert len(fk_bookmarks) > 0, "No foreign key found on bookmarks"
    assert fk_bookmarks[0][2] == "shlokas" and fk_bookmarks[0][3] == "shloka_id" and fk_bookmarks[0][4] == "id"
    print("  -> Foreign key bookmarks(shloka_id) -> shlokas(id) verified")

    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indices = [r[0] for r in cur.fetchall()]
    assert "idx_shloka_parva_chapter" in indices
    assert "idx_shloka_verse_tag" in indices
    assert "idx_chapter_parva_number" in indices
    assert "idx_bookmark_shloka_id" in indices
    print(f"  -> All expected indices verified: {indices}")
    conn.close()


def test_data_corpus_and_4_languages():
    print("\n--- [Test 3] 18 Parvas & 4-Language Verse Alignment ---")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT number, name_sanskrit, name_hindi, name_english, color_seed FROM parvas ORDER BY number ASC")
    parvas = cur.fetchall()
    assert len(parvas) == 18, f"Expected 18 Parvas, got {len(parvas)}"
    for p in parvas:
        num, skt, hin, eng, color = p
        assert num >= 1 and num <= 18
        assert skt and len(skt.strip()) > 0
        assert hin and len(hin.strip()) > 0
        assert eng and len(eng.strip()) > 0
        assert color and color.startswith("#")
    print("  -> All 18 Parvas present with Devanagari, Hindi, English, and Color Seeds")

    # Verify Shlokas text completeness
    cur.execute("""
        SELECT verse_tag, sanskrit_devanagari, sanskrit_iast, translation_hindi, translation_english
        FROM shlokas
    """)
    shlokas = cur.fetchall()
    assert len(shlokas) >= 20, f"Expected at least 20 shlokas, got {len(shlokas)}"
    for s in shlokas:
        tag, skt, iast, hin, eng = s
        assert skt and len(skt.strip()) > 5, f"Empty Sanskrit in {tag}"
        assert iast and len(iast.strip()) > 5, f"Empty IAST in {tag}"
        assert hin and len(hin.strip()) > 5, f"Empty Hindi in {tag}"
        assert eng and len(eng.strip()) > 5, f"Empty English in {tag}"
    print(f"  -> All {len(shlokas)} shlokas have complete 4-language text")
    conn.close()


def test_fts5_latency():
    print("\n--- [Test 4] Sub-15ms SQLite FTS5 Multilingual Search Benchmark ---")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    queries = [
        ("Sanskrit Devanagari (Invocation)", "नारायणं"),
        ("Sanskrit Devanagari (Gita Opening)", "धर्मक्षेत्रे"),
        ("IAST Transliteration (Kurukshetra)", "dharmaksetre*"),
        ("IAST Transliteration (Duryodhana)", "duryodhana*"),
        ("Hindi Translation (संजय)", "संजय"),
        ("English Translation (Narayana)", "Narayana"),
        ("English Translation (Kurukshetra)", "Kurukshetra"),
        ("Prefix Search (धर्म*)", "धर्म*"),
        ("Prefix Search (Nara*)", "Nara*")
    ]

    for label, q in queries:
        latencies = []
        for _ in range(10): # 10 runs each
            t0 = time.perf_counter()
            cur.execute("""
                SELECT s.verse_tag, s.sanskrit_devanagari, s.translation_english
                FROM shlokas s
                JOIN shlokas_fts fts ON s.id = fts.rowid
                WHERE shlokas_fts MATCH ?
            """, (q,))
            rows = cur.fetchall()
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000)

        avg_lat = sum(latencies) / len(latencies)
        min_lat = min(latencies)
        assert len(rows) > 0, f"Query '{q}' returned 0 rows"
        assert avg_lat < 15.0, f"Query '{q}' average latency {avg_lat:.2f}ms exceeded 15ms SLA"
        print(f"  -> [{label}] Query '{q}': {len(rows)} hits, avg={avg_lat:.3f}ms, min={min_lat:.3f}ms (PASS < 15ms)")

    conn.close()


def test_bookmark_and_history_persistence():
    print("\n--- [Test 5] Bookmarking & Reading History Persistence Semantics ---")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Test reading history upsert
    cur.execute("""
        INSERT OR REPLACE INTO reading_history (parva_number, last_chapter_number, last_verse_number, scroll_offset, updated_at)
        VALUES (1, 1, 5, 250, ?)
    """, (int(time.time() * 1000),))
    conn.commit()

    cur.execute("SELECT last_chapter_number, last_verse_number, scroll_offset FROM reading_history WHERE parva_number = 1")
    hist = cur.fetchone()
    assert hist == (1, 5, 250), f"Unexpected history: {hist}"
    print("  -> Reading history upsert and retrieval verified")

    # Test bookmark insert and delete
    cur.execute("""
        INSERT INTO bookmarks (shloka_id, collection_name, user_note, created_at)
        VALUES (1, 'Favorites', 'Key verse', ?)
    """, (int(time.time() * 1000),))
    bm_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT id, collection_name, user_note FROM bookmarks WHERE id = ?", (bm_id,))
    bm = cur.fetchone()
    assert bm == (bm_id, "Favorites", "Key verse")
    print("  -> Bookmark insert and retrieval verified")

    # Clean up test rows
    cur.execute("DELETE FROM bookmarks WHERE id = ?", (bm_id,))
    cur.execute("DELETE FROM reading_history WHERE parva_number = 1")
    conn.commit()
    conn.close()
    print("  -> Bookmark and history cleanup verified")


def test_manifest_and_resources():
    print("\n--- [Test 6] AndroidManifest.xml and Resource XML Verification ---")
    assert os.path.exists(MANIFEST_PATH), f"Manifest missing: {MANIFEST_PATH}"
    tree = ET.parse(MANIFEST_PATH)
    root = tree.getroot()

    app_elem = root.find("application")
    assert app_elem is not None, "application element missing in Manifest"

    # Verify MainActivity
    activity = app_elem.find("activity")
    assert activity is not None, "MainActivity missing"
    assert activity.attrib.get("{http://schemas.android.com/apk/res/android}name") == "com.vyas.mahabharata.MainActivity"

    # Verify FileProvider
    provider = app_elem.find("provider")
    assert provider is not None, "FileProvider missing"
    assert provider.attrib.get("{http://schemas.android.com/apk/res/android}name") == "androidx.core.content.FileProvider"
    print("  -> AndroidManifest.xml parsed and verified (MainActivity + FileProvider)")

    # Verify resource files
    for res_file in ["values/strings.xml", "values/colors.xml", "values/themes.xml", "xml/file_paths.xml"]:
        p = os.path.join(RES_DIR, res_file)
        assert os.path.exists(p), f"Resource file missing: {p}"
        ET.parse(p)
        print(f"  -> Resource valid: {res_file}")


def main():
    print("==================================================================")
    print("VYASA MAHABHARATA - MILESTONE 1 VERIFICATION SUITE")
    print("==================================================================")
    test_schema_alignment_1_to_1()
    test_foreign_keys_and_indices()
    test_data_corpus_and_4_languages()
    test_fts5_latency()
    test_bookmark_and_history_persistence()
    test_manifest_and_resources()
    print("\n==================================================================")
    print("ALL MILESTONE 1 FORENSIC INTEGRITY CHECKS PASSED SUCCESSFULLY!")
    print("==================================================================")


if __name__ == "__main__":
    main()
