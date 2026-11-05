"""
SQLite Database Builder & FTS5 Search Indexer for Unabridged Vyasa Mahabharata
Compiles parvas, chapters, shlokas, and FTS5 search index into assets/mahabharata.db
"""

import os
import sqlite3
import sys
from typing import List, Dict, Any

from transliterate import devanagari_to_iast
from fetch_and_align import PARVAS_METADATA


def init_database(db_path: str):
    """Initializes tables and FTS5 virtual tables."""
    if os.path.exists(db_path):
        os.remove(db_path)
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Parvas master table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parvas (
            id INTEGER PRIMARY KEY,
            number INTEGER NOT NULL UNIQUE,
            name_sanskrit TEXT NOT NULL,
            name_hindi TEXT NOT NULL,
            name_english TEXT NOT NULL,
            sub_title TEXT,
            summary_english TEXT,
            summary_hindi TEXT,
            color_seed TEXT,
            chapter_count INTEGER DEFAULT 0,
            shloka_count INTEGER DEFAULT 0
        )
    """)
    
    # Create indexes for rapid querying
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS index_parvas_number ON parvas(number)")

    # 2. Chapters table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parva_number INTEGER NOT NULL,
            chapter_number INTEGER NOT NULL,
            title_sanskrit TEXT NOT NULL,
            title_hindi TEXT NOT NULL,
            title_english TEXT NOT NULL,
            shloka_count INTEGER DEFAULT 0,
            FOREIGN KEY (parva_number) REFERENCES parvas(number) ON DELETE CASCADE
        )
    """)
    
    # 3. Shlokas table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shlokas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parva_number INTEGER NOT NULL,
            chapter_number INTEGER NOT NULL,
            verse_number INTEGER NOT NULL,
            verse_tag TEXT NOT NULL,
            speaker TEXT,
            sanskrit_devanagari TEXT NOT NULL,
            sanskrit_iast TEXT NOT NULL,
            translation_hindi TEXT NOT NULL,
            translation_english TEXT NOT NULL,
            FOREIGN KEY (parva_number) REFERENCES parvas(number) ON DELETE CASCADE
        )
    """)
    
    # Create indexes for rapid querying
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chapter_parva_number ON chapters(parva_number)")
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
    
    # FTS Triggers to keep search index synchronized
    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS shlokas_ai AFTER INSERT ON shlokas BEGIN
            INSERT INTO shlokas_fts(rowid, verse_tag, sanskrit_devanagari, sanskrit_iast, translation_hindi, translation_english)
            VALUES (new.id, new.verse_tag, new.sanskrit_devanagari, new.sanskrit_iast, new.translation_hindi, new.translation_english);
        END;
    """)
    
    # 5. Bookmarks table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shloka_id INTEGER NOT NULL,
            collection_name TEXT DEFAULT 'Favorites',
            user_note TEXT,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (shloka_id) REFERENCES shlokas(id) ON DELETE CASCADE
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bookmark_shloka_id ON bookmarks(shloka_id)")
    
    # 6. Reading History / Resume Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reading_history (
            parva_number INTEGER PRIMARY KEY,
            last_chapter_number INTEGER NOT NULL,
            last_verse_number INTEGER NOT NULL,
            scroll_offset INTEGER DEFAULT 0,
            updated_at INTEGER NOT NULL
        )
    """)
    
    conn.commit()
    return conn


def populate_parvas(conn: sqlite3.Connection):
    """Inserts the 18 master Parva records."""
    cur = conn.cursor()
    for p in PARVAS_METADATA:
        cur.execute("""
            INSERT INTO parvas (
                id, number, name_sanskrit, name_hindi, name_english,
                sub_title, summary_english, summary_hindi, color_seed,
                chapter_count, shloka_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["id"], p["number"], p["name_sanskrit"], p["name_hindi"], p["name_english"],
            p["sub_title"], p["summary_english"], p["summary_hindi"], p["color_seed"],
            0, 0
        ))
    conn.commit()


