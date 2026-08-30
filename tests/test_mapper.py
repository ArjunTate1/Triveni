"""
Test suite for NIPUN Mapper
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.nipun_mapper import NIPUNMapper


def test_nipun_mapping():
    """Test NIPUN outcome mapping"""
    mapper = NIPUNMapper("F:/nipun-offline")
    
    result = mapper.find_best_match(
        grade="Grade 1",
        domain="Numeracy",
        topics=["counting", "numbers"],
        skills=["number_recognition", "counting"],
        learning_objective="बच्चे 1 से 10 तक की संख्याओं को पहचानेंगे"
    )
    
    assert result['matched_outcome_id'] != "NO_MATCH", "No match found"
    assert result['confidence'] > 0, "Confidence should be > 0"
    assert len(result['competency']) > 0, "Competency should not be empty"
    print("✓ NIPUN mapping test passed")


def test_grade_filtering():
    """Test grade-specific outcome retrieval"""
    mapper = NIPUNMapper("F:/nipun-offline")
    
    outcomes = mapper.get_all_outcomes_for_grade("Grade 1")
    assert len(outcomes) > 0, "No outcomes found for Grade 1"
    
    for outcome in outcomes:
        assert outcome['grade'] == "Grade 1", f"Wrong grade: {outcome['grade']}"
    
    print("✓ Grade filtering test passed")


def test_domain_filtering():
    """Test domain filtering"""
    mapper = NIPUNMapper("F:/nipun-offline")
    
    numeracy_outcomes = mapper.get_outcomes_by_domain("Grade 1", "Numeracy")
    assert len(numeracy_outcomes) > 0, "No numeracy outcomes found"
    
    for outcome in numeracy_outcomes:
        assert outcome['domain'] == "Numeracy", f"Wrong domain: {outcome['domain']}"
    
    print("✓ Domain filtering test passed")


if __name__ == "__main__":
    print("Running NIPUN Mapper Tests...\n")
    test_nipun_mapping()
    test_grade_filtering()
    test_domain_filtering()
    print("\n✅ All tests passed!")
