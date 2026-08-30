"""
Test suite for Curriculum Analyzer
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.curriculum_analyzer import CurriculumAnalyzer


def test_numeracy_detection():
    """Test numeracy curriculum detection"""
    analyzer = CurriculumAnalyzer("F:/nipun-offline")
    
    result = analyzer.analyze(
        curriculum_text="बच्चे 1 से 10 तक की संख्याओं को पहचानेंगे और वस्तुओं को गिनेंगे।",
        grade="Grade 1",
        user_domain=None
    )
    
    assert result['detected_domain'] == "Numeracy", f"Expected Numeracy, got {result['detected_domain']}"
    assert len(result['detected_topics']) > 0, "No topics detected"
    assert result['numbers_found'] == [1, 10], f"Expected [1, 10], got {result['numbers_found']}"
    print("✓ Numeracy detection test passed")


def test_literacy_detection():
    """Test literacy curriculum detection"""
    analyzer = CurriculumAnalyzer("F:/nipun-offline")
    
    result = analyzer.analyze(
        curriculum_text="बच्चे अक्षरों को पहचानेंगे और उनसे बनने वाले सरल शब्दों को पढ़ेंगे।",
        grade="Grade 1",
        user_domain=None
    )
    
    assert result['detected_domain'] == "Literacy", f"Expected Literacy, got {result['detected_domain']}"
    assert len(result['detected_topics']) > 0, "No topics detected"
    print("✓ Literacy detection test passed")


def test_comparison_detection():
    """Test comparison topic detection"""
    analyzer = CurriculumAnalyzer("F:/nipun-offline")
    
    result = analyzer.analyze(
        curriculum_text="बच्चे दो समूहों में वस्तुओं की संख्या की तुलना करेंगे।",
        grade="Grade 1",
        user_domain=None
    )
    
    assert result['detected_domain'] == "Numeracy"
    assert 'comparison' in result['detected_topics'], "Comparison topic not detected"
    print("✓ Comparison detection test passed")


if __name__ == "__main__":
    print("Running Curriculum Analyzer Tests...\n")
    test_numeracy_detection()
    test_literacy_detection()
    test_comparison_detection()
    print("\n✅ All tests passed!")
