"""
Flashcard Generator - Generate flashcards using local templates
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from typing import List, Dict
from app.utils.file_loader import FileLoader


class FlashcardGenerator:
    """Generate flashcards based on curriculum content"""
    
    def __init__(self, base_path: str = "."):
        self.loader = FileLoader(base_path)
    
    def generate(
        self,
        grade: str,
        domain: str,
        topic: str,
        topics: List[str],
        skills: List[str]
    ) -> Dict:
        """Generate a set of flashcards"""
        
        # Load flashcard templates
        try:
            templates = self.loader.load_templates("flashcard_templates")
        except FileNotFoundError:
            templates = {}
        
        flashcards = []
        
        # Generate flashcards based on topics and domain
        if domain == "Numeracy":
            flashcards = self._generate_numeracy_flashcards(topics, templates)
        elif domain == "Literacy":
            flashcards = self._generate_literacy_flashcards(topics, templates)
        
        # If no flashcards generated, use defaults
        if not flashcards:
            flashcards = self._default_flashcards(domain)
        
        return {
            "title": f"{domain} फ्लैशकार्ड - {topic or 'सामान्य'}",
            "grade": grade,
            "domain": domain,
            "topic": topic or ", ".join(topics),
            "flashcards": flashcards[:10]  # Max 10 flashcards
        }
    
    def _generate_numeracy_flashcards(
        self, topics: List[str], templates: Dict
    ) -> List[Dict]:
        """Generate numeracy flashcards"""
        flashcards = []
        
        # Check for numbers/counting topics
        if any(t in ["numbers", "counting", "number_recognition"] for t in topics):
            if "numbers_1_to_10" in templates:
                for card_data in templates["numbers_1_to_10"][:10]:
                    flashcards.append({
                        "front_text": card_data.get("front", ""),
                        "front_image": card_data.get("image"),
                        "back_text": card_data.get("back", ""),
                        "back_image": None
                    })
        
        # Check for shapes
        if "shapes" in topics:
            if "shapes" in templates:
                for card_data in templates["shapes"]:
                    flashcards.append({
                        "front_text": card_data.get("front", ""),
                        "front_image": card_data.get("image"),
                        "back_text": card_data.get("back", ""),
                        "back_image": None
                    })
        
        return flashcards
    
    def _generate_literacy_flashcards(
        self, topics: List[str], templates: Dict
    ) -> List[Dict]:
        """Generate literacy flashcards"""
        flashcards = []
        
        # Check for letters
        if any(t in ["letters", "letter_recognition"] for t in topics):
            if "vowels" in templates:
                for card_data in templates["vowels"][:10]:
                    flashcards.append({
                        "front_text": card_data.get("front", ""),
                        "front_image": None,
                        "back_text": f"{card_data.get('back', '')} ({card_data.get('example', '')})",
                        "back_image": None
                    })
            
            # Also add some consonants
            if "consonants_ka_varg" in templates:
                for card_data in templates["consonants_ka_varg"][:5]:
                    flashcards.append({
                        "front_text": card_data.get("front", ""),
                        "front_image": None,
                        "back_text": f"{card_data.get('back', '')} ({card_data.get('example', '')})",
                        "back_image": None
                    })
        
        # Check for words
        if any(t in ["words", "word_reading", "word_recognition"] for t in topics):
            if "simple_words" in templates:
                for card_data in templates["simple_words"]:
                    flashcards.append({
                        "front_text": card_data.get("front", ""),
                        "front_image": card_data.get("image"),
                        "back_text": card_data.get("back", ""),
                        "back_image": None
                    })
        
        return flashcards
    
    def _default_flashcards(self, domain: str) -> List[Dict]:
        """Generate default flashcards"""
        if domain == "Numeracy":
            return [
                {"front_text": "1", "front_image": None, "back_text": "एक", "back_image": None},
                {"front_text": "2", "front_image": None, "back_text": "दो", "back_image": None},
                {"front_text": "3", "front_image": None, "back_text": "तीन", "back_image": None},
                {"front_text": "4", "front_image": None, "back_text": "चार", "back_image": None},
                {"front_text": "5", "front_image": None, "back_text": "पांच", "back_image": None}
            ]
        else:
            return [
                {"front_text": "अ", "front_image": None, "back_text": "a (अनार)", "back_image": None},
                {"front_text": "आ", "front_image": None, "back_text": "aa (आम)", "back_image": None},
                {"front_text": "इ", "front_image": None, "back_text": "i (इमली)", "back_image": None},
                {"front_text": "ई", "front_image": None, "back_text": "ee (ईख)", "back_image": None},
                {"front_text": "उ", "front_image": None, "back_text": "u (उल्लू)", "back_image": None}
            ]
