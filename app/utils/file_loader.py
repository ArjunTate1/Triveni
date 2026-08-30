"""
Utility functions for loading local JSON data files
"""
import json
import os
from typing import Dict, List, Any
from pathlib import Path


class FileLoader:
    """Lazy loader for JSON data files"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self._cache = {}
    
    def load_json(self, file_path: str, use_cache: bool = True) -> Any:
        """
        Load JSON file with optional caching
        
        Args:
            file_path: Relative path to JSON file
            use_cache: Whether to cache the loaded data
        
        Returns:
            Parsed JSON data
        """
        full_path = self.base_path / file_path
        
        # Check cache first
        if use_cache and str(full_path) in self._cache:
            return self._cache[str(full_path)]
        
        # Load from file
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Cache if requested
        if use_cache:
            self._cache[str(full_path)] = data
        
        return data
    
    def load_nipun_data(self, grade: str) -> List[Dict[str, Any]]:
        """
        Load NIPUN knowledge base for specific grade
        
        Args:
            grade: Grade level (Balvatika, Grade 1, Grade 2, Grade 3)
        
        Returns:
            List of NIPUN learning outcome records
        """
        grade_mapping = {
            "Balvatika": "balvatika.json",
            "Grade 1": "grade1.json",
            "Grade 2": "grade2.json",
            "Grade 3": "grade3.json"
        }
        
        filename = grade_mapping.get(grade)
        if not filename:
            raise ValueError(f"Unknown grade: {grade}")
        
        return self.load_json(f"data/nipun/{filename}")
    
    def load_dictionary(self, dict_name: str) -> Dict[str, Any]:
        """
        Load keyword dictionary
        
        Args:
            dict_name: Dictionary name (e.g., 'literacy_keywords', 'numeracy_keywords')
        
        Returns:
            Dictionary data
        """
        return self.load_json(f"data/dictionaries/{dict_name}.json")
    
    def load_templates(self, template_name: str) -> Dict[str, Any]:
        """
        Load template file
        
        Args:
            template_name: Template name (e.g., 'literacy_activities', 'worksheet_templates')
        
        Returns:
            Template data
        """
        return self.load_json(f"data/templates/{template_name}.json")
    
    def clear_cache(self):
        """Clear the cache to free memory"""
        self._cache.clear()
    
    def get_cache_size(self) -> int:
        """Get number of cached items"""
        return len(self._cache)
