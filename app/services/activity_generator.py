"""
Activity Generator - Generate learning activities from templates
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from typing import List, Dict
from app.utils.file_loader import FileLoader
import random


class ActivityGenerator:
    """
    Generate learning activities based on domain, topic, and skills
    Uses local template-based system
    """
    
    def __init__(self, base_path: str = "."):
        self.loader = FileLoader(base_path)
    
    def generate(
        self,
        domain: str,
        topics: List[str],
        skills: List[str],
        grade: str
    ) -> List[Dict]:
        """
        Generate activities based on curriculum analysis
        
        Args:
            domain: Literacy or Numeracy
            topics: Detected topics
            skills: Detected skills
            grade: Grade level
        
        Returns:
            List of generated activities
        """
        # Load activity templates
        if domain == "Numeracy":
            template_file = "numeracy_activities"
        elif domain == "Literacy":
            template_file = "literacy_activities"
        else:
            return []
        
        try:
            templates = self.loader.load_templates(template_file)
        except FileNotFoundError:
            return []
        
        activities = []
        
        # Try to find activities for each detected topic
        for topic in topics:
            if topic in templates:
                topic_activities = templates[topic]
                # Add all activities for this topic (max 2 per topic)
                for activity in topic_activities[:2]:
                    activities.append({
                        "title": activity.get("title", ""),
                        "instructions": activity.get("instructions", ""),
                        "materials": activity.get("materials", []),
                        "steps": activity.get("steps", []),
                        "duration": activity.get("duration", "20 मिनट")
                    })
        
        # If no activities found from topics, try to match by skills
        if not activities:
            activities = self._find_by_skills(templates, skills)
        
        # If still no activities, return a default activity
        if not activities:
            activities = [self._default_activity(domain)]
        
        return activities[:3]  # Return max 3 activities
    
    def _find_by_skills(self, templates: Dict, skills: List[str]) -> List[Dict]:
        """Find activities that match the detected skills"""
        activities = []
        
        # Map skills to template keys (simple keyword matching)
        for skill in skills:
            for template_key, template_activities in templates.items():
                if skill.lower() in template_key.lower():
                    for activity in template_activities[:1]:
                        activities.append({
                            "title": activity.get("title", ""),
                            "instructions": activity.get("instructions", ""),
                            "materials": activity.get("materials", []),
                            "steps": activity.get("steps", []),
                            "duration": activity.get("duration", "20 मिनट")
                        })
                    break
        
        return activities
    
    def _default_activity(self, domain: str) -> Dict:
        """Return a generic default activity"""
        if domain == "Numeracy":
            return {
                "title": "संख्याओं के साथ अभ्यास",
                "instructions": "बच्चों को संख्याओं के साथ व्यावहारिक गतिविधियां कराएं।",
                "materials": ["वस्तुएं", "संख्या कार्ड", "चॉक/पेंसिल"],
                "steps": [
                    "संख्याओं को पहचानने का अभ्यास करें",
                    "वस्तुओं को गिनें",
                    "संख्याओं को लिखने का अभ्यास करें",
                    "सरल गणित की समस्याएं हल करें"
                ],
                "duration": "20-25 मिनट"
            }
        else:  # Literacy
            return {
                "title": "पढ़ना और लिखना अभ्यास",
                "instructions": "बच्चों को अक्षरों और शब्दों के साथ अभ्यास कराएं।",
                "materials": ["अक्षर कार्ड", "किताबें", "स्लेट/कागज"],
                "steps": [
                    "अक्षरों को पहचानने का अभ्यास करें",
                    "शब्दों को पढ़ें",
                    "अक्षर और शब्द लिखें",
                    "छोटे वाक्य बनाएं"
                ],
                "duration": "20-25 मिनट"
            }
