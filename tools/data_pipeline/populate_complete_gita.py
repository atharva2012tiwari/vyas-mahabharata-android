"""
Complete Srimad Bhagavad Gita Database Builder
Builds all 18 Chapters and all 701 canonical verses into assets/mahabharata.db
with Devanagari Sanskrit, Roman IAST, Hindi meaning, English translation,
vivid speaker attribution, and SQLite FTS5 search indexing.
"""

import os
import re
import json
import sqlite3
import sys

GITA_REPO_DIR = "/tmp/gita_repo"
TARGET_ASSET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app/src/main/assets"))
DB_PATH = os.path.join(TARGET_ASSET_DIR, "mahabharata.db")

COLOR_SEEDS = [
    "#D95D00", # Ch 1: Saffron
    "#026670", # Ch 2: Peacock Blue
    "#9C4100", # Ch 3: Ochre
    "#0F766E", # Ch 4: Deep Teal
    "#C05621", # Ch 5: Terracotta
    "#2C5282", # Ch 6: Royal Navy
    "#B7791F", # Ch 7: Amber Gold
    "#1A365D", # Ch 8: Midnight Blue
    "#D69E2E", # Ch 9: Sacred Gold
    "#744210", # Ch 10: Bronze
    "#007791", # Ch 11: Celestial Blue
    "#DD6B20", # Ch 12: Warm Flame
    "#2D3748", # Ch 13: Slate
    "#319795", # Ch 14: Turquoise
    "#805AD5", # Ch 15: Sacred Amethyst
    "#C53030", # Ch 16: Ruby Crimson
    "#38A169", # Ch 17: Forest Jade
    "#D95D00", # Ch 18: Ultimate Saffron
]

def clean_shloka(raw_slok: str):
    """Separates speaker and normalizes Sanskrit shloka text."""
    lines = [l.strip() for l in raw_slok.split('\n') if l.strip()]
    speaker = None
    if lines:
        l0 = lines[0].replace('|', '').strip()
        if l0.endswith('वाच') or 'उवाच' in l0 or 'नुवाच' in l0:
            speaker = l0
            lines = lines[1:]

    cleaned_lines = []
    for l in lines:
        # Normalize dandas
        l = l.replace('||', '॥').replace('|', '।')
        # Remove trailing chapter-verse numbering like ॥२-४७॥ or ॥1-1॥
        l = re.sub(r'॥[०-९0-9\-\s]+॥', '॥', l)
        l = re.sub(r'॥\s*॥', '॥', l)
        cleaned_lines.append(l.strip())

    return speaker, '\n'.join(cleaned_lines)

def clean_iast(raw_iast: str):
    """Cleans Roman IAST transliteration."""
    lines = [l.strip() for l in raw_iast.split('\n') if l.strip()]
    cleaned = []
    for l in lines:
        l = re.sub(r'\|+[0-9\-\s]+\|+', '||', l)
        l = re.sub(r'\|+', '||', l)
        cleaned.append(l.strip())
    return '\n'.join(cleaned)

FALLBACK_HINDI = {
    '12.3': 'जो मनुष्य इन्द्रिय-समुदाय को भली प्रकार वश में करके सर्वत्र समबुद्धि रखते हुए उस अनिर्देश्य, अव्यक्त, सर्वव्यापी, अचिन्त्य, कूटस्थ, अचल और नित्य अविनाशी स्वरूप की उपासना करते हैं—',
    '12.18': 'जो मनुष्य शत्रु और मित्र में तथा मान और अपमान में सम है, शीत-उष्ण और सुख-दुःख आदि द्वन्द्वों में सम है तथा आसक्ति से सर्वथा रहित है—'
}

def clean_hindi(data: dict, verse_key: str = ""):
    """Extracts best available Hindi translation."""
    if verse_key in FALLBACK_HINDI:
        return FALLBACK_HINDI[verse_key]
    h = ""
    for key in ['tej', 'san', 'rams', 'chinmay', 'adi']:
        val = data.get(key, {}).get('ht', '')
        if val and val.strip() and "did not comment" not in val.lower():
            h = val.strip()
            break
    # Clean leading ।।1.1।। or ।।2.47।।
    h = re.sub(r'^[।\s\.\d\-]+', '', h)
    return h.strip()

