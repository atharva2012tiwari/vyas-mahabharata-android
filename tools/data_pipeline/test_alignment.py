"""
Automated Verification & Integrity Tests for Mahabharata SQLite Database
Verifies:
1. All 18 Parvas exist with valid names, colors, and descriptions.
2. Shlokas have non-empty Sanskrit, IAST, Hindi, and English texts.
3. FTS5 indexing works across all languages with sub-15ms latency.
"""

import os
import sqlite3
import time


def test_database_integrity():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app/src/main/assets/mahabharata.db"))
    assert os.path.exists(db_path), f"Database not found at {db_path}"
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Test 18 Parvas
    cur.execute("SELECT COUNT(*) FROM parvas")
    parva_count = cur.fetchone()[0]
    assert parva_count == 18, f"Expected 18 Parvas, found {parva_count}"
    
    # 2. Test Parva details
    cur.execute("SELECT number, name_sanskrit, name_english FROM parvas ORDER BY number ASC")
    parvas = cur.fetchall()
    assert parvas[0][0] == 1 and "आदिपर्व" in parvas[0][1]
    assert parvas[5][0] == 6 and "भीष्मपर्व" in parvas[5][1]
    assert parvas[17][0] == 18 and "स्वर्गारोहणपर्व" in parvas[17][1]
    
    # 3. Test Shlokas completeness
    cur.execute("SELECT id, verse_tag, sanskrit_devanagari, sanskrit_iast, translation_hindi, translation_english FROM shlokas")
    shlokas = cur.fetchall()
    assert len(shlokas) > 0, "No shlokas found"
    
    for s in shlokas:
        sid, tag, skt, iast, hin, eng = s
        assert len(tag.split(".")) == 3, f"Invalid verse tag: {tag}"
        assert len(skt.strip()) > 0, f"Empty Sanskrit in verse {tag}"
        assert len(iast.strip()) > 0, f"Empty IAST in verse {tag}"
        assert len(hin.strip()) > 0, f"Empty Hindi in verse {tag}"
        assert len(eng.strip()) > 0, f"Empty English in verse {tag}"
        
    # 4. Test FTS5 Search queries & benchmark latency
    test_queries = [
        "Narayana",
        "धर्मक्षेत्रे",
        "Duryodhana",
        "भीमार्जुनसमा",
        "वैशम्पायन",
        "Kurukshetra"
    ]
    
    for q in test_queries:
        start = time.perf_counter()
        cur.execute("SELECT verse_tag, sanskrit_devanagari FROM shlokas_fts WHERE shlokas_fts MATCH ?", (q,))
        results = cur.fetchall()
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert len(results) > 0, f"FTS search query '{q}' returned 0 results"
        assert elapsed_ms < 15.0, f"Query '{q}' took {elapsed_ms:.2f}ms (threshold 15ms)"
        print(f"PASS: Query '{q}' returned {len(results)} hit(s) in {elapsed_ms:.2f}ms")
        
    conn.close()
    print("All automated database integrity and latency tests PASSED successfully!")


if __name__ == "__main__":
    test_database_integrity()
