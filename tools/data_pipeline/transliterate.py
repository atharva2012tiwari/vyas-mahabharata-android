"""
Devanagari to IAST (International Alphabet of Sanskrit Transliteration) Converter
Pure Python, zero-dependency, highly accurate converter for Sanskrit and Vedic texts.
"""

# Vowels (Independent)
VOWELS = {
    'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū',
    'ऋ': 'ṛ', 'ॠ': 'ṝ', 'ऌ': 'ḷ', 'ॡ': 'ḹ',
    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au'
}

# Vowel Signs (Matras)
MATRAS = {
    'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū',
    'ृ': 'ṛ', 'ॄ': 'ṝ', 'ॢ': 'ḷ', 'ॣ': 'ḹ',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au'
}

# Consonants (inherent 'a' is stripped or kept depending on following virama/matra)
CONSONANTS = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ṅ',
    'च': 'c', 'छ': 'ch', 'ज': 'j', 'झ': 'jh', 'ञ': 'ñ',
    'ट': 'ṭ', 'ठ': 'ṭh', 'ड': 'ḍ', 'ढ': 'ḍh', 'ण': 'ṇ',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
    'श': 'ś', 'ष': 'ṣ', 'स': 's', 'ह': 'h',
    'ळ': 'ḻ', 'क्ष': 'kṣ', 'ज्ञ': 'jñ'
}

# Modifiers
MODIFIERS = {
    'ं': 'ṃ',
    'ः': 'ḥ',
    'ँ': 'm̐',
    'ऽ': "'",
    '।': ' |',
    '॥': ' ||'
}

VIRAMA = '्'


def devanagari_to_iast(text: str) -> str:
    """Converts a Devanagari Sanskrit string into standard IAST."""
    if not text:
        return ""
    
    result = []
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        # Check 2-character conjunct specials like क्ष or ज्ञ if present directly
        if i + 1 < n and text[i:i+2] in CONSONANTS:
            cons = CONSONANTS[text[i:i+2]]
            i += 2
            # Check next character
            if i < n and text[i] == VIRAMA:
                result.append(cons)
                i += 1
            elif i < n and text[i] in MATRAS:
                result.append(cons + MATRAS[text[i]])
                i += 1
            else:
                result.append(cons + 'a')
            continue
            
        if char in CONSONANTS:
            cons = CONSONANTS[char]
            i += 1
            if i < n and text[i] == VIRAMA:
                result.append(cons)
                i += 1
            elif i < n and text[i] in MATRAS:
                result.append(cons + MATRAS[text[i]])
                i += 1
            else:
                result.append(cons + 'a')
        elif char in VOWELS:
            result.append(VOWELS[char])
            i += 1
        elif char in MATRAS:
            # Standalone matra fallback
            result.append(MATRAS[char])
            i += 1
        elif char in MODIFIERS:
            result.append(MODIFIERS[char])
            i += 1
        else:
            result.append(char)
            i += 1
            
    return "".join(result)


if __name__ == "__main__":
    sample = "नारायणं नमस्कृत्य नरं चैव नरोत्तमम् । देवीं सरस्वतीं व्यासं ततो जयमुदीरयेत् ॥"
    print("Devanagari:", sample)
    print("IAST:      ", devanagari_to_iast(sample))