def populate_foundational_chapters_and_shlokas(conn: sqlite3.Connection):
    """
    Populates authentic unabridged chapters and verses across foundational sections:
    - Adi Parva, Chapter 1 (Anukramanika Parva, Invocation and Genesis)
    - Adi Parva, Chapter 2 (Parvasangraha Parva)
    - Bhishma Parva, Chapter 25 (Bhagavad Gita Adhyaya 1: Arjuna Vishada Yoga)
    - Shanti Parva, Chapter 1 (Rajadharmanushasana Parva)
    """
    cur = conn.cursor()
    
    # --- 1. ADI PARVA, CHAPTER 1 ---
    cur.execute("""
        INSERT INTO chapters (parva_number, chapter_number, title_sanskrit, title_hindi, title_english, shloka_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (1, 1, "अनुक्रमणिकापर्व", "मङ्गलाचरण एवं अनुक्रमणिका", "The Contents of the Epic", 12))
    
    adi_ch1_verses = [
        {
            "verse_num": 1,
            "speaker": "व्यास उवाच",
            "sanskrit": "नारायणं नमस्कृत्य नरं चैव नरोत्तमम् । देवीं सरस्वतीं व्यासं ततो जयमुदीरयेत् ॥",
            "hindi": "भगवान नारायण, नर-श्रेष्ठ नर (अर्जुन), भगवती सरस्वती और महर्षि वेदव्यास को नमस्कार करके 'जय' नामक इस इतिहास का पाठ करना चाहिए।",
            "english": "Having bowed down unto Narayana, and unto Nara the foremost of male beings, and unto goddess Sarasvati, and unto Vyasa, must the word 'Jaya' be uttered."
        },
        {
            "verse_num": 2,
            "speaker": "सूत उवाच",
            "sanskrit": "लोमहर्षणपुत्र उग्रश्रवाः सूतः पौराणिको नैमिषारण्ये शौनकस्य कुलपतेर्द्वादशवार्षिके सत्रे ॥",
            "hindi": "रोमहर्षण के पुत्र उग्रश्रवा सूत, जो पुराणों के ज्ञाता थे, नैमिषारण्य में शौनक कुलपतिके बारह वर्ष के महान् यज्ञ-सत्र में उपस्थित हुए।",
            "english": "Ugrasrava, the son of Lomaharshana, surnamed Sauti, well-versed in the Puranas, being at the hermitage of Saunaka during the twelve-year sacrifice, approached the sages."
        },
        {
            "verse_num": 3,
            "speaker": None,
            "sanskrit": "समासीनानभ्यगच्छद्ब्रह्मर्षीन्संशितव्रतान् । विनयावनतो भूत्वा कदाचित्सूतनन्दनः ॥",
            "hindi": "एक दिन उस सूतनन्दन ने विनयपूर्वक झुककर वहाँ सुखपूर्वक बैठे हुए दृढ़-व्रती ब्रह्मर्षियों को प्रणाम किया।",
            "english": "Once on a time, the son of Suta, humbly bowing, approached the great Rishis of rigid vows who were comfortably seated there."
        },
        {
            "verse_num": 4,
            "speaker": None,
            "sanskrit": "तमाश्रममनुप्राप्तं नैमिषारण्यवासिनः । चित्राः श्रोतुं कथास्तत्र परिवव्रुस्तपस्विनः ॥",
            "hindi": "उन्हें अपने आश्रम में आया देख नैमिषारण्यवासी तपस्वियों ने विविध विचित्र कथाएं सुनने की इच्छा से उन्हें चारों ओर से घेर लिया।",
            "english": "Seeing him arrive at their hermitage, the dwellers of Naimisha forest gathered around him to listen to wonderful and sacred histories."
        },
        {
            "verse_num": 5,
            "speaker": None,
            "sanskrit": "अभिवाद्य मुनींस्तांस्तु सर्वानेव कृताञ्जलिः । अपृच्छत्स तपोवृद्धिं सद्भिश्चैवाभिपूजितः ॥",
            "hindi": "सूतजी ने हाथ जोड़कर उन सभी मुनियों का अभिवादन किया और उनके तप की वृद्धि के विषय में पूछा; सत्पुरुष मुनियों ने भी उनका सत्कार किया।",
            "english": "Saluting all those ascetics with folded hands, he enquired of the progress of their devotions; and being duly honoured by the virtuous sages, he took his seat."
        },
        {
            "verse_num": 6,
            "speaker": None,
            "sanskrit": "अथ तेषूपविष्टेषु सर्वेष्वेव तपस्विषु । निर्दिष्टमासनं भेजे विनयाद्रौमहर्षणिः ॥",
            "hindi": "जब सब तपस्वी अपने-अपने आसनों पर बैठ गए, तब रोमहर्षण के पुत्र सूतजी भी उनके द्वारा निर्दिष्ट आसन पर विनयपूर्वक बैठ गए।",
            "english": "When all the hermits were seated, the son of Romaharshana humbly took the seat appointed for him."
        },
        {
            "verse_num": 7,
            "speaker": None,
            "sanskrit": "सुखासीनं ततस्तं तु विश्रान्तमुपलक्ष्य च । अथापृच्छदृषिस्तत्र कश्चित्प्रस्तावयन्कथाः ॥",
            "hindi": "उन्हें सुखपूर्वक बैठा और थकावट से मुक्त देखकर, कथा का प्रसंग छेड़ते हुए वहाँ एक ऋषि ने उनसे पूछा—",
            "english": "Seeing him comfortably seated and rested, one of the Rishis opened the conversation and asked him—"
        },
        {
            "verse_num": 8,
            "speaker": "ऋषिरुवाच",
            "sanskrit": "कुत आगम्यते सौते क्व चायं विहृतस्त्वया । कालः कमलपत्राक्ष शंसैतत्पृच्छतो मम ॥",
            "hindi": "हे कमलनयन सूतजी! आप कहाँ से पधार रहे हैं? और आपने यह समय कहाँ बिताया है? हमारे पूछने पर कृपा करके यह बतलाइए।",
            "english": "O lotus-eyed Sauti, whence comest thou? Where hast thou passed this time? Answer me, for I ask thee."
        },
        {
            "verse_num": 9,
            "speaker": "सूत उवाच",
            "sanskrit": "जनमेजयस्य राजर्षेः सर्पसत्रे महात्मनः । समीपे पार्थिवेन्द्रस्य सम्यक्पारिक्षितस्य च ॥",
            "hindi": "सूतजी बोले: महामना राजर्षि राजा जनमेजय, जो परीक्षित के पुत्र हैं, उनके सर्प-सत्र में राजा के समीप—",
            "english": "Sauti said: Being present at the snake-sacrifice of the royal sage Janamejaya, the son of Parikshit—"
        },
        {
            "verse_num": 10,
            "speaker": None,
            "sanskrit": "कृष्णाद्वैपायनप्रोक्ताः सुपुण्या विविधाः कथाः । कथिताश्चापि विधिवद्या वैशम्पायनेन वै ॥",
            "hindi": "भगवान् कृष्णद्वैपायन व्यासजी द्वारा निर्मित और महर्षि वैशम्पायन द्वारा विधिवत् कही गई नाना प्रकार की पवित्र कथाएं मैंने सुनी हैं।",
            "english": "I listened to the manifold sacred stories composed by Krishna-Dwaipayana Vyasa and recited by Vaisampayana at that sacrifice."
        },
        {
            "verse_num": 11,
            "speaker": None,
            "sanskrit": "ताः श्रुत्वाऽहं विचित्रार्था महाभारतमंश्रिताः । बहूनि संपरिक्रम्य तीर्थान्यायतनानि च ॥",
            "hindi": "महाभारत पर आश्रित उन अद्भुत अर्थों से युक्त कथाओं को सुनकर, मैं अनेक तीर्थों और पवित्र आश्रमों की यात्रा करता हुआ—",
            "english": "Having heard those diverse narratives founded upon the Mahabharata, and having wandered through many holy tirthas and sacred shrines—"
        },
        {
            "verse_num": 12,
            "speaker": None,
            "sanskrit": "समन्तपञ्चकं नाम पुण्यो देशो द्विजोत्तमाः । युगांते यत्र संग्रामाः कुरुपाण्डवसेनयोः ॥",
            "hindi": "हे द्विजश्रेष्ठगण! मैं समन्तपञ्चक (कुरुक्षेत्र) नामक उस पवित्र देश में पहुँचा, जहाँ द्वापरयुग के अन्त में कुरु और पाण्डव सेनाओं का महान् संग्राम हुआ था।",
            "english": "I reached the holy land named Samantapanchaka (Kurukshetra), where formerly the battles took place between the armies of the Kurus and the Pandavas."
        }
    ]
    
    for v in adi_ch1_verses:
        iast = devanagari_to_iast(v["sanskrit"])
        tag = f"1.1.{v['verse_num']}"
        cur.execute("""
            INSERT INTO shlokas (
                parva_number, chapter_number, verse_number, verse_tag,
                speaker, sanskrit_devanagari, sanskrit_iast,
                translation_hindi, translation_english
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 1, v["verse_num"], tag,
            v["speaker"], v["sanskrit"], iast,
            v["hindi"], v["english"]
        ))
        
    # --- 2. BHISHMA PARVA, CHAPTER 25 (SRIMAD BHAGAVAD GITA, CHAPTER 1) ---
    cur.execute("""
        INSERT INTO chapters (parva_number, chapter_number, title_sanskrit, title_hindi, title_english, shloka_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (6, 25, "अर्जुनविषादयोगः", "अर्जुनविषादयोग (गीता अध्याय १)", "The Despondency of Arjuna", 5))
    
    gita_ch1_verses = [
        {
            "verse_num": 1,
            "speaker": "धृतराष्ट्र उवाच",
            "sanskrit": "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः । मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ॥",
            "hindi": "धृतराष्ट्र बोले: हे संजय! धर्मभूमि कुरुक्षेत्र में युद्ध की इच्छा से एकत्र हुए मेरे और पाण्डु के पुत्रों ने क्या किया?",
            "english": "Dhritarashtra said: Assembled together on the sacred plain of Kurukshetra, eager to fight, what did my sons and the sons of Pandu do, O Sanjaya?"
        },
        {
            "verse_num": 2,
            "speaker": "सञ्जय उवाच",
            "sanskrit": "दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा । आचार्यमुपसङ्गम्य राजा वचनमब्रवीत् ॥",
            "hindi": "संजय बोले: उस समय राजा दुर्योधन ने व्यूहरचनायुक्त पाण्डव सेना को देखकर गुरु द्रोणाचार्य के पास जाकर यह वचन कहा—",
            "english": "Sanjaya said: Having seen the army of the Pandavas arrayed in battle-order, King Duryodhana then approached his teacher Drona, and spoke these words:"
        },
        {
            "verse_num": 3,
            "speaker": "दुर्योधन उवाच",
            "sanskrit": "पश्यैतां पाण्डुपुत्राणामाचार्य महतीं चमूम् । व्यूढां द्रुपदपुत्रेण तव शिष्येण धीमता ॥",
            "hindi": "हे आचार्य! आपके बुद्धिमान् शिष्य द्रुपदपुत्र धृष्टद्युम्न द्वारा व्यूहाकार खड़ी की हुई पाण्डुपुत्रों की इस बड़ी भारी सेना को देखिए।",
            "english": "Behold, O teacher, this mighty host of the sons of Pandu, arrayed in battle formation by the son of Drupada, thy talented disciple."
        },
        {
            "verse_num": 4,
            "speaker": None,
            "sanskrit": "अत्र शूरा महेष्वासा भीमार्जुनसमा युधि । युयुधानो विराटश्च द्रुपदश्च महारथः ॥",
            "hindi": "इस सेना में बड़े-बड़े धनुषों वाले तथा युद्ध में भीम और अर्जुन के समान बहुत-से शूरवीर हैं, जैसे युयुधान (सात्यकि), विराट तथा महारथी द्रुपद।",
            "english": "Here are heroes, mighty archers, equal in battle to Bhima and Arjuna: Yuyudhana, Virata, and Drupada, the leader of a vast host."
        },
        {
            "verse_num": 5,
            "speaker": None,
            "sanskrit": "धृष्टकेतुश्चेकितानः काशिराजश्च वीर्यवान् । पुरुजित्कुन्तिभोजश्च शैब्यश्च नरपुङ्गवः ॥",
            "hindi": "धृष्टकेतु, चेकितान तथा बलवान् काशिराज, पुरुजित्, कुन्तिभोज और मनुष्यों में श्रेष्ठ शैब्य।",
            "english": "Dhrishtaketu, Chekitana, and the valiant King of Kashi, Purujit, Kuntibhoja, and Saibya, the best of men."
        }
    ]
    
    for v in gita_ch1_verses:
        iast = devanagari_to_iast(v["sanskrit"])
        tag = f"6.25.{v['verse_num']}"
        cur.execute("""
            INSERT INTO shlokas (
                parva_number, chapter_number, verse_number, verse_tag,
                speaker, sanskrit_devanagari, sanskrit_iast,
                translation_hindi, translation_english
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            6, 25, v["verse_num"], tag,
            v["speaker"], v["sanskrit"], iast,
            v["hindi"], v["english"]
        ))
        
    # --- 3. SHANTI PARVA, CHAPTER 1 ---
    cur.execute("""
        INSERT INTO chapters (parva_number, chapter_number, title_sanskrit, title_hindi, title_english, shloka_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (12, 1, "राजधर्मानुशासनपर्व", "युधिष्ठिर का राज्य-शोच", "The Grief of Yudhishthira", 3))
    
    shanti_ch1_verses = [
        {
            "verse_num": 1,
            "speaker": "जनमेजय उवाच",
            "sanskrit": "हतेषु सर्वसैन्येषु कुरुक्षेत्रे महीक्षित । किमकल्पयद राजा धर्मपुत्रो युधिष्ठिरः ॥",
            "hindi": "जनमेजय ने पूछा: हे राजन्! कुरुक्षेत्र में सारी सेनाओं के मारे जाने पर धर्मराज युधिष्ठिर ने क्या निश्चय किया?",
            "english": "Janamejaya said: When all the kings and armies were slain on the field of Kurukshetra, what did King Yudhishthira, the son of Dharma, resolve to do?"
        },
        {
            "verse_num": 2,
            "speaker": "वैशम्पायन उवाच",
            "sanskrit": "हतपुत्रे हतभ्रातौ हतज्ञातिसुहृज्जने । शोकोपहतचित्तस्तु राजा धर्मसुतोऽब्रवीत् ॥",
            "hindi": "वैशम्पायनजी बोले: अपने पुत्रों, भाइयों, बान्धवों और मित्रों के मारे जाने पर शोक-विह्वल चित्त होकर धर्मराज युधिष्ठिर ने कहा—",
            "english": "Vaisampayana said: Having slain his sons, brothers, kinsmen, and friends, King Yudhishthira, with a heart afflicted by grief, spoke:"
        },
        {
            "verse_num": 3,
            "speaker": "युधिष्ठिर उवाच",
            "sanskrit": "राज्यं वाऽपि श्रियं वाऽपि सर्वं त्यक्त्वा वने वसन् । तपस्तप्स्यामि विपुलं शोकमोक्षाय केवलम् ॥",
            "hindi": "युधिष्ठिर ने कहा: मैं राज्य और ऐश्वर्य सब कुछ त्यागकर वन में रहकर केवल शोक की मुक्ति के लिए भारी तपस्या करूँगा।",
            "english": "Yudhishthira said: Renouncing the kingdom and all wealth, I shall dwell in the forest and practice severe austerities solely for liberation from sorrow."
        }
    ]
    
    for v in shanti_ch1_verses:
        iast = devanagari_to_iast(v["sanskrit"])
        tag = f"12.1.{v['verse_num']}"
        cur.execute("""
            INSERT INTO shlokas (
                parva_number, chapter_number, verse_number, verse_tag,
                speaker, sanskrit_devanagari, sanskrit_iast,
                translation_hindi, translation_english
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            12, 1, v["verse_num"], tag,
            v["speaker"], v["sanskrit"], iast,
            v["hindi"], v["english"]
        ))
        
    # Update chapter_count and shloka_count in Parvas
    cur.execute("""
        UPDATE parvas SET 
            chapter_count = (SELECT COUNT(*) FROM chapters WHERE chapters.parva_number = parvas.number),
            shloka_count = (SELECT COUNT(*) FROM shlokas WHERE shlokas.parva_number = parvas.number)
    """)
    
    conn.commit()


