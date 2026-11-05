"""
Data Ingestion & Alignment Engine for Unabridged Vyasa Mahabharata
Fetches, normalizes, and aligns Sanskrit, Hindi, and English corpora across all 18 Parvas.
"""

import json
import os
import re
import sys
import urllib.request
from typing import Dict, List, Any, Optional

from transliterate import devanagari_to_iast

# 18 Parvas Canonical Metadata
PARVAS_METADATA = [
    {
        "id": 1,
        "number": 1,
        "name_sanskrit": "आदिपर्व",
        "name_hindi": "आदि पर्व",
        "name_english": "Adi Parva",
        "sub_title": "The Book of the Beginning",
        "summary_english": "Introduces the origins of the Kuru dynasty, the birth and youth of the Pandavas and Kauravas, the wax house conspiracy, and Draupadi's swayamvara.",
        "summary_hindi": "कुरु वंश की उत्पत्ति, पाण्डवों और कौरवों का जन्म, लाक्षागृह षड्यन्त्र, द्रौपदी का स्वयंवर तथा इन्द्रप्रस्थ की स्थापना का वर्णन।",
        "color_seed": "#8F4C1B"
    },
    {
        "id": 2,
        "number": 2,
        "name_sanskrit": "सभापर्व",
        "name_hindi": "सभा पर्व",
        "name_english": "Sabha Parva",
        "sub_title": "The Book of the Assembly Hall",
        "summary_english": "The Maya Sabha palace, Yudhishthira's Rajasuya sacrifice, the fateful dice game, and the exile of the Pandavas.",
        "summary_hindi": "इन्द्रप्रस्थ में मय सभा का निर्माण, राजसूय यज्ञ, द्यूत-क्रीड़ा, द्रौपदी का चीरहरण और पाण्डवों का वनवास।",
        "color_seed": "#70583A"
    },
    {
        "id": 3,
        "number": 3,
        "name_sanskrit": "वनपर्व (अरण्यकपर्व)",
        "name_hindi": "वन पर्व",
        "name_english": "Vana Parva",
        "sub_title": "The Book of the Forest",
        "summary_english": "The 12-year exile in the Kamyaka and Dwaita forests, philosophical discourses, pilgrimages, and the stories of Nala-Damayanti and Savitri-Satyavan.",
        "summary_hindi": "पाण्डवों का १२ वर्ष का वनवास, तीर्थयात्राएं, नलोपाख्यान, सावित्री-सत्यवान आख्यान और यक्ष-युधिष्ठिर संवाद।",
        "color_seed": "#2E5339"
    },
    {
        "id": 4,
        "number": 4,
        "name_sanskrit": "विराटपर्व",
        "name_hindi": "विराट पर्व",
        "name_english": "Virata Parva",
        "sub_title": "The Book of Virata",
        "summary_english": "The 13th year of incognito exile in King Virata's court (Matsya Kingdom), the slaying of Kichaka, and the cattle raid battle.",
        "summary_hindi": "राजा विराट के मत्स्य देश में पाण्डवों का अज्ञातवास, कीचक-वध और उत्तर गो-ग्रहण का युद्ध।",
        "color_seed": "#4A6267"
    },
    {
        "id": 5,
        "number": 5,
        "name_sanskrit": "उद्योगपर्व",
        "name_hindi": "उद्योग पर्व",
        "name_english": "Udyoga Parva",
        "sub_title": "The Book of Effort / Peace Missions",
        "summary_english": "Preparations for the great war, peace diplomacy, Sri Krishna's peace embassy to Hastinapura, and Vidura Niti.",
        "summary_hindi": "महाभारत युद्ध की पूर्व तैयारियां, विदुर नीति, भगवान श्रीकृष्ण का शान्ति-दूत बनकर हस्तिनापुर जाना और युद्ध का निश्चय।",
        "color_seed": "#855325"
    },
    {
        "id": 6,
        "number": 6,
        "name_sanskrit": "भीष्मपर्व",
        "name_hindi": "भीष्म पर्व",
        "name_english": "Bhishma Parva",
        "sub_title": "The Book of Bhishma (Contains Srimad Bhagavad Gita)",
        "summary_english": "First 10 days of the Kurukshetra war under Bhishma's command, including the immortal teaching of the Srimad Bhagavad Gita, ending with Bhishma on the bed of arrows.",
        "summary_hindi": "कुरुक्षेत्र युद्ध के प्रथम १० दिन, भीष्म का सेनापतित्व, श्रीमद्भगवद्गीता का अमर उपदेश तथा भीष्म का शरशय्या पर शयन।",
        "color_seed": "#9A4020"
    },
    {
        "id": 7,
        "number": 7,
        "name_sanskrit": "द्रोणपर्व",
        "name_hindi": "द्रोण पर्व",
        "name_english": "Drona Parva",
        "sub_title": "The Book of Drona",
        "summary_english": "Days 11 to 15 of the war under Dronacharya, the Chakravyuha formation, the tragic martyrdom of Abhimanyu, Arjuna's vow, and Jayadratha's slaying.",
        "summary_hindi": "युद्ध के ११वें से १५वें दिन तक द्रोणाचार्य का सेनापतित्व, चक्रव्यूह रचना, वीर अभिमन्यु का बलिदान और जयद्रथ वध।",
        "color_seed": "#6B4938"
    },
    {
        "id": 8,
        "number": 8,
        "name_sanskrit": "कर्णपर्व",
        "name_hindi": "कर्ण पर्व",
        "name_english": "Karna Parva",
        "sub_title": "The Book of Karna",
        "summary_english": "Days 16 and 17 of the war under Karna, Shalya as Karna's charioteer, the climactic duel between Arjuna and Karna, and Karna's fall.",
        "summary_hindi": "कर्ण का सेनापतित्व, शल्य का सारथ्य, अर्जुन और कर्ण का महासंग्राम तथा कर्ण का वीरगति प्राप्त होना।",
        "color_seed": "#8E3B24"
    },
    {
        "id": 9,
        "number": 9,
        "name_sanskrit": "शल्यपर्व",
        "name_hindi": "शल्य पर्व",
        "name_english": "Shalya Parva",
        "sub_title": "The Book of Shalya",
        "summary_english": "The 18th and final day of war, Shalya's demise, Duryodhana hiding in Dwaipayana lake, and the mace duel between Bhima and Duryodhana.",
        "summary_hindi": "युद्ध का अन्तिम १८वाँ दिन, शल्य का वध, दुर्योधन का द्वैपायन सरोवर में छिपना तथा भीम-दुर्योधन गदा युद्ध।",
        "color_seed": "#5C4A3A"
    },
    {
        "id": 10,
        "number": 10,
        "name_sanskrit": "सौप्तिकपर्व",
        "name_hindi": "सौप्तिक पर्व",
        "name_english": "Sauptika Parva",
        "sub_title": "The Book of the Sleeping Warriors",
        "summary_english": "Ashwatthama, Kripa, and Kritavarma execute a midnight raid on the sleeping Pandava camp, slaying the Upapandavas and Dhrishtadyumna.",
        "summary_hindi": "अश्वत्थामा, कृपाचार्य और कृतवर्मा द्वारा रात्रि में सोए हुए पाण्डव शिविर पर आक्रमण और उप-पाण्डवों का संहार।",
        "color_seed": "#3E3836"
    },
    {
        "id": 11,
        "number": 11,
        "name_sanskrit": "स्त्रीपर्व",
        "name_hindi": "स्त्री पर्व",
        "name_english": "Stri Parva",
        "sub_title": "The Book of the Women",
        "summary_english": "Gandhari, Kunti, and the women lament the fallen warriors on the Kurukshetra battlefield; Gandhari's curse to Krishna.",
        "summary_hindi": "कुरुक्षेत्र के रणक्षेत्र में गान्धारी, कुन्ती तथा अन्य स्त्रियों का विलाप, गान्धारी द्वारा श्रीकृष्ण को शाप और श्राद्ध कर्म।",
        "color_seed": "#58424E"
    },
    {
        "id": 12,
        "number": 12,
        "name_sanskrit": "शान्तिपर्व",
        "name_hindi": "शान्ति पर्व",
        "name_english": "Shanti Parva",
        "sub_title": "The Book of Peace",
        "summary_english": "The coronation of Yudhishthira, and Bhishma's encyclopedic discourse on statecraft (Rajadharma), governance, and spiritual liberation (Mokshadharma).",
        "summary_hindi": "युधिष्ठिर का राज्याभिषेक तथा शरशय्या पर लेटे भीष्म पितामह द्वारा राजधर्म, आपद्धर्म और मोक्षधर्म का गूढ़ उपदेश।",
        "color_seed": "#385458"
    },
    {
        "id": 13,
        "number": 13,
        "name_sanskrit": "अनुशासनपर्व",
        "name_hindi": "अनुशासन पर्व",
        "name_english": "Anushasana Parva",
        "sub_title": "The Book of Instructions",
        "summary_english": "Bhishma's final instructions on charity, dharma, duty, the Vishnu Sahasranama (Thousand Names of Lord Vishnu), and Bhishma's departure (Iccha Mrityu).",
        "summary_hindi": "भीष्म द्वारा धर्म, दान, सदाचार का उपदेश, श्रीविष्णुसहस्रनाम स्तोत्र तथा सूर्य के उत्तरायण होने पर भीष्म का प्राण-त्याग।",
        "color_seed": "#4A4358"
    },
    {
        "id": 14,
        "number": 14,
        "name_sanskrit": "आश्वमेधिकपर्व",
        "name_hindi": "आश्वमेधिक पर्व",
        "name_english": "Ashvamedhika Parva",
        "sub_title": "The Book of the Horse Sacrifice",
        "summary_english": "Yudhishthira's royal Ashvamedha sacrifice, Arjuna's campaign across Bharata, and the Anugita teachings by Sri Krishna.",
        "summary_hindi": "युधिष्ठिर द्वारा अश्वमेध यज्ञ का अनुष्ठान, अर्जुन द्वारा दिग्विजय अभियान और श्रीकृष्ण-अर्जुन संवाद रूपी 'अनुगीता'।",
        "color_seed": "#6B5035"
    },
    {
        "id": 15,
        "number": 15,
        "name_sanskrit": "आश्रमवासिकपर्व",
        "name_hindi": "आश्रमवासिक पर्व",
        "name_english": "Ashramavasika Parva",
        "sub_title": "The Book of the Hermitage",
        "summary_english": "Dhritarashtra, Gandhari, and Kunti retire to the forest hermitage; their ascetic life and eventual passing in a forest conflagration.",
        "summary_hindi": "धृतराष्ट्र, गान्धारी, कुन्ती और विदुर का वानप्रस्थ आश्रम में जाना, तपस्या और दावानल में देहत्याग।",
        "color_seed": "#4D463D"
    },
    {
        "id": 16,
        "number": 16,
        "name_sanskrit": "मौसलपर्व",
        "name_hindi": "मौसल पर्व",
        "name_english": "Mausala Parva",
        "sub_title": "The Book of the Maces",
        "summary_english": "The destruction of the Vrishni/Yadava clan by the iron mace curse, the submergence of Dwaraka in the ocean, and Krishna's ascent to his eternal abode.",
        "summary_hindi": "ऋषि-शाप के फलस्वरूप मूसल से यदुवंश का विनाश, द्वारका का समुद्र में निमज्जन और भगवान श्रीकृष्ण का परमधाम गमन।",
        "color_seed": "#523B3B"
    },
    {
        "id": 17,
        "number": 17,
        "name_sanskrit": "महाप्रस्थानिकपर्व",
        "name_hindi": "महाप्रस्थानिक पर्व",
        "name_english": "Mahaprasthanika Parva",
        "sub_title": "The Book of the Great Journey",
        "summary_english": "The Pandavas and Draupadi renounce their kingdom and embark on their final pilgrimage towards the Himalayas and Mount Meru.",
        "summary_hindi": "पाण्डवों और द्रौपदी का राज्य-त्याग, हिमालय की ओर महाप्रस्थान तथा एक-एक करके सबका शरीर पतन।",
        "color_seed": "#3D4850"
    },
    {
        "id": 18,
        "number": 18,
        "name_sanskrit": "स्वर्गारोहणपर्व",
        "name_hindi": "स्वर्गारोहण पर्व",
        "name_english": "Svargarohana Parva",
        "sub_title": "The Book of the Ascent to Heaven",
        "summary_english": "Yudhishthira ascends to heaven with the faithful dog (Dharma), passes the final test of illusion in the nether regions, and reunites with his brothers, Draupadi, and Krishna in eternal peace.",
        "summary_hindi": "युधिष्ठिर का सशरीर स्वर्ग-गमन, धर्मराज की परीक्षा, मायावी नरक-दर्शन और अन्ततः सभी भाइयों तथा द्रौपदी का दिव्य धाम में मिलन।",
        "color_seed": "#785820"
    }
]


def create_parva_records() -> List[Dict[str, Any]]:
    """Returns the master Parva records for all 18 Parvas."""
    return PARVAS_METADATA


def extract_speakers(shloka: str) -> Optional[str]:
    """Detects speaker attribution prefixes like 'धृतराष्ट्र उवाच', 'संजय उवाच'."""
    pattern = r"((?:श्री)?(?:[^\n।॥]+)\s*उवाच(?:\s*:)?[॥।]?)"
    match = re.search(pattern, shloka)
    if match:
        return match.group(1).strip()
    return None


def clean_sanskrit_verse(text: str) -> str:
    """Cleans verse text, normalizes whitespace and standard dandas."""
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("||", "॥").replace("|", "।")
    return text


if __name__ == "__main__":
    parvas = create_parva_records()
    print(f"Loaded metadata for all {len(parvas)} Parvas.")
    for p in parvas[:3]:
        print(f" - Parva {p['number']}: {p['name_sanskrit']} ({p['name_english']})")
