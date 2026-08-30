"""
Quiz Generator - Generate MCQ (Multiple Choice Questions) quizzes
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from typing import List, Dict, Tuple
from app.utils.file_loader import FileLoader
import random


class QuizGenerator:
    """
    Generate MCQ quizzes based on domain, topic, and grade
    Uses template-based system with Hindi support
    """

    def __init__(self, base_path: str = "."):
        self.loader = FileLoader(base_path)

    def generate(
        self,
        grade: str,
        domain: str,
        topic: str,
        topics: List[str],
        skills: List[str],
        num_questions: int = 10,
        difficulty: str = "mixed"
    ) -> Dict:
        """
        Generate an MCQ quiz.

        Returns a dict with title, grade, domain, topic, instructions,
        total_questions, and a list of question dicts.
        """
        quiz = {
            "title": f"{grade} - {domain} क्विज़ / Quiz",
            "grade": grade,
            "domain": domain,
            "topic": topic,
            "instructions": (
                "प्रत्येक प्रश्न के लिए सही विकल्प चुनें। / "
                "Choose the correct option for each question."
            ),
            "total_questions": num_questions,
            "questions": []
        }

        if domain == "Numeracy":
            quiz["questions"] = self._generate_numeracy_mcqs(
                topics, skills, num_questions, grade
            )
        else:
            quiz["questions"] = self._generate_literacy_mcqs(
                topics, skills, num_questions, grade
            )

        # Ensure total_questions matches what was actually generated
        quiz["total_questions"] = len(quiz["questions"])
        return quiz

    # ──────────────────────────────────────────────────────────────
    # NUMERACY
    # ──────────────────────────────────────────────────────────────

    def _generate_numeracy_mcqs(
        self, topics: List[str], skills: List[str], num: int, grade: str
    ) -> List[Dict]:
        """
        Build a pool of numeracy questions across all skill areas,
        shuffle them, and return exactly `num` questions (re-numbered).
        """
        pool: List[Tuple] = []  # each item: (question_text, options, correct, skill, difficulty)

        # 1. Counting questions
        pool += self._pool_counting(6)

        # 2. Addition questions
        pool += self._pool_addition(6)

        # 3. Subtraction questions
        pool += self._pool_subtraction(5)

        # 4. Comparison questions
        pool += self._pool_comparison(5)

        # 5. Number ordering / sequence
        pool += self._pool_number_sequence(4)

        # 6. Place value (for grade 2/3)
        pool += self._pool_place_value(4)

        # 7. Simple word problems
        pool += self._pool_word_problems(5)

        # 8. Shape / pattern recognition
        pool += self._pool_shapes(3)

        random.shuffle(pool)
        selected = pool[:num]

        mcqs = []
        for i, (question, options, correct, skill, diff) in enumerate(selected, start=1):
            mcqs.append({
                "question_number": i,
                "question": question,
                "options": options,
                "correct_answer": correct,
                "skill": skill,
                "difficulty": diff
            })
        return mcqs

    def _pool_counting(self, n: int) -> List[Tuple]:
        pool = []
        emojis = ["🍎", "⭐", "🌸", "🐕", "🎈", "🍌", "🐟", "🌻", "🎯", "🍊"]
        for _ in range(n):
            count = random.randint(2, 10)
            emoji = random.choice(emojis)
            correct = str(count)
            options = self._number_options(count, 4)
            pool.append((
                f"{emoji * count} इन्हें गिनो / Count them: ___",
                options, correct, "counting", "easy"
            ))
        return pool

    def _pool_addition(self, n: int) -> List[Tuple]:
        pool = []
        for _ in range(n):
            a = random.randint(1, 9)
            b = random.randint(1, 9)
            correct = str(a + b)
            options = self._number_options(a + b, 4)
            pool.append((
                f"{a} + {b} = ?",
                options, correct, "addition", "easy"
            ))
        return pool

    def _pool_subtraction(self, n: int) -> List[Tuple]:
        pool = []
        for _ in range(n):
            a = random.randint(5, 15)
            b = random.randint(1, a)
            correct = str(a - b)
            options = self._number_options(a - b, 4)
            pool.append((
                f"{a} - {b} = ?",
                options, correct, "subtraction", "medium"
            ))
        return pool

    def _pool_comparison(self, n: int) -> List[Tuple]:
        pool = []
        for _ in range(n):
            a = random.randint(1, 15)
            b = random.randint(1, 15)
            while a == b:
                b = random.randint(1, 15)
            bigger = max(a, b)
            correct = str(bigger)
            options = [str(a), str(b), "बराबर / Equal", "पता नहीं / Don't know"]
            random.shuffle(options)
            pool.append((
                f"{a} और {b} में से कौन बड़ा है? / Which is greater?",
                options, correct, "comparison", "easy"
            ))
        return pool

    def _pool_number_sequence(self, n: int) -> List[Tuple]:
        pool = []
        for _ in range(n):
            start = random.randint(1, 15)
            correct = start + 1
            options = self._number_options(correct, 4)
            pool.append((
                f"संख्या {start} के बाद कौन सी संख्या आती है? / What comes after {start}?",
                options, str(correct), "number_sequence", "easy"
            ))
        # Also add "before" questions
        for _ in range(n // 2):
            start = random.randint(2, 16)
            correct = start - 1
            options = self._number_options(correct, 4)
            pool.append((
                f"संख्या {start} से पहले कौन सी संख्या आती है? / What comes before {start}?",
                options, str(correct), "number_sequence", "easy"
            ))
        return pool

    def _pool_place_value(self, n: int) -> List[Tuple]:
        pool = []
        tens_units = [
            (10, "दस / Ten"), (20, "बीस / Twenty"), (30, "तीस / Thirty"),
            (11, "ग्यारह / Eleven"), (15, "पन्द्रह / Fifteen"),
        ]
        for _ in range(n):
            val, name = random.choice(tens_units)
            tens = val // 10
            units = val % 10
            q = f"{val} में कितने दहाई (Tens) हैं? / How many tens in {val}?"
            correct = str(tens)
            options = self._number_options(tens, 4)
            pool.append((q, options, correct, "place_value", "medium"))
        return pool

    def _pool_word_problems(self, n: int) -> List[Tuple]:
        pool = []
        problems = [
            ("राम के पास 🍎 5 सेब हैं और श्याम के पास 🍎 3 सेब हैं। कुल कितने? / Total?",
             5 + 3, "addition"),
            ("पेड़ पर 🐦 8 चिड़िया थीं। 🐦 3 उड़ गईं। कितनी बचीं? / How many left?",
             8 - 3, "subtraction"),
            ("बाजार में 🍌 4 केले और 🍊 6 संतरे हैं। कुल फल? / Total fruits?",
             4 + 6, "addition"),
            ("दुकान में 🎈 10 गुब्बारे थे। 🎈 4 बिक गए। बचे? / Left?",
             10 - 4, "subtraction"),
            ("सीता के पास 🌸 7 फूल हैं। गीता के पास 🌸 9 फूल हैं। किसके पास अधिक?",
             9, "comparison"),
        ]
        for _ in range(n):
            q_text, ans, skill = random.choice(problems)
            options = self._number_options(ans, 4)
            pool.append((q_text, options, str(ans), skill, "medium"))
        return pool

    def _pool_shapes(self, n: int) -> List[Tuple]:
        pool = []
        shapes = [
            ("🔴 यह कौन सा आकार है? / What shape is this?",
             ["वृत्त / Circle", "वर्ग / Square", "त्रिभुज / Triangle", "आयत / Rectangle"],
             "वृत्त / Circle", "shapes"),
            ("🔷 यह कौन सा आकार है? / What shape?",
             ["त्रिभुज / Triangle", "वृत्त / Circle", "वर्ग / Square", "आयत / Rectangle"],
             "वर्ग / Square", "shapes"),
            ("त्रिभुज में कितनी भुजाएं होती हैं? / How many sides does a triangle have?",
             ["2", "3", "4", "5"],
             "3", "shapes"),
            ("वर्ग में कितने कोने होते हैं? / How many corners in a square?",
             ["2", "3", "4", "6"],
             "4", "shapes"),
        ]
        for _ in range(n):
            q, opts, correct, skill = random.choice(shapes)
            pool.append((q, opts, correct, skill, "easy"))
        return pool

    def _number_options(self, correct: int, num_options: int = 4) -> List[str]:
        """Generate plausible number options around the correct answer."""
        options = {str(correct)}
        offsets = [1, -1, 2, -2, 3, -3, 4, -4]
        random.shuffle(offsets)
        for offset in offsets:
            candidate = correct + offset
            if candidate >= 0 and str(candidate) not in options:
                options.add(str(candidate))
            if len(options) >= num_options:
                break
        result = list(options)
        random.shuffle(result)
        return result[:num_options]

    # ──────────────────────────────────────────────────────────────
    # LITERACY
    # ──────────────────────────────────────────────────────────────

    def _generate_literacy_mcqs(
        self, topics: List[str], skills: List[str], num: int, grade: str
    ) -> List[Dict]:
        """
        Build a large pool of varied literacy questions, shuffle,
        and return exactly `num` (re-numbered).
        """
        pool: List[Tuple] = []

        pool += self._pool_vowel_recognition(6)
        pool += self._pool_consonant_recognition(6)
        pool += self._pool_word_recognition(6)
        pool += self._pool_word_starting_letter(6)
        pool += self._pool_opposite_words(5)
        pool += self._pool_sentence_completion(5)
        pool += self._pool_word_meaning(5)
        pool += self._pool_rhyming_words(4)

        random.shuffle(pool)
        selected = pool[:num]

        mcqs = []
        for i, (question, options, correct, skill, diff) in enumerate(selected, start=1):
            mcqs.append({
                "question_number": i,
                "question": question,
                "options": options,
                "correct_answer": correct,
                "skill": skill,
                "difficulty": diff
            })
        return mcqs

    def _pool_vowel_recognition(self, n: int) -> List[Tuple]:
        pool = []
        vowels = ["अ", "आ", "इ", "ई", "उ", "ऊ", "ए", "ऐ", "ओ", "औ"]
        consonants = ["क", "ख", "ग", "घ", "च", "ट", "त", "न", "म", "र"]
        questions = [
            ("इनमें से कौन सा स्वर है? / Which one is a vowel?",
             "vowel_recognition"),
        ]
        for _ in range(n):
            correct = random.choice(vowels)
            distractors = random.sample([c for c in consonants], 3)
            options = distractors + [correct]
            random.shuffle(options)
            pool.append((
                f"इनमें से कौन सा स्वर है? / Which is a vowel?",
                options, correct, "vowel_recognition", "easy"
            ))
        return pool

    def _pool_consonant_recognition(self, n: int) -> List[Tuple]:
        pool = []
        varga = {
            "क वर्ग": ["क", "ख", "ग", "घ", "ङ"],
            "च वर्ग": ["च", "छ", "ज", "झ", "ञ"],
            "ट वर्ग": ["ट", "ठ", "ड", "ढ", "ण"],
            "त वर्ग": ["त", "थ", "द", "ध", "न"],
            "प वर्ग": ["प", "फ", "ब", "भ", "म"],
        }
        all_consonants = [c for group in varga.values() for c in group]
        for _ in range(n):
            group_name, group = random.choice(list(varga.items()))
            correct = random.choice(group)
            distractors = random.sample([c for c in all_consonants if c not in group], 3)
            options = distractors + [correct]
            random.shuffle(options)
            pool.append((
                f"'{group_name}' का एक वर्ण कौन सा है? / Which belongs to '{group_name}'?",
                options, correct, "consonant_recognition", "medium"
            ))
        return pool

    def _pool_word_recognition(self, n: int) -> List[Tuple]:
        pool = []
        words_data = [
            ("🏠 घर (home)", "घर", ["गर", "धर", "हर", "घर"]),
            ("💧 पानी (water)", "पानी", ["पनी", "पाणी", "पनि", "पानी"]),
            ("🌳 पेड़ (tree)", "पेड़", ["पेढ़", "पेड", "पेर", "पेड़"]),
            ("📚 किताब (book)", "किताब", ["कताब", "किताव", "किताप", "किताब"]),
            ("✏️ पेंसिल (pencil)", "पेंसिल", ["पेनसिल", "पेंसल", "पैंसिल", "पेंसिल"]),
            ("🐄 गाय (cow)", "गाय", ["गाय", "गाई", "गे", "गाव"]),
            ("🐟 मछली (fish)", "मछली", ["मछिली", "मछाली", "मछलि", "मछली"]),
            ("🌞 सूरज (sun)", "सूरज", ["सुरज", "सूरज", "सूरच", "शूरज"]),
        ]
        for _ in range(n):
            label, correct, opts = random.choice(words_data)
            options = list(opts)
            random.shuffle(options)
            pool.append((
                f"सही वर्तनी चुनें / Choose correct spelling: {label}",
                options, correct, "word_recognition", "medium"
            ))
        return pool

    def _pool_word_starting_letter(self, n: int) -> List[Tuple]:
        pool = []
        letter_words = {
            "क": ["कमल", "काक", "किला", "कोयल"],
            "म": ["माँ", "मछली", "मकान", "मोर"],
            "घ": ["घर", "घड़ी", "घास", "घोड़ा"],
            "फ": ["फूल", "फल", "फिल्म", "फावड़ा"],
            "ब": ["बच्चा", "बिल्ली", "बादल", "बगीचा"],
            "र": ["रोटी", "राजा", "रात", "रस"],
            "स": ["सेब", "सूरज", "सड़क", "सबक"],
            "न": ["नदी", "नाव", "नाम", "नींबू"],
        }
        all_words = [w for ws in letter_words.values() for w in ws]
        for _ in range(n):
            letter, words = random.choice(list(letter_words.items()))
            correct = random.choice(words)
            distractors = random.sample([w for w in all_words if not w.startswith(letter)], 3)
            options = distractors + [correct]
            random.shuffle(options)
            pool.append((
                f"'{letter}' से शुरू होने वाला शब्द कौन सा है? / Which word starts with '{letter}'?",
                options, correct, "phonics", "easy"
            ))
        return pool

    def _pool_opposite_words(self, n: int) -> List[Tuple]:
        pool = []
        opposites = [
            ("दिन / Day", "रात / Night", ["सुबह / Morning", "शाम / Evening", "दोपहर / Noon", "रात / Night"]),
            ("गर्म / Hot", "ठंडा / Cold", ["नरम / Soft", "ठंडा / Cold", "गीला / Wet", "सूखा / Dry"]),
            ("बड़ा / Big", "छोटा / Small", ["लंबा / Tall", "छोटा / Small", "मोटा / Fat", "पतला / Thin"]),
            ("ऊपर / Up", "नीचे / Down", ["आगे / Forward", "नीचे / Down", "पीछे / Back", "बाईं / Left"]),
            ("काला / Black", "सफेद / White", ["लाल / Red", "हरा / Green", "सफेद / White", "नीला / Blue"]),
            ("खुश / Happy", "दुखी / Sad", ["गुस्सा / Angry", "दुखी / Sad", "डरा / Scared", "थका / Tired"]),
        ]
        for _ in range(n):
            word, correct, opts = random.choice(opposites)
            options = list(opts)
            random.shuffle(options)
            pool.append((
                f"'{word}' का विलोम शब्द क्या है? / What is the opposite?",
                options, correct, "vocabulary", "medium"
            ))
        return pool

    def _pool_sentence_completion(self, n: int) -> List[Tuple]:
        pool = []
        sentences = [
            ("आसमान का रंग ___ है। / The sky is ___ in color.",
             "नीला / Blue",
             ["लाल / Red", "हरा / Green", "नीला / Blue", "पीला / Yellow"],
             "vocabulary"),
            ("सूरज ___ से निकलता है। / The sun rises from the ___.",
             "पूर्व / East",
             ["पश्चिम / West", "उत्तर / North", "पूर्व / East", "दक्षिण / South"],
             "general_knowledge"),
            ("बिल्ली ___ करती है। / The cat ___.",
             "म्याऊं / Meows",
             ["भौंकती / Barks", "म्याऊं / Meows", "रम्भाती / Moos", "चहकती / Chirps"],
             "vocabulary"),
            ("हम भोजन ___ से खाते हैं। / We eat food with ___.",
             "हाथ / Hands",
             ["पैर / Feet", "हाथ / Hands", "आँख / Eyes", "कान / Ears"],
             "general_knowledge"),
            ("पानी का रंग ___ होता है। / Water is ___ in color.",
             "पारदर्शी / Transparent",
             ["नीला / Blue", "सफेद / White", "पारदर्शी / Transparent", "हरा / Green"],
             "general_knowledge"),
        ]
        for _ in range(n):
            q, correct, opts, skill = random.choice(sentences)
            options = list(opts)
            random.shuffle(options)
            pool.append((q, options, correct, skill, "medium"))
        return pool

    def _pool_word_meaning(self, n: int) -> List[Tuple]:
        pool = []
        meanings = [
            ("'माँ' का अर्थ क्या है? / What does 'माँ' mean?",
             "Mother",
             ["Father", "Sister", "Mother", "Brother"],
             "vocabulary"),
            ("'पानी' का अर्थ क्या है? / What does 'पानी' mean?",
             "Water",
             ["Milk", "Water", "Juice", "Air"],
             "vocabulary"),
            ("'नदी' क्या होती है? / What is a 'नदी'?",
             "River",
             ["Mountain", "River", "Forest", "Desert"],
             "vocabulary"),
            ("'आकाश' का अर्थ क्या है? / What does 'आकाश' mean?",
             "Sky",
             ["Earth", "Sky", "Ocean", "Star"],
             "vocabulary"),
            ("'पुस्तक' का अर्थ क्या है? / What does 'पुस्तक' mean?",
             "Book",
             ["Pen", "Book", "Bag", "Chair"],
             "vocabulary"),
            ("'विद्यालय' क्या होता है? / What is 'विद्यालय'?",
             "School",
             ["Home", "School", "Hospital", "Market"],
             "vocabulary"),
        ]
        for _ in range(n):
            q, correct, opts, skill = random.choice(meanings)
            options = list(opts)
            random.shuffle(options)
            pool.append((q, options, correct, skill, "medium"))
        return pool

    def _pool_rhyming_words(self, n: int) -> List[Tuple]:
        pool = []
        rhymes = [
            ("'घर' के साथ कौन सा शब्द तुकबंदी करता है? / Rhymes with 'घर'?",
             "डर",
             ["नल", "डर", "बस", "माँ"]),
            ("'नल' के साथ कौन सा तुकबंदी? / Rhymes with 'नल'?",
             "जल",
             ["घर", "जल", "रोटी", "माँ"]),
            ("'राज' के साथ कौन सा तुकबंदी? / Rhymes with 'राज'?",
             "काज",
             ["घर", "पानी", "काज", "नदी"]),
            ("'फूल' के साथ कौन सा तुकबंदी? / Rhymes with 'फूल'?",
             "भूल",
             ["पेड़", "भूल", "सूरज", "पानी"]),
        ]
        for _ in range(n):
            q, correct, opts = random.choice(rhymes)
            options = list(opts)
            random.shuffle(options)
            pool.append((q, options, correct, "rhyming", "easy"))
        return pool