def clean_english(data: dict):
    """Extracts best available English translation."""
    e = ""
    for key in ['purohit', 'siva', 'prabhu', 'san', 'chinmay']:
        val = data.get(key, {}).get('et', '')
        if val and val.strip() and "did not comment" not in val.lower():
            e = val.strip()
            break
    # Clean leading 1.1 or 2.47
    e = re.sub(r'^\d+[\.\-]\d+\s*', '', e)
    return e.strip()

def init_database(db_path: str):
    """Initializes tables and FTS5 virtual table with exact Room schema."""
    if os.path.exists(db_path):
        os.remove(db_path)

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Parvas master table (representing the 18 Chapters)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parvas (
            id INTEGER NOT NULL,
            number INTEGER NOT NULL,
            name_sanskrit TEXT NOT NULL,
            name_hindi TEXT NOT NULL,
            name_english TEXT NOT NULL,
            sub_title TEXT,
            summary_english TEXT,
            summary_hindi TEXT,
            color_seed TEXT,
            chapter_count INTEGER NOT NULL DEFAULT 0,
            shloka_count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(id)
        )
    """)
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_parvas_number ON parvas(number)")

    # 2. Chapters table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            parva_number INTEGER NOT NULL,
            chapter_number INTEGER NOT NULL,
            title_sanskrit TEXT NOT NULL,
            title_hindi TEXT NOT NULL,
            title_english TEXT NOT NULL,
            shloka_count INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (parva_number) REFERENCES parvas(number) ON UPDATE NO ACTION ON DELETE CASCADE
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chapter_parva_number ON chapters(parva_number)")

    # 3. Shlokas table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shlokas (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            parva_number INTEGER NOT NULL,
            chapter_number INTEGER NOT NULL,
            verse_number INTEGER NOT NULL,
            verse_tag TEXT NOT NULL,
            speaker TEXT,
            sanskrit_devanagari TEXT NOT NULL,
            sanskrit_iast TEXT NOT NULL,
            translation_hindi TEXT NOT NULL,
            translation_english TEXT NOT NULL,
            FOREIGN KEY (parva_number) REFERENCES parvas(number) ON UPDATE NO ACTION ON DELETE CASCADE
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shloka_parva_chapter ON shlokas(parva_number, chapter_number)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_shloka_verse_tag ON shlokas(verse_tag)")

    # 4. FTS5 Virtual Table for Instant Multilingual Search
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS shlokas_fts USING fts5 (
            verse_tag UNINDEXED,
            sanskrit_devanagari,
            sanskrit_iast,
            translation_hindi,
            translation_english,
            content='shlokas',
            content_rowid='id'
        )
    """)
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS shlokas_ai AFTER INSERT ON shlokas BEGIN
            INSERT INTO shlokas_fts(rowid, verse_tag, sanskrit_devanagari, sanskrit_iast, translation_hindi, translation_english)
            VALUES (new.id, new.verse_tag, new.sanskrit_devanagari, new.sanskrit_iast, new.translation_hindi, new.translation_english);
        END;
    """)

    # 5. Bookmarks table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            shloka_id INTEGER NOT NULL,
            collection_name TEXT NOT NULL DEFAULT 'Favorites',
            user_note TEXT,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (shloka_id) REFERENCES shlokas(id) ON UPDATE NO ACTION ON DELETE CASCADE
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bookmark_shloka_id ON bookmarks(shloka_id)")

    # 6. Reading History Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reading_history (
            parva_number INTEGER NOT NULL,
            last_chapter_number INTEGER NOT NULL,
            last_verse_number INTEGER NOT NULL,
            scroll_offset INTEGER NOT NULL DEFAULT 0,
            updated_at INTEGER NOT NULL,
            PRIMARY KEY(parva_number)
        )
    """)

    # 7. Room Master Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS room_master_table (
            id INTEGER PRIMARY KEY,
            identity_hash TEXT
        )
    """)
    cur.execute("INSERT OR REPLACE INTO room_master_table (id, identity_hash) VALUES (42, 'df3c175abb9c1c67a74cb040896b52f7')")

    conn.commit()
    return conn

def main():
    print(f"Initializing complete Srimad Bhagavad Gita SQLite DB at: {DB_PATH}")
    conn = init_database(DB_PATH)
    cur = conn.cursor()

    total_shlokas = 0

    for ch in range(1, 19):
        ch_path = f"{GITA_REPO_DIR}/chapter/bhagavadgita_chapter_{ch}.json"
        with open(ch_path, "r", encoding="utf-8") as f:
            ch_data = json.load(f)

        sanskrit_title = ch_data.get("name", "")
        if sanskrit_title.endswith("योग"):
            sanskrit_title += "ः"
        hindi_title = ch_data.get("meaning", {}).get("hi", ch_data.get("name", ""))
        english_title = ch_data.get("meaning", {}).get("en", ch_data.get("translation", ""))
        verses_count = ch_data.get("verses_count", 0)
        summary_hi = ch_data.get("summary", {}).get("hi", "")
        summary_en = ch_data.get("summary", {}).get("en", "")
        color_seed = COLOR_SEEDS[ch - 1]

        # 1. Insert Parva
        cur.execute("""
            INSERT INTO parvas (
                id, number, name_sanskrit, name_hindi, name_english,
                sub_title, summary_english, summary_hindi, color_seed,
                chapter_count, shloka_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ch, ch, sanskrit_title, hindi_title, english_title,
            f"अध्याय {ch} • {verses_count} श्लोक", summary_en, summary_hi, color_seed,
            1, verses_count
        ))

        # 2. Insert Chapter
        cur.execute("""
            INSERT INTO chapters (
                parva_number, chapter_number, title_sanskrit, title_hindi, title_english, shloka_count
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ch, ch, sanskrit_title, hindi_title, english_title, verses_count
        ))

        # 3. Insert all verses for this chapter
        ch_shloka_count = 0
        for v in range(1, verses_count + 1):
            v_path = f"{GITA_REPO_DIR}/slok/bhagavadgita_chapter_{ch}_slok_{v}.json"
            if not os.path.exists(v_path):
                print(f"Warning: File not found {v_path}")
                continue

            with open(v_path, "r", encoding="utf-8") as vf:
                v_data = json.load(vf)

            raw_slok = v_data.get("slok", "")
            raw_iast = v_data.get("transliteration", "")

            speaker, clean_sanskrit = clean_shloka(raw_slok)
            clean_iast_text = clean_iast(raw_iast)
            hindi_trans = clean_hindi(v_data, f"{ch}.{v}")
            english_trans = clean_english(v_data)

            verse_tag = f"{ch}.{ch}.{v}"

            cur.execute("""
                INSERT INTO shlokas (
                    parva_number, chapter_number, verse_number, verse_tag,
                    speaker, sanskrit_devanagari, sanskrit_iast,
                    translation_hindi, translation_english
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ch, ch, v, verse_tag,
                speaker, clean_sanskrit, clean_iast_text,
                hindi_trans, english_trans
            ))
            ch_shloka_count += 1
            total_shlokas += 1

        print(f"  Chapter {ch:2d}: {sanskrit_title:25s} | {ch_shloka_count} verses inserted")

    conn.commit()

    # Verify counts
    cur.execute("SELECT COUNT(*) FROM parvas")
    p_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM chapters")
    c_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM shlokas")
    s_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM shlokas_fts")
    fts_cnt = cur.fetchone()[0]

    db_size = os.path.getsize(DB_PATH)

    print("\n================ DATABASE SUMMARY ================")
    print(f"Parvas (Adhyayas): {p_cnt} / 18")
    print(f"Chapters:          {c_cnt} / 18")
    print(f"Total Shlokas:     {s_cnt} / 701")
    print(f"FTS5 Indexed Rows: {fts_cnt} / 701")
    print(f"Database File Size: {db_size:,} bytes")
    print("==================================================")

    # Test FTS5 queries
    queries = [
        "धर्मक्षेत्रे",
        "कर्मण्येवाधिकारस्ते",
        "यदा यदा हि धर्मस्य",
        "अहं वैश्वानरो भूत्वा",
        "सर्वधर्मान्परित्यज्य",
        "योगेश्वरः कृष्णो",
        "Karmanye",
        "duty"
    ]

    print("\nRunning FTS5 verification queries...")
    for q in queries:
        cur.execute("SELECT verse_tag, sanskrit_devanagari, translation_english FROM shlokas_fts WHERE shlokas_fts MATCH ? LIMIT 1", (q,))
        row = cur.fetchone()
        if row:
            print(f"  [PASS] '{q}' -> Verse {row[0]}: {row[1][:30]}...")
        else:
            print(f"  [WARN] '{q}' yielded no direct FTS hit")

    conn.close()
    print("\nComplete Bhagavad Gita database successfully compiled!")

if __name__ == "__main__":
    main()
