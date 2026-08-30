"""
Assessment Generator - Generate assessments with 10+ questions always
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from typing import List, Dict
from app.utils.file_loader import FileLoader
import random


class AssessmentGenerator:
    """
    Generate assessments with guaranteed 10+ questions.
    Uses a built-in question bank - no template dependency.
    """

    def __init__(self, base_path: str = "."):
        self.loader = FileLoader(base_path)

    def generate(
        self,
        grade: str,
        domain: str,
        topic: str,
        learning_objective: str,
        topics: List[str],
        skills: List[str],
        nipun_outcome_id: str
    ) -> Dict:
        """Generate an assessment with 10+ questions."""

        if domain == "Numeracy" or domain == "Unknown":
            questions = self._numeracy_questions(topics, nipun_outcome_id)
        else:
            questions = self._literacy_questions(topics, nipun_outcome_id)

        # Re-number
        for i, q in enumerate(questions, start=1):
            q["question_number"] = i

        total_marks = len(questions) * 2

        return {
            "title": f"{grade} - {domain} मूल्यांकन / Assessment",
            "grade": grade,
            "domain": domain,
            "topic": topic or ", ".join(topics[:2]) or "General",
            "learning_objective": learning_objective,
            "nipun_reference": nipun_outcome_id,
            "instructions": (
                "सभी प्रश्नों के उत्तर दें। प्रत्येक प्रश्न 2 अंक का है। / "
                "Answer all questions. Each question carries 2 marks."
            ),
            "duration": "30-40 मिनट / minutes",
            "questions": questions,
            "total_marks": total_marks,
        }

    # ──────────────────────────────────────────────────────────────
    # NUMERACY BANK
    # ──────────────────────────────────────────────────────────────

    def _numeracy_questions(self, topics: List[str], ref: str) -> List[Dict]:
        pool = []

        # Counting
        for _ in range(3):
            n = random.randint(3, 9)
            emoji = random.choice(["🍎", "⭐", "🌸", "🎈", "🐟"])
            pool.append(self._q(
                f"{emoji * n} — इन्हें गिनो और लिखो। / Count and write.",
                str(n), "counting", "easy", ref
            ))

        # Addition
        for _ in range(3):
            a, b = random.randint(1, 9), random.randint(1, 9)
            pool.append(self._q(
                f"{a} + {b} = ___",
                str(a + b), "addition", "easy", ref
            ))

        # Subtraction
        for _ in range(3):
            a = random.randint(5, 15)
            b = random.randint(1, a)
            pool.append(self._q(
                f"{a} - {b} = ___",
                str(a - b), "subtraction", "medium", ref
            ))

        # Comparison
        for _ in range(2):
            a, b = random.randint(1, 15), random.randint(1, 15)
            while a == b:
                b = random.randint(1, 15)
            pool.append(self._q(
                f"{a} और {b} में से बड़ी संख्या कौन सी है? / Which is greater?",
                str(max(a, b)), "comparison", "easy", ref
            ))

        # Number sequence
        for _ in range(2):
            n = random.randint(1, 18)
            pool.append(self._q(
                f"संख्या {n} के बाद कौन सी संख्या आती है? / What comes after {n}?",
                str(n + 1), "number_sequence", "easy", ref
            ))

        # Word problems
        wp_data = [
            (random.randint(2, 8), random.randint(1, 5), "add"),
            (random.randint(5, 10), random.randint(1, 4), "sub"),
            (random.randint(3, 7), random.randint(2, 6), "add"),
        ]
        for a, b, op in wp_data:
            if op == "add":
                pool.append(self._q(
                    f"रमेश के पास {a} पेंसिलें थीं। उसने {b} और खरीदीं। अब कितनी? / Ramesh had {a} pencils, bought {b} more. Total?",
                    str(a + b), "word_problem", "medium", ref
                ))
            else:
                pool.append(self._q(
                    f"पेड़ पर {a} 🐦 बैठी थीं। {b} उड़ गईं। कितनी बचीं? / {a} birds sat on tree, {b} flew away. How many left?",
                    str(a - b), "word_problem", "medium", ref
                ))

        # Fill in the blanks
        blanks = [
            ("2, 4, 6, ___, 10 — खाली जगह भरो।", "8", "pattern"),
            ("1, 3, 5, ___, 9 — खाली जगह भरो।", "7", "pattern"),
            ("सबसे छोटी एकल अंक वाली संख्या: ___", "1", "number_sense"),
            ("सबसे बड़ी एकल अंक वाली संख्या: ___", "9", "number_sense"),
            ("दस को अंक में लिखो: ___", "10", "number_writing"),
        ]
        for q_text, ans, skill in blanks:
            pool.append(self._q(q_text, ans, skill, "easy", ref))

        # True / False
        tf = [
            ("5 + 3 = 8 — सही है या गलत? / True or False?", "सही ✅", "addition"),
            ("7 > 9 — सही है या गलत? / True or False?", "गलत ❌", "comparison"),
            ("10 - 4 = 6 — सही है या गलत? / True or False?", "सही ✅", "subtraction"),
        ]
        for q_text, ans, skill in tf:
            pool.append(self._q(q_text, ans, skill, "easy", ref))

        random.shuffle(pool)
        return pool[:12]

    # ──────────────────────────────────────────────────────────────
    # LITERACY BANK
    # ──────────────────────────────────────────────────────────────

    def _literacy_questions(self, topics: List[str], ref: str) -> List[Dict]:
        pool = []

        # Vowel recognition
        vowels = ["अ", "आ", "इ", "ई", "उ", "ऊ", "ए", "ओ"]
        consonants = ["क", "ख", "ग", "घ", "च", "ट", "त", "न", "म", "र"]
        for _ in range(2):
            v = random.choice(vowels)
            pool.append(self._q(
                f"'{v}' — यह स्वर है या व्यंजन? / Is this a vowel or consonant?",
                "स्वर / Vowel", "vowel_recognition", "easy", ref
            ))
        for _ in range(2):
            c = random.choice(consonants)
            pool.append(self._q(
                f"'{c}' — यह स्वर है या व्यंजन? / Is this a vowel or consonant?",
                "व्यंजन / Consonant", "consonant_recognition", "easy", ref
            ))

        # Word reading
        words = [
            ("🏠", "घर"), ("💧", "पानी"), ("🌳", "पेड़"),
            ("📚", "किताब"), ("☀️", "सूरज"), ("🐄", "गाय"),
        ]
        for _ in range(3):
            emoji, word = random.choice(words)
            pool.append(self._q(
                f"{emoji} इस चित्र का हिंदी नाम लिखो। / Write the Hindi name.",
                word, "word_recognition", "easy", ref
            ))

        # Letter to word
        letters = {
            "क": "कमल", "म": "माँ", "घ": "घर",
            "स": "सेब", "न": "नदी", "र": "राजा",
        }
        for letter, example in list(letters.items())[:3]:
            pool.append(self._q(
                f"'{letter}' से शुरू होने वाला एक शब्द लिखो। / Write a word starting with '{letter}'.",
                f"{example} (या अन्य / or other)", "phonics", "easy", ref
            ))

        # Opposites
        opp_pairs = [
            ("दिन / Day", "रात / Night"),
            ("गर्म / Hot", "ठंडा / Cold"),
            ("बड़ा / Big", "छोटा / Small"),
            ("ऊपर / Up", "नीचे / Down"),
        ]
        for word, ans in opp_pairs[:3]:
            pool.append(self._q(
                f"'{word}' का विलोम शब्द लिखो। / Write the opposite.",
                ans, "vocabulary", "medium", ref
            ))

        # Sentence completion
        sentences = [
            ("आसमान का रंग ___ है।", "नीला / Blue"),
            ("सूरज ___ से उगता है।", "पूर्व / East"),
            ("हम भोजन ___ से खाते हैं।", "हाथ / Hands"),
            ("वाक्य के अंत में ___ लगाते हैं।", "पूर्णविराम (।)"),
        ]
        for q_text, ans in sentences[:3]:
            pool.append(self._q(q_text, ans, "sentence_completion", "medium", ref))

        # Word formation
        formations = [
            ("क + म + ल = ___", "कमल"),
            ("न + म + क = ___", "नमक"),
            ("घ + र = ___", "घर"),
        ]
        for q_text, ans in formations:
            pool.append(self._q(q_text, ans, "word_formation", "medium", ref))

        # True / False
        tf = [
            ("'क' एक स्वर है। / 'क' is a vowel. — सही या गलत?", "गलत ❌"),
            ("'अ' हिंदी वर्णमाला का पहला अक्षर है। — सही या गलत?", "सही ✅"),
            ("'दिन' और 'रात' विलोम शब्द हैं। — सही या गलत?", "सही ✅"),
        ]
        for q_text, ans in tf:
            pool.append(self._q(q_text, ans, "true_false", "easy", ref))

        # Comprehension
        pool.append(self._q(
            "इस वाक्य को पढ़कर उत्तर दो: 'राम स्कूल जाता है।' — राम कहाँ जाता है?",
            "स्कूल / School", "comprehension", "medium", ref
        ))
        pool.append(self._q(
            "इन शब्दों से एक वाक्य बनाओ: 'जाता / स्कूल / राम / है'",
            "राम स्कूल जाता है।", "writing", "medium", ref
        ))

        random.shuffle(pool)
        return pool[:12]

    # ──────────────────────────────────────────────────────────────
    # HELPER
    # ──────────────────────────────────────────────────────────────

    def _q(
        self,
        question: str,
        answer: str,
        skill: str,
        difficulty: str,
        ref: str,
        question_number: int = 0
    ) -> Dict:
        return {
            "question_number": question_number,
            "question": question,
            "question_type": skill,
            "expected_answer": answer,
            "skill": skill,
            "difficulty": difficulty,
            "learning_outcome_reference": ref
        }
