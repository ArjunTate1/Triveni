"""
Study Material Generator - Generate lesson plans and study guides for teachers
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from typing import List, Dict
from app.utils.file_loader import FileLoader


class StudyMaterialGenerator:
    """
    Generate study materials including:
    - Lesson plans for teachers
    - Study guides for students
    - Teaching tips and strategies
    """
    
    def __init__(self, base_path: str = "."):
        self.loader = FileLoader(base_path)
    
    def generate_lesson_plan(
        self,
        grade: str,
        domain: str,
        topics: List[str],
        skills: List[str],
        learning_objective: str,
        nipun_reference: str
    ) -> Dict:
        """
        Generate a comprehensive lesson plan for teachers
        
        Returns:
            Lesson plan dictionary with all sections
        """
        # Load activity templates for lesson activities
        try:
            if domain == "Numeracy":
                activities = self.loader.load_templates("numeracy_activities")
            else:
                activities = self.loader.load_templates("literacy_activities")
        except FileNotFoundError:
            activities = {}
        
        lesson_plan = {
            "title": f"{grade} - {domain} पाठ योजना (Lesson Plan)",
            "grade": grade,
            "domain": domain,
            "topic": ", ".join(topics[:2]),
            "learning_objective": learning_objective,
            "nipun_reference": nipun_reference,
            "duration": "40-45 मिनट",
            "materials_needed": self._get_materials(domain, topics, activities),
            "lesson_structure": self._create_lesson_structure(domain, topics, activities),
            "assessment_strategies": self._get_assessment_strategies(domain),
            "differentiation_tips": self._get_differentiation_tips(domain),
            "homework_suggestion": self._get_homework_suggestion(domain, topics)
        }
        
        return lesson_plan
    
    def generate_study_guide(
        self,
        grade: str,
        domain: str,
        topics: List[str],
        skills: List[str],
        learning_objective: str
    ) -> Dict:
        """
        Generate a study guide for students
        
        Returns:
            Study guide dictionary
        """
        study_guide = {
            "title": f"{grade} - {domain} अध्ययन मार्गदर्शिका (Study Guide)",
            "grade": grade,
            "domain": domain,
            "topic": ", ".join(topics[:2]),
            "learning_objective": learning_objective,
            "key_concepts": self._get_key_concepts(domain, topics),
            "examples": self._get_examples(domain, topics),
            "practice_tips": self._get_practice_tips(domain),
            "common_mistakes": self._get_common_mistakes(domain, topics),
            "quick_revision": self._get_quick_revision(domain, topics)
        }
        
        return study_guide
    
    def _get_materials(self, domain: str, topics: List[str], activities: Dict) -> List[str]:
        """Get list of materials needed for the lesson"""
        materials = set()
        
        # Get materials from activity templates
        for topic in topics:
            if topic in activities:
                topic_activities = activities[topic]
                for activity in topic_activities[:2]:
                    materials.update(activity.get("materials", []))
        
        # Add common materials
        if domain == "Numeracy":
            materials.update([
                "संख्या कार्ड (1-10)",
                "गिनने के लिए वस्तुएं (पत्थर, बीज, बटन)",
                "बोर्ड और चॉक/मार्कर",
                "वर्कशीट कॉपियां"
            ])
        else:  # Literacy
            materials.update([
                "अक्षर कार्ड",
                "शब्द कार्ड",
                "चित्र कार्ड",
                "कहानी की किताबें",
                "बोर्ड और चॉक/मार्कर",
                "लेखन सामग्री (कॉपी, पेंसिल)"
            ])
        
        return list(materials)
    
    def _create_lesson_structure(self, domain: str, topics: List[str], activities: Dict) -> Dict:
        """Create the main lesson structure with timing"""
        structure = {
            "introduction": {
                "duration": "5-7 मिनट",
                "activities": [
                    "🎯 आज के पाठ के उद्देश्य बताएं",
                    "🤔 पूर्व ज्ञान को याद दिलाएं (पिछले पाठ से जोड़ें)",
                    "❓ प्रेरक प्रश्न पूछें",
                    "🎵 संबंधित गीत या कविता से शुरुआत करें"
                ],
                "example": self._get_intro_example(domain, topics)
            },
            "main_teaching": {
                "duration": "20-25 मिनट",
                "activities": self._get_main_teaching_activities(domain, topics, activities),
                "teaching_points": self._get_teaching_points(domain, topics)
            },
            "guided_practice": {
                "duration": "10-12 मिनट",
                "activities": [
                    "👥 समूह में अभ्यास करें",
                    "🤝 जोड़ी बनाकर काम करें",
                    "✅ शिक्षक की मदद से सवाल हल करें",
                    "🎯 व्यावहारिक अभ्यास दें"
                ]
            },
            "independent_practice": {
                "duration": "5-7 मिनट",
                "activities": [
                    "📝 व्यक्तिगत रूप से वर्कशीट हल करें",
                    "✍️ स्वतंत्र लेखन/हल करना",
                    "🎨 रचनात्मक गतिविधि"
                ]
            },
            "closure": {
                "duration": "3-5 मिनट",
                "activities": [
                    "📋 आज क्या सीखा - सारांश",
                    "❓ त्वरित समीक्षा प्रश्न",
                    "⭐ अच्छे काम की सराहना करें",
                    "🏠 होमवर्क दें और समझाएं"
                ]
            }
        }
        
        return structure
    
    def _get_intro_example(self, domain: str, topics: List[str]) -> str:
        """Get introduction example"""
        if domain == "Numeracy":
            if "counting" in topics:
                return "प्रश्न: 'बच्चों, आज सुबह कितने बच्चे स्कूल आए हैं? चलो मिलकर गिनते हैं! 🙋' इस तरह गिनती की शुरुआत करें।"
            elif "addition" in topics:
                return "प्रश्न: 'अगर तुम्हारे पास 🍎 2 सेब हैं और मैं तुम्हें 🍎 3 और दूं, तो कितने हो जाएंगे?' - वास्तविक उदाहरण से शुरू करें।"
            else:
                return "दैनिक जीवन से जुड़े उदाहरण से शुरुआत करें। बच्चों को सोचने के लिए प्रेरित करें।"
        else:  # Literacy
            if "letter_recognition" in topics:
                return "प्रश्न: 'क्या तुम अपने नाम का पहला अक्षर जानते हो? आओ आज नए अक्षर सीखें! 📖' - व्यक्तिगत संदर्भ से जोड़ें।"
            else:
                return "कहानी या गीत से शुरुआत करें। बच्चों को सुनने और भाग लेने के लिए प्रेरित करें।"
    
    def _get_main_teaching_activities(self, domain: str, topics: List[str], activities: Dict) -> List[str]:
        """Get main teaching activities"""
        teaching_activities = []
        
        # Get activities from templates
        for topic in topics[:2]:
            if topic in activities:
                topic_activities = activities[topic]
                for activity in topic_activities[:1]:  # Take first activity
                    teaching_activities.append(f"🎯 {activity.get('title', '')} - {activity.get('instructions', '')}")
        
        # Add general activities
        if domain == "Numeracy":
            teaching_activities.extend([
                "📊 बोर्ड पर स्पष्ट उदाहरण दिखाएं",
                "🧮 वास्तविक वस्तुओं से समझाएं",
                "🎲 गणित के खेल खेलें",
                "👐 हाथों से गतिविधि करें"
            ])
        else:
            teaching_activities.extend([
                "📚 ज़ोर से पढ़ें और बच्चों से दोहराएं",
                "✍️ बोर्ड पर लिखकर दिखाएं",
                "🎭 अभिनय या कठपुतली से समझाएं",
                "🎨 चित्रों का उपयोग करें"
            ])
        
        return teaching_activities[:6]  # Return top 6
    
    def _get_teaching_points(self, domain: str, topics: List[str]) -> List[str]:
        """Get key teaching points"""
        if domain == "Numeracy":
            if "counting" in topics:
                return [
                    "✅ प्रत्येक वस्तु को केवल एक बार गिनें",
                    "✅ गिनते समय वस्तु को छुएं या इंगित करें",
                    "✅ अंतिम संख्या ही कुल संख्या होती है",
                    "✅ संख्या का क्रम महत्वपूर्ण है"
                ]
            elif "addition" in topics:
                return [
                    "✅ 'और' या '+' का अर्थ मिलाना है",
                    "✅ जोड़ने पर संख्या बढ़ती है",
                    "✅ दोनों समूहों को मिलाकर गिनें",
                    "✅ संख्या रेखा का उपयोग करें"
                ]
            elif "subtraction" in topics:
                return [
                    "✅ घटाने का अर्थ हटाना है",
                    "✅ घटाने पर संख्या कम होती है",
                    "✅ बड़ी संख्या में से छोटी घटाएं",
                    "✅ 'बाकी' या 'शेष' पर ध्यान दें"
                ]
            else:
                return [
                    "✅ स्पष्ट और धीरे-धीरे समझाएं",
                    "✅ उदाहरणों का उपयोग करें",
                    "✅ बच्चों को हाथों से करने दें",
                    "✅ गलतियों को सुधारने का मौका दें"
                ]
        else:  # Literacy
            if "letter_recognition" in topics or "vowels" in topics or "consonants" in topics:
                return [
                    "✅ अक्षर के आकार पर ध्यान दें",
                    "✅ सही उच्चारण सिखाएं",
                    "✅ अक्षर से शुरू होने वाले शब्द बताएं",
                    "✅ बार-बार अभ्यास कराएं"
                ]
            elif "word_reading" in topics:
                return [
                    "✅ शब्द को ध्वनियों में तोड़ें",
                    "✅ प्रत्येक ध्वनि स्पष्ट बोलें",
                    "✅ फिर पूरा शब्द मिलाकर पढ़ें",
                    "✅ चित्र से शब्द का संबंध बताएं"
                ]
            else:
                return [
                    "✅ स्पष्ट और धीरे बोलें",
                    "✅ बच्चों से दोहराने को कहें",
                    "✅ सरल से कठिन की ओर बढ़ें",
                    "✅ प्रोत्साहन देते रहें"
                ]
    
    def _get_assessment_strategies(self, domain: str) -> Dict:
        """Get assessment strategies"""
        return {
            "formative_assessment": [
                "👀 कक्षा में बच्चों के काम को देखें",
                "❓ मौखिक प्रश्न पूछें",
                "✋ हाथ उठाकर जवाब दें",
                "🎯 त्वरित क्विज़ दें",
                "📝 व्हाइटबोर्ड पर लिखने को कहें"
            ],
            "summative_assessment": [
                "📋 वर्कशीट से मूल्यांकन करें",
                "📝 लिखित परीक्षा लें",
                "🗣️ मौखिक परीक्षा लें",
                "🎨 परियोजना या प्रस्तुति से आंकलन करें"
            ],
            "observation_points": [
                "क्या बच्चा सही तरीके से कर रहा है?",
                "क्या बच्चा आत्मविश्वास से जवाब दे रहा है?",
                "क्या कोई कठिनाई हो रही है?",
                "क्या अतिरिक्त सहायता चाहिए?"
            ]
        }
    
    def _get_differentiation_tips(self, domain: str) -> Dict:
        """Get differentiation strategies for different learners"""
        return {
            "for_slow_learners": {
                "title": "धीमी गति से सीखने वाले बच्चों के लिए 🐢",
                "tips": [
                    "➕ अतिरिक्त समय और अभ्यास दें",
                    "🎯 एक बार में एक ही कौशल सिखाएं",
                    "🔄 बार-बार दोहराएं और समीक्षा करें",
                    "👫 साथी की मदद दें (peer support)",
                    "🎁 छोटी सफलता पर भी प्रोत्साहन दें",
                    "📦 वस्तुओं का अधिक उपयोग करें"
                ]
            },
            "for_fast_learners": {
                "title": "तेज़ी से सीखने वाले बच्चों के लिए 🚀",
                "tips": [
                    "🎯 चुनौतीपूर्ण प्रश्न दें",
                    "📚 अतिरिक्त पढ़ने की सामग्री दें",
                    "👨‍🏫 दूसरों की मदद करने दें (peer teaching)",
                    "🧩 समस्या-समाधान वाली गतिविधियां दें",
                    "🎨 रचनात्मक परियोजनाएं दें",
                    "📈 उच्च स्तर के कार्य दें"
                ]
            },
            "for_visual_learners": {
                "title": "दृश्य शिक्षार्थियों के लिए 👁️",
                "tips": [
                    "🖼️ चित्र, चार्ट, और पोस्टर दिखाएं",
                    "🎨 रंगीन सामग्री का उपयोग करें",
                    "📊 ग्राफ़ और diagram बनाएं",
                    "🎬 वीडियो या स्लाइड दिखाएं (यदि उपलब्ध हो)",
                    "✍️ बोर्ड पर लिखकर दिखाएं"
                ]
            },
            "for_kinesthetic_learners": {
                "title": "क्रियाशील शिक्षार्थियों के लिए 🤸",
                "tips": [
                    "🏃 हाथों-से-करने वाली गतिविधियां दें",
                    "🎲 खेल और चलने-फिरने वाले कार्य दें",
                    "🧱 ब्लॉक, वस्तुओं से सीखने दें",
                    "🎭 अभिनय और नाटक करने दें",
                    "✋ शारीरिक हरकतों से सीखने दें"
                ]
            }
        }
    
    def _get_homework_suggestion(self, domain: str, topics: List[str]) -> str:
        """Get homework suggestion"""
        if domain == "Numeracy":
            return "🏠 होमवर्क: वर्कशीट में 5-8 अभ्यास प्रश्न दें। घर में वस्तुओं को गिनने या माप-तौल करने का कार्य दें।"
        else:
            return "🏠 होमवर्क: अक्षर/शब्द लेखन अभ्यास दें। घर में माता-पिता के साथ पढ़ने का कार्य दें। छोटी कहानी या 3-4 वाक्य लिखने को कहें।"
    
    def _get_key_concepts(self, domain: str, topics: List[str]) -> List[Dict]:
        """Get key concepts for study guide"""
        concepts = []
        
        if domain == "Numeracy":
            if "counting" in topics:
                concepts.append({
                    "concept": "गिनती (Counting)",
                    "explanation": "वस्तुओं को एक-एक करके गिनना और कुल संख्या बताना।",
                    "emoji": "🔢"
                })
            if "addition" in topics:
                concepts.append({
                    "concept": "जोड़ (Addition)",
                    "explanation": "दो या अधिक संख्याओं को मिलाना। चिन्ह: + (जमा)",
                    "emoji": "➕"
                })
            if "subtraction" in topics:
                concepts.append({
                    "concept": "घटाव (Subtraction)",
                    "explanation": "बड़ी संख्या में से छोटी संख्या घटाना। चिन्ह: - (घटा)",
                    "emoji": "➖"
                })
            if "comparison" in topics:
                concepts.append({
                    "concept": "तुलना (Comparison)",
                    "explanation": "दो संख्याओं में कौन बड़ा, छोटा या बराबर है। चिन्ह: >, <, =",
                    "emoji": "⚖️"
                })
        else:  # Literacy
            if "letter_recognition" in topics or "vowels" in topics:
                concepts.append({
                    "concept": "स्वर (Vowels)",
                    "explanation": "हिंदी में 11 स्वर हैं: अ, आ, इ, ई, उ, ऊ, ए, ऐ, ओ, औ (और अं, अः)",
                    "emoji": "🔤"
                })
            if "consonants" in topics:
                concepts.append({
                    "concept": "व्यंजन (Consonants)",
                    "explanation": "स्वरों के अलावा सभी अक्षर व्यंजन हैं। जैसे: क, ख, ग...",
                    "emoji": "🔡"
                })
            if "word_reading" in topics:
                concepts.append({
                    "concept": "शब्द पढ़ना (Word Reading)",
                    "explanation": "अक्षरों को मिलाकर शब्द बनाना और पढ़ना।",
                    "emoji": "📖"
                })
        
        return concepts
    
    def _get_examples(self, domain: str, topics: List[str]) -> List[str]:
        """Get examples for study guide"""
        examples = []
        
        if domain == "Numeracy":
            if "counting" in topics:
                examples.append("🍎 सेब गिनो: 🍎🍎🍎🍎🍎 = 5 (पाँच)")
            if "addition" in topics:
                examples.extend([
                    "2 + 3 = 5 (दो और तीन मिलाकर पाँच)",
                    "🍬 3 टॉफी + 🍬 2 टॉफी = 🍬 5 टॉफी"
                ])
            if "subtraction" in topics:
                examples.extend([
                    "5 - 2 = 3 (पाँच में से दो घटाने पर तीन)",
                    "🎈 7 गुब्बारे - 🎈 3 फूटे = 🎈 4 बचे"
                ])
        else:  # Literacy
            if "letter_recognition" in topics:
                examples.extend([
                    "'क' से कमल 🪷, कुत्ता 🐕",
                    "'म' से माँ, मछली 🐟"
                ])
            if "word_reading" in topics:
                examples.extend([
                    "घ + र = घर 🏠",
                    "ब + स = बस 🚌"
                ])
        
        return examples
    
    def _get_practice_tips(self, domain: str) -> List[str]:
        """Get practice tips for students"""
        if domain == "Numeracy":
            return [
                "🏠 घर में रोज़ चीज़ें गिनने का अभ्यास करो",
                "🎲 परिवार के साथ गणित के खेल खेलो",
                "✍️ रोज़ कुछ गणित के सवाल हल करो",
                "📚 संख्याओं को ज़ोर से बोलकर पढ़ो",
                "🧮 वस्तुओं से जोड़-घटाव का अभ्यास करो",
                "👪 माता-पिता से मदद मांगो जब ज़रूरत हो"
            ]
        else:
            return [
                "📖 रोज़ कम से कम 10-15 मिनट पढ़ो",
                "✍️ रोज़ अक्षर और शब्द लिखने का अभ्यास करो",
                "🗣️ जो पढ़ो उसे ज़ोर से बोलो",
                "👂 कहानियां सुनो और समझो",
                "🎵 अक्षरों के गीत गाओ",
                "👪 घर में हिंदी में बात करो"
            ]
    
    def _get_common_mistakes(self, domain: str, topics: List[str]) -> List[Dict]:
        """Get common mistakes and how to avoid them"""
        mistakes = []
        
        if domain == "Numeracy":
            if "counting" in topics:
                mistakes.append({
                    "mistake": "❌ गिनते समय कोई संख्या छूट जाना या दो बार गिन लेना",
                    "solution": "✅ प्रत्येक वस्तु को छूते हुए या अलग करते हुए गिनो"
                })
            if "addition" in topics:
                mistakes.append({
                    "mistake": "❌ जोड़ने के बजाय घटा देना",
                    "solution": "✅ '+' चिन्ह देखो और समझो कि मिलाना है, घटाना नहीं"
                })
        else:  # Literacy
            mistakes.append({
                "mistake": "❌ मिलते-जुलते अक्षरों में गड़बड़ करना (जैसे: ध और घ)",
                "solution": "✅ अक्षर के आकार पर ध्यान दो और बार-बार अभ्यास करो"
            })
            mistakes.append({
                "mistake": "❌ मात्राएं गलत लगाना",
                "solution": "✅ मात्रा की सही जगह याद करो और अभ्यास करो"
            })
        
        return mistakes
    
    def _get_quick_revision(self, domain: str, topics: List[str]) -> List[str]:
        """Get quick revision points"""
        revision = []
        
        if domain == "Numeracy":
            revision.extend([
                "📌 1 से 10 तक की गिनती याद करो",
                "📌 संख्याओं को पहचानना सीखो",
                "📌 सरल जोड़ और घटाव के सवाल हल करो",
                "📌 बड़ा-छोटा-बराबर समझो"
            ])
        else:
            revision.extend([
                "📌 सभी स्वर और व्यंजन याद करो",
                "📌 दो अक्षर के शब्द पढ़ो और लिखो",
                "📌 सरल वाक्य बनाओ",
                "📌 रोज़ कुछ नया पढ़ो"
            ])
        
        return revision
