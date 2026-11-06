"""
Full Srimad Bhagavad Gita Database Builder & Search Indexer
Builds all 18 Chapters with authentic Sanskrit titles, English names, shloka counts,
wisdom summaries, and iconic shlokas into assets/mahabharata.db with FTS5 search.
"""

import os
import sqlite3
import sys
from transliterate import devanagari_to_iast

GITA_CHAPTERS = [
    {
        "number": 1,
        "name_sanskrit": "अर्जुनविषादयोगः",
        "name_hindi": "अर्जुनविषादयोग",
        "name_english": "The Dilemma of Arjuna",
        "sub_title": "अध्याय १ • ४७ श्लोक",
        "summary_hindi": "कुरुक्षेत्र के रणक्षेत्र में दोनों सेनाओं को देखकर अर्जुन अपने ही सगे-सम्बन्धियों के प्रति मोह और शोक से व्याकुल होकर धनुष-बाण त्याग देते हैं। यहीं से गीता के उपदेश की पृष्ठभूमि तैयार होती है।",
        "summary_english": "On the battlefield of Kurukshetra, observing beloved elders, teachers, and kinsmen ready to fight, Arjuna is overwhelmed by grief and despondency, laying down his bow and arrows.",
        "shloka_count": 47,
        "color_seed": "#D95D00",
        "shlokas": [
            {
                "verse_num": 1,
                "speaker": "धृतराष्ट्र उवाच",
                "sanskrit": "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः ।\nमामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ॥",
                "hindi": "धृतराष्ट्र बोले: हे संजय! धर्मभूमि कुरुक्षेत्र में युद्ध की इच्छा से एकत्र हुए मेरे और पाण्डु के पुत्रों ने क्या किया?",
                "english": "Dhritarashtra said: Assembled together on the sacred plain of Kurukshetra, eager for battle, what did my sons and the sons of Pandu do, O Sanjaya?"
            },
            {
                "verse_num": 2,
                "speaker": "सञ्जय उवाच",
                "sanskrit": "दृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा ।\nआचार्यमुपसङ्गम्य राजा वचनमब्रवीत् ॥",
                "hindi": "संजय बोले: उस समय राजा दुर्योधन ने व्यूहरचनायुक्त पाण्डव सेना को देखकर गुरु द्रोणाचार्य के समीप जाकर यह वचन कहा।",
                "english": "Sanjaya said: Having seen the army of the Pandavas arrayed in battle-order, King Duryodhana approached his teacher Drona and spoke these words."
            },
            {
                "verse_num": 47,
                "speaker": "सञ्जय उवाच",
                "sanskrit": "एवमुक्त्वार्जुनः संख्ये रथोपस्थ उपाविशत् ।\nविसृज्य सशरं चापं शोकसंविग्नमानसः ॥",
                "hindi": "संजय बोले: रणभूमि में शोक से व्याकुल मन वाले अर्जुन ऐसा कहकर बाणसहित धनुष को त्यागकर रथ के पिछले भाग में बैठ गए।",
                "english": "Sanjaya said: Having spoken thus on the battlefield, Arjuna cast away his bow and arrows and sank down into the seat of his chariot, his heart weighed down with sorrow."
            }
        ]
    },
    {
        "number": 2,
        "name_sanskrit": "सांख्ययोगः",
        "name_hindi": "सांख्ययोग",
        "name_english": "The Yoga of Self-Knowledge",
        "sub_title": "अध्याय २ • ७२ श्लोक",
        "summary_hindi": "भगवान् श्रीकृष्ण आत्मा की अमरता और देह की नश्वरता का उपदेश देते हैं। निष्काम कर्मयोग का सिद्धान्त समझाते हैं और स्थितप्रज्ञ पुरुष के लक्षण बताते हैं।",
        "summary_english": "Lord Krishna reveals the eternal, indestructible nature of the Soul (Atman) and the perishable nature of the physical body. He introduces the path of selfless action (Nishkama Karma) and the virtues of the steady-minded sage (Sthitaprajna).",
        "shloka_count": 72,
        "color_seed": "#026670",
        "shlokas": [
            {
                "verse_num": 11,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "अशोच्यानन्वशोचस्त्वं प्रज्ञावादांश्च भाषसे ।\nगतासूनगतासूंश्च नानुशोचन्ति पण्डिताः ॥",
                "hindi": "श्रीभगवान् बोले: तू न शोक करने योग्य मनुष्यों के लिए शोक करता है और पण्डितों के से वचन बोलता है; ज्ञानी पुरुष मृत या जीवित किसी के लिए शोक नहीं करते।",
                "english": "The Blessed Lord said: Thou hast grieved for those who should not be grieved for, yet thou speakest words of wisdom. The wise grieve neither for the dead nor for the living."
            },
            {
                "verse_num": 20,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "न जायते म्रियते वा कदाचिन्नायं भूत्वा भविता वा न भूयः ।\nअजो नित्यः शाश्वतोऽयं पुराणो न हन्यते हन्यमाने शरीरे ॥",
                "hindi": "यह आत्मा कभी न जन्मता है और न मरता है; यह अजन्मा, नित्य, सनातन और पुरातन है। शरीर के मारे जाने पर भी यह नहीं मारा जाता।",
                "english": "The Soul is never born, nor doth it ever die; nor having once been, doth it ever cease to be. Unborn, eternal, changeless, and primeval, it is not slain when the body is slain."
            },
            {
                "verse_num": 47,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन ।\nमा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि ॥",
                "hindi": "तेरा कर्म करने में ही अधिकार है, फल में कभी नहीं। तू कर्मफल का हेतु मत बन, और तेरी अकर्मण्यता में आसक्ति न हो।",
                "english": "Thy right is to work alone, never to its fruits. Let not the fruit of action be thy motive, nor let thy attachment be to inaction."
            }
        ]
    },
    {
        "number": 3,
        "name_sanskrit": "कर्मयोगः",
        "name_hindi": "कर्मयोग",
        "name_english": "The Yoga of Action",
        "sub_title": "अध्याय ३ • ४३ श्लोक",
        "summary_hindi": "कर्म से कोई भी व्यक्ति बच नहीं सकता। स्वधर्म का पालन, यज्ञभाव से लोक-कल्याण के लिए कर्तव्य कर्म करना ही कर्मयोग है।",
        "summary_english": "No being can remain inactive even for a moment. Performing one's natural duty without selfish desire, as a sacred offering for universal welfare, is the true path of Karma Yoga.",
        "shloka_count": 43,
        "color_seed": "#D95D00",
        "shlokas": [
            {
                "verse_num": 19,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "तस्मादसक्तः सततं कार्यं कर्म समाचर ।\nअसक्तो ह्याचरन्कर्म परमाप्नोति पूरुषः ॥",
                "hindi": "इसलिए तू निरन्तर अनासक्त होकर कर्तव्य कर्म का भली-भाँति आचरण कर; क्योंकि अनासक्त होकर कर्म करता हुआ मनुष्य परम पद को प्राप्त होता है।",
                "english": "Therefore, constantly perform thy duty without attachment; for by performing actions without personal clinging, man attains the Supreme."
            },
            {
                "verse_num": 35,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात् ।\nस्वधर्मे निधनं श्रेयः परधर्मो भयावहः ॥",
                "hindi": "अच्छी तरह आचरण में लाए हुए दूसरे के धर्म की अपेक्षा गुणरहित भी अपना धर्म श्रेष्ठ है; स्वधर्म में मरना कल्याणकारक है और परधर्म भय को देने वाला है।",
                "english": "Better is one's own duty, though destitute of merit, than the duty of another well-discharged. Better is death in the discharge of one's own duty; the duty of another is fraught with danger."
            }
        ]
    },
    {
        "number": 4,
        "name_sanskrit": "ज्ञानकर्मसंन्यासयोगः",
        "name_hindi": "ज्ञानकर्मसंन्यासयोग",
        "name_english": "The Yoga of Wisdom & Action",
        "sub_title": "अध्याय ४ • ४२ श्लोक",
        "summary_hindi": "भगवान् के अवतार का रहस्य, ज्ञानरूपी अग्नि द्वारा कर्मबन्धन की भस्म और श्रद्धावान् मनुष्य द्वारा ज्ञान की प्राप्ति का वर्णन।",
        "summary_english": "The divine secret of Divine Incarnation (Avatarhood), how the fire of wisdom burns all karmic reactions to ashes, and the attainment of supreme peace through reverent knowledge.",
        "shloka_count": 42,
        "color_seed": "#026670",
        "shlokas": [
            {
                "verse_num": 7,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत ।\nअभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम् ॥",
                "hindi": "हे भारत! जब-जब धर्म की हानि और अधर्म की वृद्धि होती है, तब-तब मैं अपने रूप को प्रकट करता हूँ।",
                "english": "Whenever there is a decline of righteousness, O Bharata, and an uprising of unrighteousness, then I manifest Myself."
            },
            {
                "verse_num": 8,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "परित्राणाय साधूनां विनाशाय च दुष्कृताम् ।\nधर्मसंस्थापनार्थाय संभवामि युगे युगे ॥",
                "hindi": "साधु पुरुषों के उद्धार के लिए, पापकर्म करने वालों के विनाश के लिए और धर्म की भली-भाँति स्थापना के लिए मैं युग-युग में प्रकट होता हूँ।",
                "english": "For the protection of the good, for the destruction of the wicked, and for the firm establishment of righteousness, I am born in every age."
            },
            {
                "verse_num": 38,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "न हि ज्ञानेन सदृशं पवित्रमिह विद्यते ।\nतत्स्वयं योगसंसिद्धः कालेनात्मनि विन्दति ॥",
                "hindi": "इस संसार में ज्ञान के समान पवित्र करने वाला कुछ भी नहीं है; उस ज्ञान को योग द्वारा सिद्ध हुआ मनुष्य समय पाकर स्वयं अपनी आत्मा में पाता है।",
                "english": "Truly, there is nothing in this world as purifying as wisdom. He who has attained perfection in Yoga finds it in himself in due course of time."
            }
        ]
    },
    {
        "number": 5,
        "name_sanskrit": "कर्मसंन्यासयोगः",
        "name_hindi": "कर्मसंन्यासयोग",
        "name_english": "The Yoga of True Renunciation",
        "sub_title": "अध्याय ५ • २९ श्लोक",
        "summary_hindi": "कर्मसंन्यास और कर्मयोग दोनों का समन्वय। सच्चा संन्यासी वह है जो न किसी से द्वेष करता है और न आकांक्षा; वह कर्म करते हुए भी कमल के पत्ते पर जल की भाँति निर्लेप रहता है।",
        "summary_english": "Harmonizing renunciation with selfless action. The true renunciant neither hates nor desires; performing duties without attachment, untouched by sin, like a lotus leaf unmoistened by water.",
        "shloka_count": 29,
        "color_seed": "#D95D00",
        "shlokas": [
            {
                "verse_num": 10,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "ब्रह्मण्याधाय कर्माणि सङ्गं त्यक्त्वा करोति यः ।\nलिप्यते न स पापेन पद्मपत्रमिवाम्भसा ॥",
                "hindi": "जो पुरुष सब कर्मों को परमात्मा में अर्पण करके और आसक्ति को त्यागकर कर्म करता है, वह पाप से वैसे ही लिप्त नहीं होता जैसे कमल का पत्ता जल से।",
                "english": "He who acts offering all actions to the Supreme, having abandoned attachment, is untainted by sin, just as the lotus leaf remains untouched by water."
            }
        ]
    },
    {
        "number": 6,
        "name_sanskrit": "आत्मसंयमयोगः",
        "name_hindi": "आत्मसंयमयोग (ध्यानयोग)",
        "name_english": "The Yoga of Meditation",
        "sub_title": "अध्याय ६ • ४७ श्लोक",
        "summary_hindi": "मन के संयम और ध्यान का अभ्यास। वायु की तरह चञ्चल मन को अभ्यास और वैराग्य से वश में किया जा सकता है।",
        "summary_english": "The discipline of meditation and mastering the mind. Though as restless and difficult to curb as the wind, the mind can be stilled through regular practice (abhyasa) and non-attachment (vairagya).",
        "shloka_count": 47,
        "color_seed": "#026670",
        "shlokas": [
            {
                "verse_num": 5,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "उद्धरेदात्मनाऽत्मानं नात्मानमवसादयेत् ।\nआत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः ॥",
                "hindi": "मनुष्य अपने द्वारा अपना उद्धार करे, अपना पतन न होने दे; क्योंकि आत्मा ही अपना मित्र है और आत्मा ही अपना शत्रु है।",
                "english": "Let a man lift himself by his own Self, let him not depress himself; for the Self alone is the friend of oneself, and the Self alone is the enemy of oneself."
            },
            {
                "verse_num": 26,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "यतो यतो निश्चरति मनश्चञ्चलमस्थिरम् ।\nततस्ततो नियम्यैतदात्मन्येव वशं नयेत् ॥",
                "hindi": "यह चञ्चल और अस्थिर मन जिस-जिस विषय के निमित्त से भटकता है, उस-उस से रोककर इसे बार-बार आत्मा में ही स्थिर करे।",
                "english": "From whatever cause the restless and unsteady mind wanders away, from that let him restrain it and bring it back under the control of the Self alone."
            }
        ]
    },
    {
        "number": 7,
        "name_sanskrit": "ज्ञानविज्ञानयोगः",
        "name_hindi": "ज्ञानविज्ञानयोग",
        "name_english": "The Yoga of Wisdom & Realization",
        "sub_title": "अध्याय ७ • ३० श्लोक",
        "summary_hindi": "ईश्वर की परा और अपरा प्रकृति का विवेचन। समस्त सृष्टि भगवान् में वैसे ही पिरोई है जैसे सूत में मणियाँ। चार प्रकार के भक्त भगवान् की शरण लेते हैं।",
        "summary_english": "The higher and lower energies of the Divine. All creation is strung upon the Lord like clusters of pearls upon a thread. Four classes of virtuous souls turn to God.",
        "shloka_count": 30,
        "color_seed": "#D95D00",
        "shlokas": [
            {
                "verse_num": 7,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "मत्तः परतरं नान्यत्किञ्चिदस्ति धनञ्जय ।\nमयि सर्वमिदं प्रोतं सूत्रे मणिगणा इव ॥",
                "hindi": "हे धनञ्जय! मुझसे श्रेष्ठ दूसरा कोई भी परम कारण नहीं है; यह सम्पूर्ण जगत् मुझमें वैसे ही पिरोया हुआ है जैसे धागे में मणियाँ।",
                "english": "There is nothing whatsoever higher than Me, O Dhananjaya! All this universe is strung on Me, like clusters of pearls on a thread."
            }
        ]
    },
    {
        "number": 8,
        "name_sanskrit": "अक्षरब्रह्मयोगः",
        "name_hindi": "अक्षरब्रह्मयोग",
        "name_english": "The Yoga of Imperishable Brahman",
        "sub_title": "अध्याय ८ • २८ श्लोक",
        "summary_hindi": "अन्तकाल में भगवान् के स्मरण का महत्त्व और मुक्ति के मार्ग। जो अन्तकाल में परमात्मा का स्मरण करता हुआ देह त्यागता है, वह परम पद को पाता है।",
        "summary_english": "The spiritual significance of one's consciousness at the final hour of passing. Whoever departs the body remembering the Divine alone attains to the Supreme Abode.",
        "shloka_count": 28,
        "color_seed": "#026670",
        "shlokas": [
            {
                "verse_num": 5,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "अन्तकाले च मामेव स्मरन्मुक्त्वा कलेवरम् ।\nयः प्रयाति स मद्भावं याति नास्त्यत्र संशयः ॥",
                "hindi": "जो पुरुष अन्तकाल में भी मेरा ही स्मरण करता हुआ शरीर को त्यागकर जाता है, वह मेरे साक्षात् स्वरूप को प्राप्त होता है—इसमें कोई संशय नहीं है।",
                "english": "And whosoever, at the time of death, leaves his body remembering Me alone, he attains to My being; there is no doubt about this."
            }
        ]
    },
    {
        "number": 9,
        "name_sanskrit": "राजविद्याराजगुह्ययोगः",
        "name_hindi": "राजविद्याराजगुह्ययोग",
        "name_english": "The Sovereign Secret",
        "sub_title": "अध्याय ९ • ३४ श्लोक",
        "summary_hindi": "परम गोपनीय ज्ञान और अनन्य भक्ति की महिमा। भगवान् सभी प्राणियों के योगक्षेम को वहन करते हैं जो अनन्य भाव से उनका चिन्तन करते हैं।",
        "summary_english": "The supreme secret of devotion and spiritual sovereign wisdom. The Lord promises to carry the preservation and welfare of those who worship Him with single-minded devotion.",
        "shloka_count": 34,
        "color_seed": "#D95D00",
        "shlokas": [
            {
                "verse_num": 22,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "अनन्याश्चिन्तयन्तो मां ये जनाः पर्युपासते ।\nतेषां नित्याभियुक्तानां योगक्षेमं वहाम्यहम् ॥",
                "hindi": "जो अनन्य भक्तजन मेरा निरन्तर चिन्तन करते हुए निष्काम भाव से मेरी उपासना करते हैं, उन नित्य-युक्त पुरुषों का योगक्षेम मैं स्वयं वहन करता हूँ।",
                "english": "To those who worship Me alone, meditating upon Me with single-minded devotion, to those ever steadfast, I ensure their security and supply what they lack."
            },
            {
                "verse_num": 26,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "पत्रं पुष्पं फलं तोयं यो मे भक्त्या प्रयच्छति ।\nतदहं भक्त्युपहृतमश्नामि प्रयतात्मनः ॥",
                "hindi": "जो कोई भक्त मेरे लिए प्रेमपूर्वक पत्र, पुष्प, फल या जल अर्पण करता है, उस शुद्ध बुद्धि निष्काम भक्त का वह प्रेमपूर्वक लाया हुआ उपहार मैं स्वीकार करता हूँ।",
                "english": "Whosoever offers unto Me with devotion a leaf, a flower, a fruit, or even water, that offering of love by the pure-hearted I joyfully accept."
            }
        ]
    },
    {
        "number": 10,
        "name_sanskrit": "विभूतियोगः",
        "name_hindi": "विभूतियोग",
        "name_english": "The Divine Splendours",
        "sub_title": "अध्याय १० • ४२ श्लोक",
        "summary_hindi": "सृष्टि के समस्त ऐश्वर्य, तेज और सौन्दर्य में भगवान् की ही दिव्य विभूति विद्यमान है। सूर्य में प्रकाश, नदियों में गङ्गा, और सम्पूर्ण भूतों का मूल भगवान् ही हैं।",
        "summary_english": "The all-pervading divine manifestations across the cosmos. Whatever is glorious, beautiful, or mighty is but a spark of the Lord's boundless splendour.",
        "shloka_count": 42,
        "color_seed": "#026670",
        "shlokas": [
            {
                "verse_num": 20,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "अहमात्मा गुडाकेश सर्वभूताशयस्थितः ।\nअहमादिश्च मध्यं च भूतानामन्त एव च ॥",
                "hindi": "हे गुडाकेश! मैं समस्त प्राणियों के हृदय में स्थित आत्मा हूँ; तथा सम्पूर्ण प्राणियों का आदि, मध्य और अन्त भी मैं ही हूँ।",
                "english": "I am the Self, O Gudakesha, seated in the hearts of all living beings; I am the beginning, the middle, and also the end of all existence."
            },
            {
                "verse_num": 41,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "यद्यद्विभूतिमत्सत्त्वं श्रीमदूर्जितमेव वा ।\nतत्तदेवावगच्छ त्वं मम तेजोंऽशसंभवम् ॥",
                "hindi": "जो-जो भी ऐश्वर्ययुक्त, कान्तियुक्त और शक्तिसम्पन्न वस्तु है, उस-उस को तू मेरे ही तेज के अंश की अभिव्यक्ति जान।",
                "english": "Whatever entity is glorious, prosperous, or endowed with power, know thou that to be a manifestation of a fragment of My splendour."
            }
        ]
    },
    {
        "number": 11,
        "name_sanskrit": "विश्वरूपदर्शनयोगः",
        "name_hindi": "विश्वरूपदर्शनयोग",
        "name_english": "The Cosmic Vision",
        "sub_title": "अध्याय ११ • ५५ श्लोक",
        "summary_hindi": "अर्जुन की प्रार्थना पर भगवान् श्रीकृष्ण अपने असीम, दिव्य विश्वरूप का दर्शन कराते हैं, जिसमें सम्पूर्ण ब्रह्माण्ड, काल और दिशाएं समाहित हैं।",
        "summary_english": "Upon Arjuna's prayer, Lord Krishna reveals His awe-inspiring Cosmic Universal Form (Vishwarupa), containing all planets, celestial beings, time, and cosmic annihilation.",
        "shloka_count": 55,
        "color_seed": "#D95D00",
        "shlokas": [
            {
                "verse_num": 12,
                "speaker": "सञ्जय उवाच",
                "sanskrit": "दिवि सूर्यसहस्रस्य भवेद्युगपदुत्थिता ।\nयदि भाः सदृशी सा स्याद्भासस्तस्य महात्मनः ॥",
                "hindi": "आकाश में यदि एक साथ सहस्र सूर्यों का प्रकाश उदित हो जाए, तो वह प्रकाश भी उस परमात्मा के विश्वरूप के तेज के समान शायद ही हो सके।",
                "english": "If the radiance of a thousand suns were to burst forth at once in the sky, that would be like the splendour of that Mighty Being."
            },
            {
                "verse_num": 32,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "कालोऽस्मि लोकक्षयकृत्प्रवृद्धो लोकान्समाहर्तुमिह प्रवृत्तः ।\nऋतेऽपि त्वां न भविष्यन्ति सर्वे येऽवस्थिताः प्रत्यनीकेषु योधाः ॥",
                "hindi": "मैं लोकों का क्षय करने वाला बढ़ा हुआ काल हूँ; इस समय इन सेनाओं का संहार करने प्रवृत्त हुआ हूँ। तेरे युद्ध न करने पर भी ये प्रतिपक्षी योद्धा नहीं बचेंगे।",
                "english": "I am Time, the mighty destroyer of worlds, here engaged in swallowing up the realms. Even without thee, none of the warriors assembled in the opposing armies shall survive."
            }
        ]
    },
    {
        "number": 12,
        "name_sanskrit": "भक्तियोगः",
        "name_hindi": "भक्तियोग",
        "name_english": "The Yoga of Loving Devotion",
        "sub_title": "अध्याय १२ • २० श्लोक",
        "summary_hindi": "सगुण और निर्गुण उपासना की तुलना, अनन्य भक्ति की सुगमता, और भगवान् के प्रिय भक्त के दिव्य सद्गुणों का वर्णन।",
        "summary_english": "Comparing the paths of the formless Absolute and personal loving devotion. The path of love is sweetest and most natural for embodied beings; the endearing qualities of a true devotee.",
        "shloka_count": 20,
        "color_seed": "#026670",
        "shlokas": [
            {
                "verse_num": 2,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "मय्यावेश्य मनो ये मां नित्ययुक्ता उपासते ।\nश्रद्धया परयोपेतास्ते मे युक्ततमा मताः ॥",
                "hindi": "मुझमें मन को एकाग्र करके जो नित्य-युक्त भक्त परम श्रद्धा से मेरी उपासना करते हैं, वे मेरे मत में सर्वश्रेष्ठ योगी हैं।",
                "english": "Those who, fixing their mind on Me, worship Me with steadfast devotion and endowed with supreme faith, them do I consider the highest yogins."
            },
            {
                "verse_num": 15,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "यस्मान्नोद्विजते लोको लोकान्नोद्विजते च यः ।\nहर्षामर्षभयोद्वेगैर्मुक्तो यः स च मे प्रियः ॥",
                "hindi": "जिससे किसी प्राणी को उद्वेग नहीं होता और जो स्वयं किसी प्राणी से उद्विग्न नहीं होता; जो हर्ष, अमर्ष, भय और चिन्ता से मुक्त है, वह भक्त मुझे प्रिय है।",
                "english": "He by whom the world is not agitated and who cannot be agitated by the world, who is freed from joy, anger, fear, and anxiety—he is dear to Me."
            }
        ]
    },
    {
        "number": 13,
        "name_sanskrit": "क्षेत्रक्षेत्रज्ञविभागयोगः",
        "name_hindi": "क्षेत्रक्षेत्रज्ञविभागयोग",
        "name_english": "The Field & The Knower",
        "sub_title": "अध्याय १३ • ३५ श्लोक",
        "summary_hindi": "यह नश्वर शरीर 'क्षेत्र' (खेत) है और इसमें वास करने वाली चैतन्य आत्मा 'क्षेत्रज्ञ' (जानने वाला) है। प्रकृति और पुरुष का विवेक ही परम ज्ञान है।",
        "summary_english": "The body is the Field (Kshetra), and the witnessing Consciousness within is the Knower of the Field (Kshetragya). Discerning the distinction between matter and spirit leads to liberation.",
        "shloka_count": 35,
        "color_seed": "#D95D00",
        "shlokas": [
            {
                "verse_num": 1,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "इदं शरीरं कौन्तेय क्षेत्रमित्यभिधीयते ।\nएतद्यो वेत्ति तं प्राहुः क्षेत्रज्ञ इति तद्विदः ॥",
                "hindi": "हे कौन्तेय! यह शरीर 'क्षेत्र' नाम से कहा जाता है; और जो इसे जानता है, उसको तत्त्ववेत्ता ज्ञानी 'क्षेत्रज्ञ' कहते हैं।",
                "english": "This body, O son of Kunti, is called the Field; and he who knows it is called the Knower of the Field by the wise."
            }
        ]
    },
    {
        "number": 14,
        "name_sanskrit": "गुणत्रयविभागयोगः",
        "name_hindi": "गुणत्रयविभागयोग",
        "name_english": "The Three Gunas of Nature",
        "sub_title": "अध्याय १४ • २७ श्लोक",
        "summary_hindi": "प्रकृति के तीन गुण—सत्त्व (प्रकाश/सुख), रजस् (राग/कर्म), और तमस् (प्रमाद/अज्ञान) जीव को बाँधते हैं। इन तीनों गुणों से अतीत होने पर मनुष्य अमरत्व को पाता है।",
        "summary_english": "Prakriti's three fundamental qualities—Sattva (harmony and purity), Rajas (passion and action), and Tamas (inertia and darkness). Transcending the three Gunas bestows immortality.",
        "shloka_count": 27,
        "color_seed": "#026670",
        "shlokas": [
            {
                "verse_num": 6,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "तत्र सत्त्वं निर्मलत्वात्प्रकाशकमनामयम् ।\nसुखसङ्गेन बध्नाति ज्ञानसङ्गेन चानघ ॥",
                "hindi": "हे निष्पाप! उन तीनों में सत्त्वगुण निर्मल होने के कारण प्रकाशक और निर्विकार है; वह सुख की आसक्ति और ज्ञान की आसक्ति से बाँधता है।",
                "english": "Of these, Sattva, being luminous and free from disease on account of its purity, binds by attachment to happiness and by attachment to knowledge, O sinless one."
            }
        ]
    },
    {
        "number": 15,
        "name_sanskrit": "पुरुषोत्तमयोगः",
        "name_hindi": "पुरुषोत्तमयोग",
        "name_english": "The Supreme Divine Person",
        "sub_title": "अध्याय १५ • २० श्लोक",
        "summary_hindi": "उलटे अश्वत्थ वृक्ष का रूपक। क्षर (नश्वर संसार) और अक्षर (कूटस्थ आत्मा) से परे परमात्मा ही 'पुरुषोत्तम' कहलाते हैं।",
        "summary_english": "The sacred metaphor of the cosmic upside-down Ashvattha tree. Higher than both the perishable material creation (Kshara) and the imperishable individual soul (Akshara) is the Supreme Person (Purushottama).",
        "shloka_count": 20,
        "color_seed": "#D95D00",
        "shlokas": [
            {
                "verse_num": 1,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "ऊर्ध्वमूलमधःशाखमश्वत्थं प्राहुरव्ययम् ।\nछन्दांसि यस्य पर्णानि यस्तं वेद स वेदवित् ॥",
                "hindi": "आदि-पुरुष परमात्मा रूप मूल वाले और ब्रह्मारूप मुख्य शाखा वाले संसार-रूपी अश्वत्थ वृक्ष को अविनाशी कहते हैं; जिसके पत्ते वेद हैं, जो इसे जानता है वह वेदवेत्ता है।",
                "english": "They speak of an imperishable Ashvattha tree with its roots above and branches below, whose leaves are the Vedic hymns; he who knows it is a knower of the Vedas."
            },
            {
                "verse_num": 15,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "सर्वस्य चाहं हृदि संनिविष्टो मत्तः स्मृतिर्ज्ञानमपोहनं च ।\nवेदैश्च सर्वैरहमेव वेद्यो वेदान्तकृद्वेदविदेव चाहम् ॥",
                "hindi": "मैं ही सब प्राणियों के हृदय में अन्तर्यामी रूप से स्थित हूँ; मुझसे ही स्मृति, ज्ञान और अपोहन (संशय-निवारण) होता है। सब वेदों द्वारा मैं ही जानने योग्य हूँ।",
                "english": "And I am seated in the hearts of all; from Me are memory, knowledge, and their loss. I alone am to be known through all the Vedas; I am the author of the Vedanta and the knower of the Vedas."
            }
        ]
    },
    {
        "number": 16,
        "name_sanskrit": "दैवासुरसम्पद्विभागयोगः",
        "name_hindi": "दैवासुरसम्पद्विभागयोग",
        "name_english": "Divine & Demonic Qualities",
        "sub_title": "अध्याय १६ • २४ श्लोक",
        "summary_hindi": "दैवी सम्पदा (अभय, सत्य, अहिंसा, त्याग) मनुष्य को मुक्ति की ओर ले जाती है; जबकि आसुरी सम्पदा (दम्भ, दर्प, क्रोध, लोभ) नरक और बन्धन का द्वार है।",
        "summary_english": "The division between divine qualities (fearlessness, purity, truth, forgiveness) that lead to liberation, and the destructive demonic traits (arrogance, wrath, greed, delusion) that lead to bondage.",
        "shloka_count": 24,
        "color_seed": "#026670",
        "shlokas": [
            {
                "verse_num": 1,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "अभयं सत्त्वसंशुद्धिर्ज्ञानयोगव्यवस्थितिः ।\nदानं दमश्च यज्ञश्च स्वाध्यायस्तप आर्जवम् ॥",
                "hindi": "भय का सर्वथा अभाव, अन्तःकरण की शुद्धि, ज्ञान-योग में स्थिति, दान, इन्द्रिय-दमन, यज्ञ, स्वाध्याय, तप और सरलता—ये दैवी सम्पद् के लक्षण हैं।",
                "english": "Fearlessness, purity of heart, steadfastness in knowledge and meditation, charity, self-control, sacrifice, study of scriptures, austerity, and uprightness—these are divine virtues."
            },
            {
                "verse_num": 21,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "त्रिविधं नरकस्येदं द्वारं नाशनमात्मनः ।\nकामः क्रोधस्तथा लोभस्तस्मादेतत्त्रयं त्यजेत् ॥",
                "hindi": "काम, क्रोध और लोभ—यह तीन प्रकार का नरक का द्वार आत्मा का नाश करने वाला है; इसलिए इन तीनों का सर्वथा त्याग करना चाहिए।",
                "english": "Triple is the gateway to darkness destructive of the self: Lust, Anger, and Greed; therefore, these three one should completely abandon."
            }
        ]
    },
    {
        "number": 17,
        "name_sanskrit": "श्रद्धात्रयविभागयोगः",
        "name_hindi": "श्रद्धात्रयविभागयोग",
        "name_english": "The Threefold Faith",
        "sub_title": "अध्याय १७ • २८ श्लोक",
        "summary_hindi": "मनुष्य की श्रद्धा, आहार, यज्ञ, तप और दान तीन प्रकार के (सात्त्विक, राजसिक, तामसिक) होते हैं। ॐ तत् सत् महामन्त्र का गूढ़ अर्थ समझाया गया है।",
        "summary_english": "The threefold manifestation of human faith, food, worship, austerity, and charity according to the Gunas. The profound spiritual meaning of the supreme mantra OM TAT SAT.",
        "shloka_count": 28,
        "color_seed": "#D95D00",
        "shlokas": [
            {
                "verse_num": 3,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "सत्त्वानुरूपा सर्वस्य श्रद्धा भवति भारत ।\nश्रद्धामयोऽयं पुरुषो यो यच्छ्रद्धः स एव सः ॥",
                "hindi": "हे भारत! सभी मनुष्यों की श्रद्धा उनके अन्तःकरण के अनुरूप होती है; मनुष्य श्रद्धामय है, जिसकी जैसी श्रद्धा है वह स्वयं भी वैसा ही है।",
                "english": "The faith of each is in accordance with his nature, O Bharata! Man consists of his faith: as his faith is, so indeed is he."
            }
        ]
    },
    {
        "number": 18,
        "name_sanskrit": "मोक्षसंन्यासयोगः",
        "name_hindi": "मोक्षसंन्यासयोग",
        "name_english": "The Yoga of Ultimate Liberation",
        "sub_title": "अध्याय १८ • ७८ श्लोक",
        "summary_hindi": "गीता का सम्पूर्ण उपसंहार। कर्मफल-त्याग ही सच्चा त्याग है। भगवान् का चरम आश्वाशन: सब धर्मों को त्यागकर केवल मेरी शरण में आओ, मैं तुम्हें समस्त पापों से मुक्त कर दूँगा।",
        "summary_english": "The glorious culmination of the Bhagavad Gita. Renouncing the fruits of all actions is true surrender. The Lord's ultimate promise: Relinquishing all dependencies, take refuge in Me alone; I shall liberate thee from all sorrow.",
        "shloka_count": 78,
        "color_seed": "#026670",
        "shlokas": [
            {
                "verse_num": 65,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "मन्मना भव मद्भक्तो मद्याजी मां नमस्कुरु ।\nमामेवैष्यसि सत्यं ते प्रतिजाने प्रियोऽसि मे ॥",
                "hindi": "मुझमें मन वाला हो, मेरा भक्त बन, मेरा पूजन कर और मुझको नमस्कार कर; ऐसा करने से तू मुझको ही प्राप्त होगा, यह मैं तुझसे सत्य प्रतिज्ञा करता हूँ क्योंकि तू मेरा प्रिय है।",
                "english": "Fix thy mind on Me, be devoted to Me, sacrifice unto Me, bow down to Me. Thou shalt come to Me alone; truly I pledge unto thee, for thou art dear to Me."
            },
            {
                "verse_num": 66,
                "speaker": "श्रीभगवानुवाच",
                "sanskrit": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज ।\nअहं त्वा सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः ॥",
                "hindi": "सम्पूर्ण धर्मों को छोड़कर केवल एक मेरी शरण में आ जा; मैं तुझे सब पापों से मुक्त कर दूँगा, तू शोक मत कर।",
                "english": "Abandoning all duties and dependencies, surrender unto Me alone! I will liberate thee from all sins and sorrow; grieve not!"
            },
            {
                "verse_num": 78,
                "speaker": "सञ्जय उवाच",
                "sanskrit": "यत्र योगेश्वरः कृष्णो यत्र पार्थो धनुर्धरः ।\nतत्र श्रीर्विजयो भूतिर्ध्रुवा नीतिर्मतिर्मम ॥",
                "hindi": "जहाँ योगेश्वर भगवान् श्रीकृष्ण हैं और जहाँ गाण्डीवधनुर्धारी अर्जुन हैं, वहीं श्री, विजय, विभूति और अचल नीति है—ऐसा मेरा मत है।",
                "english": "Wherever is Krishna, the Lord of Yoga, and wherever is Partha, the wielder of the bow, there are fortune, victory, spiritual abundance, and unfailing justice. Such is my conviction."
            }
        ]
    }
]