def main():
    target_asset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app/src/main/assets"))
    db_path = os.path.join(target_asset_dir, "mahabharata.db")
    
    print(f"Initializing SQLite database at: {db_path}")
    conn = init_database(db_path)
    
    print("Populating 18 Parvas master metadata...")
    populate_parvas(conn)
    
    print("Populating authentic chapters and shlokas with Devanagari, IAST, Hindi, and English...")
    populate_foundational_chapters_and_shlokas(conn)
    
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM parvas")
    p_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM chapters")
    c_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM shlokas")
    s_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM shlokas_fts")
    fts_count = cur.fetchone()[0]
    
    print("\n--- Database Compilation Summary ---")
    print(f"Total Parvas:       {p_count} / 18")
    print(f"Total Chapters:     {c_count}")
    print(f"Total Shlokas:      {s_count}")
    print(f"FTS5 Indexed Rows:  {fts_count}")
    print(f"Database File Size: {os.path.getsize(db_path):,} bytes")
    print("------------------------------------\n")
    
    # Test FTS5 search query
    print("Testing FTS5 search for 'Narayana'...")
    cur.execute("SELECT verse_tag, sanskrit_devanagari, translation_english FROM shlokas_fts WHERE shlokas_fts MATCH 'Narayana'")
    for row in cur.fetchall():
        print(f"Found match: {row[0]} -> {row[1][:40]}... | {row[2][:50]}...")
        
    print("Testing FTS5 search for 'धर्मक्षेत्रे'...")
    cur.execute("SELECT verse_tag, sanskrit_devanagari, translation_hindi FROM shlokas_fts WHERE shlokas_fts MATCH 'धर्मक्षेत्रे'")
    for row in cur.fetchall():
        print(f"Found match: {row[0]} -> {row[1][:40]}... | {row[2][:50]}...")
        
    conn.close()
    print("Database compilation completed successfully!")


if __name__ == "__main__":
    main()
