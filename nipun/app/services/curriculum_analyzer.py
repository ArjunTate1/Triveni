"""
Hindi Curriculum Analyzer - Rule-based NLP for curriculum understanding
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from typing import Dict, List, Tuple
from app.utils.hindi_text import (
    clean_hindi_text, 
    tokenize_hindi, 
    extract_numbers,
    count_keyword_matches,
    contains_keyword
)
from app.utils.file_loader import FileLoader


class CurriculumAnalyzer:
    """
    Lightweight rule-based analyzer for Hindi curriculum text
    Uses local keyword dictionaries for detection
    """
    
    def __init__(self, base_path: str = "."):
        self.loader = FileLoader(base_path)
        self._load_dictionaries()
    
    def _load_dictionaries(self):
        """Load all keyword dictionaries"""
        self.numeracy_dict = self.loader.load_dictionary("numeracy_keywords")
        self.literacy_dict = self.loader.load_dictionary("literacy_keywords")
        self.topic_dict = self.loader.load_dictionary("topic_keywords")
        self.skill_dict = self.loader.load_dictionary("skill_keywords")
    
    def analyze(self, curriculum_text: str, grade: str, user_domain: str = None) -> Dict:
        """
        Analyze Hindi curriculum text
        
        Args:
            curriculum_text: Hindi text describing curriculum
            grade: Grade level
            user_domain: Optional domain hint from user (Literacy/Numeracy)
        
        Returns:
            Analysis result dictionary
        """
        # Clean and normalize text
        cleaned_text = clean_hindi_text(curriculum_text)
        tokens = tokenize_hindi(cleaned_text)
        
        # Detect domain
        detected_domain = self._detect_domain(cleaned_text, user_domain)
        
        # Detect topics
        detected_topics = self._detect_topics(cleaned_text, detected_domain)
        
        # Detect skills
        detected_skills = self._detect_skills(cleaned_text, detected_domain)
        
        # Extract numbers (useful for numeracy content)
        numbers_found = extract_numbers(cleaned_text)
        
        # Extract learning objective
        learning_objective = self._extract_learning_objective(cleaned_text)
        
        # Calculate confidence scores
        confidence = self._calculate_confidence(
            cleaned_text, 
            detected_domain, 
            detected_topics, 
            detected_skills
        )
        
        return {
            "grade": grade,
            "detected_domain": detected_domain,
            "detected_topics": detected_topics,
            "detected_skills": detected_skills,
            "learning_objective": learning_objective,
            "numbers_found": numbers_found,
            "confidence": confidence
        }
    
    def _detect_domain(self, text: str, user_hint: str = None) -> str:
        """
        Detect if curriculum is about Literacy or Numeracy
        Uses keyword matching against domain dictionaries
        """
        if user_hint:
            return user_hint
        
        numeracy_keywords = self.numeracy_dict.get("domain_keywords", [])
        literacy_keywords = self.literacy_dict.get("domain_keywords", [])
        
        numeracy_count = count_keyword_matches(text, numeracy_keywords)
        literacy_count = count_keyword_matches(text, literacy_keywords)
        
        if numeracy_count > literacy_count:
            return "Numeracy"
        elif literacy_count > numeracy_count:
            return "Literacy"
        else:
            # Default based on common keywords
            if any(contains_keyword(text, kw) for kw in ["संख्या", "गिनती", "जोड़"]):
                return "Numeracy"
            elif any(contains_keyword(text, kw) for kw in ["अक्षर", "शब्द", "पढ़ना"]):
                return "Literacy"
            return "Unknown"
    
    def _detect_topics(self, text: str, domain: str) -> List[str]:
        """
        Detect specific topics within the domain
        """
        detected_topics = []
        
        if domain == "Numeracy":
            topics_dict = self.numeracy_dict.get("topics", {})
        elif domain == "Literacy":
            topics_dict = self.literacy_dict.get("topics", {})
        else:
            return detected_topics
        
        # Check each topic's keywords
        for topic_name, keywords in topics_dict.items():
            if any(contains_keyword(text, kw) for kw in keywords):
                detected_topics.append(topic_name)
        
        # If no topics detected, try topic_keywords.json
        if not detected_topics:
            domain_key = "numeracy_topics" if domain == "Numeracy" else "literacy_topics"
            general_topics = self.topic_dict.get(domain_key, {})
            
            for topic_name, keywords in general_topics.items():
                if any(contains_keyword(text, kw) for kw in keywords):
                    detected_topics.append(topic_name)
        
        return detected_topics
    
    def _detect_skills(self, text: str, domain: str) -> List[str]:
        """
        Detect specific skills mentioned in curriculum
        """
        detected_skills = []
        
        # Check domain-specific skills
        if domain == "Numeracy":
            skills_dict = self.skill_dict.get("numeracy_skills", {})
        elif domain == "Literacy":
            skills_dict = self.skill_dict.get("literacy_skills", {})
        else:
            skills_dict = {}
        
        for skill_name, keywords in skills_dict.items():
            if any(contains_keyword(text, kw) for kw in keywords):
                detected_skills.append(skill_name)
        
        # Also check cognitive skills
        cognitive_skills = self.skill_dict.get("cognitive_skills", {})
        for skill_name, keywords in cognitive_skills.items():
            if any(contains_keyword(text, kw) for kw in keywords):
                detected_skills.append(skill_name)
        
        return list(set(detected_skills))  # Remove duplicates
    
    def _extract_learning_objective(self, text: str) -> str:
        """
        Extract the main learning objective from curriculum text
        For now, just return cleaned text as the objective
        Future: Could use more sophisticated rule-based extraction
        """
        return clean_hindi_text(text)
    
    def _calculate_confidence(
        self, 
        text: str, 
        domain: str, 
        topics: List[str], 
        skills: List[str]
    ) -> Dict[str, float]:
        """
        Calculate confidence scores for detection
        Based on number of keyword matches
        """
        tokens = tokenize_hindi(text)
        token_count = len(tokens)
        
        # Domain confidence
        if domain == "Numeracy":
            domain_keywords = self.numeracy_dict.get("domain_keywords", [])
        elif domain == "Literacy":
            domain_keywords = self.literacy_dict.get("domain_keywords", [])
        else:
            domain_keywords = []
        
        domain_matches = count_keyword_matches(text, domain_keywords)
        domain_confidence = min(domain_matches / max(token_count * 0.2, 1), 1.0)
        
        # Topic confidence
        topic_confidence = min(len(topics) / 3.0, 1.0) if topics else 0.0
        
        # Skill confidence
        skill_confidence = min(len(skills) / 2.0, 1.0) if skills else 0.0
        
        # Overall confidence
        overall = (domain_confidence + topic_confidence + skill_confidence) / 3.0
        
        return {
            "domain": round(domain_confidence, 2),
            "topics": round(topic_confidence, 2),
            "skills": round(skill_confidence, 2),
            "overall": round(overall, 2)
        }