def build_gita_database(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Parvas table (18 Gita Chapters)
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
            chapter_count INTEGER NOT NULL DEFAULT 1,
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
    
    # 4. FTS5 Search Index
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
    
    # Insert Chapters & Verses
    for ch in GITA_CHAPTERS:
        cur.execute("""
            INSERT INTO parvas (
                id, number, name_sanskrit, name_hindi, name_english,
                sub_title, summary_english, summary_hindi, color_seed,
                chapter_count, shloka_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            ch["number"], ch["number"], ch["name_sanskrit"], ch["name_hindi"], ch["name_english"],
            ch["sub_title"], ch["summary_english"], ch["summary_hindi"], ch["color_seed"],
            ch["shloka_count"]
        ))
        
        cur.execute("""
            INSERT INTO chapters (parva_number, chapter_number, title_sanskrit, title_hindi, title_english, shloka_count)
            VALUES (?, 1, ?, ?, ?, ?)
        """, (ch["number"], ch["name_sanskrit"], ch["name_hindi"], ch["name_english"], ch["shloka_count"]))
        
        for v in ch["shlokas"]:
            iast = devanagari_to_iast(v["sanskrit"])
            tag = f"{ch['number']}.{v['verse_num']}"
            cur.execute("""
                INSERT INTO shlokas (
                    parva_number, chapter_number, verse_number, verse_tag,
                    speaker, sanskrit_devanagari, sanskrit_iast,
                    translation_hindi, translation_english
                ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ch["number"], v["verse_num"], tag,
                v["speaker"], v["sanskrit"], iast,
                v["hindi"], v["english"]
            ))
            
    conn.commit()
    conn.close()
    print(f"Successfully compiled Bhagavad Gita SQLite Database to {db_path}!")

if __name__ == "__main__":
    target = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app/src/main/assets/mahabharata.db"))
    build_gita_database(target)
