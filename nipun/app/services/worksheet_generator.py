"""
Worksheet Generator - Generate worksheets from templates
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from typing import List, Dict
from app.utils.file_loader import FileLoader
import random


class WorksheetGenerator:
    """Generate Hindi worksheets using local templates and expanded question banks."""

    def __init__(self, base_path: str = "."):
        self.loader = FileLoader(base_path)

    def generate(
        self,
        grade: str,
        domain: str,
        topic: str,
        learning_objective: str,
        nipun_reference: str,
        topics: List[str],
        skills: List[str]
    ) -> Dict:
        """Generate a comprehensive worksheet."""
        try:
            templates = self.loader.load_templates("worksheet_templates")
        except FileNotFoundError:
            templates = {}

        # Generate questions from templates (up to 5 per topic, 4 topics max)
        questions = []
        question_num = 1

        for detected_topic in topics[:4]:
            topic_questions = self._generate_questions_for_topic(
                detected_topic, domain, question_num, templates
            )
            questions.extend(topic_questions)
            question_num += len(topic_questions)

        # Always add domain-specific questions from the built-in bank
        # (runs unconditionally so even empty-topic / Unknown domain gets 10+)
        extra = self._generate_extra_questions(domain, topics, question_num)
        questions.extend(extra)
        question_num += len(extra)

        # If still fewer than 10 questions, pad with defaults
        if len(questions) < 10:
            defaults = self._default_questions(domain, grade, question_num)
            questions.extend(defaults)

        # Re-number everything cleanly
        for i, q in enumerate(questions, start=1):
            q["question_number"] = i

        answer_key = {q["question_number"]: q["correct_answer"] for q in questions}

        return {
            "grade": grade,
            "domain": domain,
            "topic": topic or ", ".join(topics),
            "learning_objective": learning_objective,
            "nipun_reference": nipun_reference,
            "instructions": self._get_instructions(domain),
            "questions": questions,
            "answer_key": answer_key
        }

    # ──────────────────────────────────────────────────────────────
    # TEMPLATE-BASED QUESTIONS
    # ──────────────────────────────────────────────────────────────

    def _generate_questions_for_topic(
        self, topic: str, domain: str, start_num: int, templates: Dict
    ) -> List[Dict]:
        if topic not in templates:
            return []

        topic_templates = templates[topic].get("templates", [])
        questions = []

        for i, template in enumerate(topic_templates[:5]):  # up to 5 per topic
            q = self._build_question_from_template(template, start_num + i, topic)
            if q:
                questions.append(q)

        return questions

    def _build_question_from_template(
        self, template: Dict, question_num: int, skill: str
    ) -> Dict:
        question_type = template.get("type", "सही उत्तर चुनो")
        question_text = template.get("question", "")

        if "{num1}" in question_text:
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            question_text = question_text.replace("{num1}", str(num1))
            question_text = question_text.replace("{num2}", str(num2))

            if "+" in question_text:
                correct_answer = str(num1 + num2)
            elif "-" in question_text:
                correct_answer = str(abs(num1 - num2))
            elif "बड़ा" in question_text or "अधिक" in question_text:
                correct_answer = str(max(num1, num2))
            else:
                correct_answer = str(num1 + num2)

        elif "{object}" in question_text:
            obj = random.choice(["सेब", "गेंद", "तारे", "फूल"])
            question_text = question_text.replace("{object}", obj)
            correct_answer = str(random.randint(1, 10))

        elif "{number}" in question_text:
            num = random.randint(1, 10)
            question_text = question_text.replace("{number}", str(num))
            correct_answer = str(num)

        else:
            correct_answer = "उत्तर"

        return {
            "question_number": question_num,
            "question_type": question_type,
            "question_text": question_text,
            "options": None,
            "correct_answer": correct_answer,
            "skill": skill
        }

    # ──────────────────────────────────────────────────────────────
    # EXTRA BUILT-IN QUESTION BANK
    # ──────────────────────────────────────────────────────────────

    def _generate_extra_questions(
        self, domain: str, topics: List[str], start_num: int
    ) -> List[Dict]:
        # Treat Unknown as Numeracy (most common fallback)
        effective_domain = domain if domain in ("Numeracy", "Literacy") else "Numeracy"
        if effective_domain == "Numeracy":
            return self._numeracy_bank(topics, start_num)
        return self._literacy_bank(topics, start_num)

    def _numeracy_bank(self, topics: List[str], start_num: int) -> List[Dict]:
        pool = []

        pool += [
            {"question_type": "जोड़ करो", "question_text": f"{random.randint(1,9)} + {random.randint(1,9)} = ___",
             "skill": "addition", "correct_answer": "?"},
            {"question_type": "घटाओ", "question_text": f"{random.randint(5,15)} - {random.randint(1,5)} = ___",
             "skill": "subtraction", "correct_answer": "?"},
            {"question_type": "तुलना करो", "question_text": "9 ___ 6 (>, < या = लिखो)",
             "skill": "comparison", "correct_answer": ">"},
            {"question_type": "खाली भरो", "question_text": "2, 4, 6, ___, 10",
             "skill": "pattern", "correct_answer": "8"},
            {"question_type": "खाली भरो", "question_text": "1, 3, 5, ___, 9",
             "skill": "pattern", "correct_answer": "7"},
            {"question_type": "संख्या लिखो", "question_text": "पाँच को अंक में लिखो: ___",
             "skill": "number_writing", "correct_answer": "5"},
            {"question_type": "शब्द में लिखो", "question_text": "7 को शब्द में लिखो: ___",
             "skill": "number_writing", "correct_answer": "सात"},
            {"question_type": "गिनो", "question_text": "🍎🍎🍎🍎🍎🍎 इन सेबों को गिनो: ___",
             "skill": "counting", "correct_answer": "6"},
            {"question_type": "क्रम लगाओ", "question_text": "9, 3, 7, 1, 5 — इन्हें बढ़ते क्रम में लिखो।",
             "skill": "ordering", "correct_answer": "1, 3, 5, 7, 9"},
            {"question_type": "क्रम लगाओ", "question_text": "2, 8, 4, 10, 6 — घटते क्रम में लिखो।",
             "skill": "ordering", "correct_answer": "10, 8, 6, 4, 2"},
            {"question_type": "जोड़ करो", "question_text": "10 + 5 = ___",
             "skill": "addition", "correct_answer": "15"},
            {"question_type": "घटाओ", "question_text": "20 - 8 = ___",
             "skill": "subtraction", "correct_answer": "12"},
        ]

        # Fix the ? answers with real computed values
        for p in pool:
            if p["correct_answer"] == "?":
                nums = [int(s) for s in p["question_text"].split() if s.isdigit()]
                if "+" in p["question_text"] and len(nums) >= 2:
                    p["correct_answer"] = str(nums[0] + nums[1])
                elif "-" in p["question_text"] and len(nums) >= 2:
                    p["correct_answer"] = str(nums[0] - nums[1])

        random.shuffle(pool)
        questions = []
        for i, p in enumerate(pool[:12], start=start_num):
            questions.append({
                "question_number": i,
                "question_type": p["question_type"],
                "question_text": p["question_text"],
                "options": None,
                "correct_answer": p["correct_answer"],
                "skill": p["skill"]
            })
        return questions

    def _literacy_bank(self, topics: List[str], start_num: int) -> List[Dict]:
        pool = [
            {"question_type": "वर्ण लिखो",
             "question_text": "'आ' की मात्रा वाले 3 शब्द लिखो।",
             "skill": "matra", "correct_answer": "माँ, राज, आम"},
            {"question_type": "वर्ण लिखो",
             "question_text": "'इ' की मात्रा वाले 3 शब्द लिखो।",
             "skill": "matra", "correct_answer": "किला, दिल, मिल"},
            {"question_type": "सुमेल करो",
             "question_text": "मिलान करो: 🐄 — ___, 🐟 — ___, 🐕 — ___",
             "skill": "vocabulary", "correct_answer": "गाय, मछली, कुत्ता"},
            {"question_type": "वाक्य बनाओ",
             "question_text": "'पानी' शब्द का उपयोग कर एक वाक्य लिखो।",
             "skill": "writing", "correct_answer": "varies"},
            {"question_type": "विलोम लिखो",
             "question_text": "विलोम लिखो: गर्म → ___, बड़ा → ___, दिन → ___",
             "skill": "vocabulary", "correct_answer": "ठंडा, छोटा, रात"},
            {"question_type": "अक्षर पहचानो",
             "question_text": "इनमें से स्वर कौन से हैं? क, अ, ग, ई, ट, उ",
             "skill": "vowel_recognition", "correct_answer": "अ, ई, उ"},
            {"question_type": "शब्द जोड़ो",
             "question_text": "अक्षरों को जोड़कर शब्द बनाओ: क + म + ल = ___",
             "skill": "word_formation", "correct_answer": "कमल"},
            {"question_type": "शब्द जोड़ो",
             "question_text": "ना + म + क = ___",
             "skill": "word_formation", "correct_answer": "नमक"},
            {"question_type": "वाक्य पूरा करो",
             "question_text": "खाली जगह भरो: सूरज ___ से उगता है।",
             "skill": "general_knowledge", "correct_answer": "पूर्व"},
            {"question_type": "सही शब्द चुनो",
             "question_text": "सही शब्द चुनो: बच्चा स्कूल ___ जाता है। (को / में / से)",
             "skill": "grammar", "correct_answer": "को"},
            {"question_type": "लिखो",
             "question_text": "अपना पूरा नाम हिंदी में लिखो।",
             "skill": "writing", "correct_answer": "varies"},
            {"question_type": "पढ़ो",
             "question_text": "इस वाक्य को पढ़कर उत्तर दो: 'राम स्कूल जाता है।' — राम कहाँ जाता है?",
             "skill": "comprehension", "correct_answer": "स्कूल"},
        ]

        random.shuffle(pool)
        questions = []
        for i, p in enumerate(pool[:12], start=start_num):
            questions.append({
                "question_number": i,
                "question_type": p["question_type"],
                "question_text": p["question_text"],
                "options": None,
                "correct_answer": p["correct_answer"],
                "skill": p["skill"]
            })
        return questions

    # ──────────────────────────────────────────────────────────────
    # DEFAULTS (fallback if templates are missing)
    # ──────────────────────────────────────────────────────────────

    def _default_questions(
        self, domain: str, grade: str, start_num: int
    ) -> List[Dict]:
        if domain == "Numeracy":
            base = [
                {"question_type": "जोड़ करो", "question_text": "2 + 3 = ____",
                 "correct_answer": "5", "skill": "addition"},
                {"question_type": "गिनकर लिखो", "question_text": "🍎🍎🍎🍎🍎 सेब गिनो:",
                 "correct_answer": "5", "skill": "counting"},
                {"question_type": "घटाओ", "question_text": "8 - 3 = ____",
                 "correct_answer": "5", "skill": "subtraction"},
                {"question_type": "तुलना", "question_text": "7 ___ 4 (> या <)",
                 "correct_answer": ">", "skill": "comparison"},
                {"question_type": "क्रम", "question_text": "1, 2, ___, 4, 5",
                 "correct_answer": "3", "skill": "sequence"},
            ]
        else:
            base = [
                {"question_type": "अक्षर पहचानो", "question_text": "यह कौन सा अक्षर है? 'अ'",
                 "correct_answer": "अ", "skill": "letter_recognition"},
                {"question_type": "शब्द लिखो", "question_text": "🏠 = ___",
                 "correct_answer": "घर", "skill": "vocabulary"},
                {"question_type": "वाक्य", "question_text": "'माँ' से एक वाक्य बनाओ।",
                 "correct_answer": "varies", "skill": "writing"},
            ]

        return [
            {
                "question_number": start_num + i,
                "question_type": p["question_type"],
                "question_text": p["question_text"],
                "options": None,
                "correct_answer": p["correct_answer"],
                "skill": p["skill"]
            }
            for i, p in enumerate(base)
        ]

    # ──────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────

    def _get_instructions(self, domain: str) -> str:
        if domain == "Numeracy":
            return "सभी प्रश्नों के उत्तर दें। अपना सर्वश्रेष्ठ प्रयास करें।"
        return "सभी प्रश्नों को ध्यान से पढ़ें और उत्तर दें।"
