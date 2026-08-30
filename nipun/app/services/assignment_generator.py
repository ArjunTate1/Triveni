"""
Assignment Generator - Generate homework assignments with practice problems
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from typing import List, Dict
from app.utils.file_loader import FileLoader
import random


class AssignmentGenerator:
    """
    Generate homework assignments based on domain, topic, and skills.
    Uses local template-based system with emoji-rich Hindi content.
    """

    def __init__(self, base_path: str = "."):
        self.loader = FileLoader(base_path)

    def generate(
        self,
        domain: str,
        topics: List[str],
        skills: List[str],
        grade: str,
        learning_objective: str,
        nipun_reference: str
    ) -> Dict:
        """Generate a comprehensive homework assignment."""
        try:
            templates = self.loader.load_templates("worksheet_templates")
        except FileNotFoundError:
            templates = {}

        assignment = {
            "title": f"{grade} - {domain} होमवर्क असाइनमेंट",
            "grade": grade,
            "domain": domain,
            "topic": ", ".join(topics[:2]),
            "learning_objective": learning_objective,
            "nipun_reference": nipun_reference,
            "instructions": self._get_instructions(domain),
            "sections": [],
            "total_questions": 0,
            "due_date": "अगले सप्ताह तक जमा करें"
        }

        # Section 1: Basic Practice
        s1 = self._generate_practice_section(domain, topics, templates)
        if s1:
            assignment["sections"].append(s1)
            assignment["total_questions"] += len(s1["problems"])

        # Section 2: Fill in the Blanks
        s2 = self._generate_fill_blanks_section(domain, topics)
        if s2:
            assignment["sections"].append(s2)
            assignment["total_questions"] += len(s2["problems"])

        # Section 3: Word Problems / Application
        s3 = self._generate_application_section(domain, topics)
        if s3:
            assignment["sections"].append(s3)
            assignment["total_questions"] += len(s3["problems"])

        # Section 4: True / False
        s4 = self._generate_true_false_section(domain, topics)
        if s4:
            assignment["sections"].append(s4)
            assignment["total_questions"] += len(s4["problems"])

        # Section 5: Creative / Extension Activity
        s5 = self._generate_creative_section(domain, topics)
        if s5:
            assignment["sections"].append(s5)

        return assignment

    # ──────────────────────────────────────────────────────────────
    # INSTRUCTIONS
    # ──────────────────────────────────────────────────────────────

    def _get_instructions(self, domain: str) -> str:
        if domain == "Numeracy":
            return "सभी प्रश्नों को हल करें। अपना काम साफ और व्यवस्थित रखें। 🎯"
        return "सभी प्रश्नों के उत्तर अपनी कॉपी में लिखें। साफ और सुंदर लिखें। ✍️"

    # ──────────────────────────────────────────────────────────────
    # SECTION 1 – BASIC PRACTICE
    # ──────────────────────────────────────────────────────────────

    def _generate_practice_section(
        self, domain: str, topics: List[str], templates: Dict
    ) -> Dict:
        problems = []
        num = 1

        if domain == "Numeracy":
            problems += self._numeracy_basic_problems(topics)
        else:
            problems += self._literacy_basic_problems(topics)

        # Re-number
        for i, p in enumerate(problems, start=1):
            p["problem_number"] = i

        return {
            "section_title": "भाग 1: अभ्यास के सवाल 📝",
            "section_instructions": "सभी सवालों को हल करें।",
            "problems": problems[:10]
        }

    def _numeracy_basic_problems(self, topics: List[str]) -> List[Dict]:
        """10 varied numeracy practice problems."""
        pool = []

        # Addition
        for _ in range(4):
            a = random.randint(1, 9)
            b = random.randint(1, 9)
            pool.append({
                "problem_number": 0,
                "question": f"🔢 {a} + {b} = ___",
                "answer_space": "___",
                "correct_answer": str(a + b)
            })

        # Subtraction
        for _ in range(3):
            a = random.randint(5, 15)
            b = random.randint(1, a)
            pool.append({
                "problem_number": 0,
                "question": f"🔢 {a} - {b} = ___",
                "answer_space": "___",
                "correct_answer": str(a - b)
            })

        # Counting
        emojis = ["🍎", "⭐", "🌸", "🎈", "🐟"]
        for _ in range(3):
            count = random.randint(3, 9)
            emoji = random.choice(emojis)
            pool.append({
                "problem_number": 0,
                "question": f"{emoji * count} गिनो और लिखो:",
                "answer_space": "___",
                "correct_answer": str(count)
            })

        random.shuffle(pool)
        return pool[:10]

    def _literacy_basic_problems(self, topics: List[str]) -> List[Dict]:
        """10 varied literacy practice problems."""
        pool = []

        # Vowels
        if "letter_recognition" in topics or "vowels" in topics or not topics:
            pool += [
                {
                    "problem_number": 0,
                    "question": "पहले 5 स्वर लिखो: ___, ___, ___, ___, ___",
                    "answer_space": "",
                    "correct_answer": "अ, आ, इ, ई, उ"
                },
                {
                    "problem_number": 0,
                    "question": "'क' से 'ङ' तक वर्ण लिखो।",
                    "answer_space": "",
                    "correct_answer": "क, ख, ग, घ, ङ"
                },
                {
                    "problem_number": 0,
                    "question": "तीन व्यंजन वर्ण लिखो जो 'ट वर्ग' में हैं।",
                    "answer_space": "1.___ 2.___ 3.___",
                    "correct_answer": "ट, ठ, ड"
                },
            ]

        # Words
        if "word_reading" in topics or "writing" in topics or not topics:
            pool += [
                {
                    "problem_number": 0,
                    "question": "दो अक्षर के 5 शब्द लिखो (जैसे: घर, नल, बस)",
                    "answer_space": "1.___ 2.___ 3.___ 4.___ 5.___",
                    "correct_answer": "varies"
                },
                {
                    "problem_number": 0,
                    "question": "'म' से शुरू होने वाले 4 शब्द लिखो।",
                    "answer_space": "1.___ 2.___ 3.___ 4.___",
                    "correct_answer": "माँ, मछली, मकान, मोर"
                },
                {
                    "problem_number": 0,
                    "question": "'स' से शुरू होने वाले 4 शब्द लिखो।",
                    "answer_space": "1.___ 2.___ 3.___ 4.___",
                    "correct_answer": "सेब, सूरज, सड़क, सबक"
                },
                {
                    "problem_number": 0,
                    "question": "तीन अक्षर के 3 शब्द लिखो (जैसे: कमल, नमक, तबला)।",
                    "answer_space": "1.___ 2.___ 3.___",
                    "correct_answer": "varies"
                },
            ]

        # Sentence
        pool += [
            {
                "problem_number": 0,
                "question": "इन शब्दों से एक सही वाक्य बनाओ: 'रहता / मैं / घर / में'",
                "answer_space": "___________________________",
                "correct_answer": "मैं घर में रहता हूँ।"
            },
            {
                "problem_number": 0,
                "question": "नीचे दिए शब्द के विलोम (उल्टे अर्थ) लिखो: दिन → ___",
                "answer_space": "___",
                "correct_answer": "रात"
            },
            {
                "problem_number": 0,
                "question": "खाली जगह भरो: आसमान का रंग ___ है।",
                "answer_space": "___",
                "correct_answer": "नीला"
            },
        ]

        random.shuffle(pool)
        return pool[:10]

    # ──────────────────────────────────────────────────────────────
    # SECTION 2 – FILL IN THE BLANKS
    # ──────────────────────────────────────────────────────────────

    def _generate_fill_blanks_section(self, domain: str, topics: List[str]) -> Dict:
        problems = []

        if domain == "Numeracy":
            blanks = [
                ("3 + ___ = 7", "4"),
                ("___ + 2 = 9", "7"),
                ("10 - ___ = 6", "4"),
                ("___ - 3 = 5", "8"),
                ("5 के बाद की संख्या: ___", "6"),
                ("12 से पहले की संख्या: ___", "11"),
                ("सबसे छोटी एकल अंक वाली संख्या: ___", "1"),
                ("सबसे बड़ी एकल अंक वाली संख्या: ___", "9"),
                ("2, 4, 6, ___, 10 — खाली जगह भरो।", "8"),
                ("1, 3, 5, ___, 9 — खाली जगह भरो।", "7"),
            ]
        else:
            blanks = [
                ("हिंदी वर्णमाला में ___ स्वर होते हैं।", "11 (या 13)"),
                ("'कमल' शब्द में ___ अक्षर हैं।", "3"),
                ("'पुस्तक' का अर्थ ___ होता है।", "किताब / Book"),
                ("'माँ' शब्द में ___ मात्रा है।", "आ की मात्रा"),
                ("वाक्य के अंत में ___ लगता है।", "पूर्णविराम (।)"),
                ("'क' के बाद ___ आता है।", "ख"),
                ("'आ' की मात्रा वाला एक शब्द: ___", "माँ / राज / आम"),
                ("'नदी' में बहने वाला द्रव: ___", "पानी"),
                ("'सूरज' ___ से उगता है।", "पूर्व"),
                ("'दिन' का विलोम: ___", "रात"),
            ]

        for i, (q, ans) in enumerate(blanks, start=1):
            problems.append({
                "problem_number": i,
                "question": q,
                "answer_space": "___",
                "correct_answer": ans
            })

        return {
            "section_title": "भाग 2: खाली जगह भरो ✏️",
            "section_instructions": "सही उत्तर लिखकर खाली जगह पूरी करें।",
            "problems": problems
        }

    # ──────────────────────────────────────────────────────────────
    # SECTION 3 – APPLICATION / WORD PROBLEMS
    # ──────────────────────────────────────────────────────────────

    def _generate_application_section(self, domain: str, topics: List[str]) -> Dict:
        problems = []

        if domain == "Numeracy":
            problems = [
                {
                    "problem_number": 1,
                    "question": "रमेश की टोकरी में 🍎 5 सेब हैं और गीता की टोकरी में 🍎 3 सेब हैं। दोनों में कुल कितने सेब हैं?",
                    "work_space": "हल:",
                    "correct_answer": "8"
                },
                {
                    "problem_number": 2,
                    "question": "पार्क में 🐦 9 चिड़िया बैठी थीं। 🐦 4 उड़ गईं। अब कितनी बची हैं?",
                    "work_space": "हल:",
                    "correct_answer": "5"
                },
                {
                    "problem_number": 3,
                    "question": "सीता के पास 🎈 7 गुब्बारे हैं और रीता के पास 🎈 5 गुब्बारे हैं। किसके पास अधिक और कितने अधिक?",
                    "work_space": "हल:",
                    "correct_answer": "सीता के पास 2 अधिक"
                },
                {
                    "problem_number": 4,
                    "question": "दुकान में 🍌 6 केले और 🍊 4 संतरे हैं। कुल कितने फल हैं?",
                    "work_space": "हल:",
                    "correct_answer": "10"
                },
                {
                    "problem_number": 5,
                    "question": "राम के पास 🖊️ 10 पेंसिलें थीं। उसने 3 दोस्त को दीं। उसके पास कितनी बचीं?",
                    "work_space": "हल:",
                    "correct_answer": "7"
                },
                {
                    "problem_number": 6,
                    "question": "एक थैले में 🍬 5 टॉफियाँ हैं। दूसरे थैले में 🍬 6 टॉफियाँ हैं। दोनों मिलाकर कुल कितनी?",
                    "work_space": "हल:",
                    "correct_answer": "11"
                },
                {
                    "problem_number": 7,
                    "question": "कक्षा में 8 लड़के और 7 लड़कियाँ हैं। कुल कितने बच्चे हैं?",
                    "work_space": "हल:",
                    "correct_answer": "15"
                },
                {
                    "problem_number": 8,
                    "question": "मेज पर 🌸 12 फूल थे। 5 फूल गिर गए। अब कितने बचे?",
                    "work_space": "हल:",
                    "correct_answer": "7"
                },
            ]
        else:
            problems = [
                {
                    "problem_number": 1,
                    "question": "अपने सबसे अच्छे दोस्त के बारे में 3 वाक्य लिखो। 👦👧",
                    "work_space": "1.___ 2.___ 3.___",
                    "correct_answer": "varies"
                },
                {
                    "problem_number": 2,
                    "question": "'🏠 घर' शब्द का उपयोग करके दो वाक्य बनाओ।",
                    "work_space": "1.___ 2.___",
                    "correct_answer": "varies (जैसे: मैं घर जा रहा हूँ।)"
                },
                {
                    "problem_number": 3,
                    "question": "इन शब्दों को वर्णमाला क्रम में लिखो: 🦁 शेर, 🐘 हाथी, 🐄 गाय, 🐟 मछली",
                    "work_space": "क्रम: ___, ___, ___, ___",
                    "correct_answer": "गाय, मछली, शेर, हाथी"
                },
                {
                    "problem_number": 4,
                    "question": "नीचे दिए अक्षरों से एक सार्थक शब्द बनाओ: ल - म - क → ___",
                    "work_space": "___",
                    "correct_answer": "कमल"
                },
                {
                    "problem_number": 5,
                    "question": "अपने परिवार के 4 सदस्यों के नाम हिंदी में लिखो।",
                    "work_space": "1.___ 2.___ 3.___ 4.___",
                    "correct_answer": "varies"
                },
                {
                    "problem_number": 6,
                    "question": "नीचे दिए शब्दों को पढ़कर उनके अर्थ अंग्रेजी में लिखो: पानी → ___, घर → ___, माँ → ___",
                    "work_space": "",
                    "correct_answer": "Water, Home/House, Mother"
                },
                {
                    "problem_number": 7,
                    "question": "एक छोटी कहानी में से सही कारक चुनो: 'राम ___ स्कूल जाता है।' (को / में / से)",
                    "work_space": "___",
                    "correct_answer": "को (राम को / की ओर)"
                },
                {
                    "problem_number": 8,
                    "question": "सही विराम चिन्ह लगाओ: 'तुम्हारा नाम क्या है___'",
                    "work_space": "___",
                    "correct_answer": "? (प्रश्नवाचक चिन्ह)"
                },
            ]

        return {
            "section_title": "भाग 3: शब्द समस्याएं / लागू करना 🧩",
            "section_instructions": "ध्यान से पढ़ें और हल करें।",
            "problems": problems
        }

    # ──────────────────────────────────────────────────────────────
    # SECTION 4 – TRUE / FALSE
    # ──────────────────────────────────────────────────────────────

    def _generate_true_false_section(self, domain: str, topics: List[str]) -> Dict:
        problems = []

        if domain == "Numeracy":
            statements = [
                ("5 + 3 = 8", True),
                ("10 - 4 = 7", False),
                ("9 > 6 (नौ, छह से बड़ा है)", True),
                ("3 + 3 = 7", False),
                ("सबसे छोटी दो-अंकीय संख्या 10 है।", True),
                ("7 - 7 = 1", False),
                ("2, 4, 6, 8 — ये सम (even) संख्याएं हैं।", True),
                ("15 < 12 (पन्द्रह, बारह से छोटा है)", False),
            ]
        else:
            statements = [
                ("हिंदी वर्णमाला में 'अ' पहला अक्षर है।", True),
                ("'क' एक स्वर है।", False),
                ("'माँ' में 'आ' की मात्रा है।", True),
                ("'घर' शब्द में 3 अक्षर हैं।", False),
                ("वाक्य के अंत में पूर्णविराम (।) लगाते हैं।", True),
                ("'दिन' और 'रात' विलोम शब्द हैं।", True),
                ("'कमल' में 2 अक्षर हैं।", False),
                ("'ब' से 'बिल्ली' शब्द बनता है।", True),
            ]

        for i, (stmt, answer) in enumerate(statements, start=1):
            problems.append({
                "problem_number": i,
                "question": f"सही है या गलत? / True or False?\n'{stmt}'",
                "answer_space": "सही / गलत (True / False)",
                "correct_answer": "सही ✅" if answer else "गलत ❌"
            })

        return {
            "section_title": "भाग 4: सही या गलत ✅❌",
            "section_instructions": "नीचे दिए वाक्य पढ़ें और सही (✅) या गलत (❌) लिखें।",
            "problems": problems
        }

    # ──────────────────────────────────────────────────────────────
    # SECTION 5 – CREATIVE / EXTENSION
    # ──────────────────────────────────────────────────────────────

    def _generate_creative_section(self, domain: str, topics: List[str]) -> Dict:
        if domain == "Numeracy":
            return {
                "section_title": "भाग 5: रचनात्मक गतिविधि 🎨",
                "activity_description": (
                    "अपने घर में 10 चीजें खोजो और उन्हें गिनो। "
                    "फिर एक तालिका (table) बनाओ।"
                ),
                "example": (
                    "जैसे:\n"
                    "🪑 कुर्सी = 4\n"
                    "📚 किताबें = 7\n"
                    "✏️ पेंसिलें = 6"
                ),
                "bonus": "बोनस: जोड़ो — कुल चीजें = ___",
                "instruction": "कम से कम 5 चीजों की सूची बनाओ। 📝"
            }
        else:
            return {
                "section_title": "भाग 5: रचनात्मक लेखन ✍️",
                "activity_description": (
                    "अपने पसंदीदा जानवर के बारे में 5-6 वाक्य लिखो "
                    "और एक चित्र बनाओ। 🐾"
                ),
                "example": (
                    "जैसे: मुझे 🐕 कुत्ता पसंद है।\n"
                    "वह वफादार होता है।\n"
                    "वह भौंकता है।\n"
                    "वह मेरे साथ खेलता है।\n"
                    "उसकी आँखें बड़ी-बड़ी होती हैं।"
                ),
                "bonus": "बोनस: उस जानवर के 3 विशेषण (adjectives) लिखो।",
                "instruction": "अपनी कल्पना का उपयोग करो! 🌈"
            }
