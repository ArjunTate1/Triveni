"""
NIPUN Mapper - Maps curriculum to NIPUN learning outcomes
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from typing import Dict, List, Optional
from app.utils.file_loader import FileLoader
from app.utils.hindi_text import contains_keyword, count_keyword_matches


class NIPUNMapper:
    """
    Maps analyzed curriculum to NIPUN/FLN learning outcomes
    Uses local knowledge base and rule-based matching
    """
    
    def __init__(self, base_path: str = "."):
        self.loader = FileLoader(base_path)
    
    def find_best_match(
        self,
        grade: str,
        domain: str,
        topics: List[str],
        skills: List[str],
        learning_objective: str
    ) -> Dict:
        """
        Find best matching NIPUN learning outcome
        
        Args:
            grade: Grade level
            domain: Literacy or Numeracy
            topics: Detected topics
            skills: Detected skills
            learning_objective: Extracted learning objective
        
        Returns:
            Best matching NIPUN outcome with confidence score
        """
        # Load NIPUN data for the grade
        try:
            nipun_records = self.loader.load_nipun_data(grade)
        except (FileNotFoundError, ValueError) as e:
            return self._no_match_result(str(e))
        
        # Score each record
        scored_records = []
        for record in nipun_records:
            score = self._calculate_match_score(
                record, domain, topics, skills, learning_objective
            )
            scored_records.append((record, score))
        
        # Sort by score (highest first)
        scored_records.sort(key=lambda x: x[1], reverse=True)
        
        if not scored_records or scored_records[0][1] == 0:
            return self._no_match_result("No matching NIPUN outcome found")
        
        # Return best match
        best_record, best_score = scored_records[0]
        
        return {
            "matched_outcome_id": best_record.get("id", "UNKNOWN"),
            "competency": best_record.get("competency", ""),
            "learning_outcome": best_record.get("learning_outcome", ""),
            "matched_skills": best_record.get("skills", []),
            "confidence": round(min(best_score / 100.0, 1.0), 2)
        }
    
    def _calculate_match_score(
        self,
        record: Dict,
        domain: str,
        topics: List[str],
        skills: List[str],
        learning_objective: str
    ) -> float:
        """
        Calculate match score for a NIPUN record
        
        Scoring system:
        - Grade match: already filtered
        - Domain match: 30 points
        - Topic match: 25 points (per topic, max 50)
        - Skill match: 20 points (per skill, max 40)
        - Keyword overlap: up to 30 points
        
        Total: up to 150 points (normalized to 0-1)
        """
        score = 0.0
        
        # Domain match (30 points)
        if record.get("domain", "").lower() == domain.lower():
            score += 30
        
        # Topic match (up to 50 points)
        record_topic = record.get("topic", "").lower()
        for detected_topic in topics:
            # Check if detected topic appears in record topic
            if detected_topic.lower() in record_topic or record_topic in detected_topic.lower():
                score += 25
                break  # Only count once
        
        # Skill match (up to 40 points)
        record_skills = [s.lower() for s in record.get("skills", [])]
        detected_skills = [s.lower() for s in skills]
        
        skill_matches = len(set(record_skills) & set(detected_skills))
        score += min(skill_matches * 20, 40)
        
        # Keyword overlap in learning outcome (up to 30 points)
        record_outcome = record.get("learning_outcome", "").lower()
        objective_lower = learning_objective.lower()
        
        # Count common significant words
        from app.utils.hindi_text import tokenize_hindi
        record_tokens = set(tokenize_hindi(record_outcome))
        objective_tokens = set(tokenize_hindi(objective_lower))
        
        common_tokens = record_tokens & objective_tokens
        # Score based on overlap percentage
        if objective_tokens:
            overlap_ratio = len(common_tokens) / len(objective_tokens)
            score += overlap_ratio * 30
        
        return score
    
    def _no_match_result(self, reason: str) -> Dict:
        """Return a no-match result"""
        return {
            "matched_outcome_id": "NO_MATCH",
            "competency": "कोई मिलान नहीं मिला",
            "learning_outcome": f"NIPUN डेटाबेस में कोई मेल खाता परिणाम नहीं मिला। कारण: {reason}",
            "matched_skills": [],
            "confidence": 0.0
        }
    
    def get_all_outcomes_for_grade(self, grade: str) -> List[Dict]:
        """
        Get all NIPUN outcomes for a grade
        
        Args:
            grade: Grade level
        
        Returns:
            List of all NIPUN records for the grade
        """
        try:
            return self.loader.load_nipun_data(grade)
        except (FileNotFoundError, ValueError):
            return []
    
    def get_outcomes_by_domain(self, grade: str, domain: str) -> List[Dict]:
        """
        Get NIPUN outcomes filtered by domain
        
        Args:
            grade: Grade level
            domain: Literacy or Numeracy
        
        Returns:
            Filtered list of NIPUN records
        """
        all_records = self.get_all_outcomes_for_grade(grade)
        return [r for r in all_records if r.get("domain", "").lower() == domain.lower()]
