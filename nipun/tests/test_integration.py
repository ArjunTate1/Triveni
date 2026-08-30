"""
Integration test - Complete pipeline
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.curriculum_analyzer import CurriculumAnalyzer
from app.services.nipun_mapper import NIPUNMapper
from app.services.activity_generator import ActivityGenerator
from app.services.worksheet_generator import WorksheetGenerator
from app.services.flashcard_generator import FlashcardGenerator
from app.services.assessment_generator import AssessmentGenerator


def test_complete_pipeline():
    """Test complete pipeline from curriculum to materials"""
    base_path = "F:/nipun-offline"
    
    # Initialize all services
    analyzer = CurriculumAnalyzer(base_path)
    mapper = NIPUNMapper(base_path)
    activity_gen = ActivityGenerator(base_path)
    worksheet_gen = WorksheetGenerator(base_path)
    flashcard_gen = FlashcardGenerator(base_path)
    assessment_gen = AssessmentGenerator(base_path)
    
    # Test curriculum
    curriculum = "बच्चे 1 से 10 तक की संख्याओं को पहचानेंगे और वस्तुओं को गिनेंगे।"
    
    # Step 1: Analyze
    print("1. Analyzing curriculum...")
    analysis = analyzer.analyze(curriculum, "Grade 1", None)
    assert analysis['detected_domain'] == "Numeracy"
    print("   ✓ Analysis complete")
    
    # Step 2: Map to NIPUN
    print("2. Mapping to NIPUN outcomes...")
    mapping = mapper.find_best_match(
        grade=analysis['grade'],
        domain=analysis['detected_domain'],
        topics=analysis['detected_topics'],
        skills=analysis['detected_skills'],
        learning_objective=analysis['learning_objective']
    )
    assert mapping['matched_outcome_id'] != "NO_MATCH"
    print("   ✓ Mapping complete")
    
    # Step 3: Generate activities
    print("3. Generating activities...")
    activities = activity_gen.generate(
        domain=analysis['detected_domain'],
        topics=analysis['detected_topics'],
        skills=analysis['detected_skills'],
        grade=analysis['grade']
    )
    assert len(activities) > 0
    print(f"   ✓ Generated {len(activities)} activities")
    
    # Step 4: Generate worksheet
    print("4. Generating worksheet...")
    worksheet = worksheet_gen.generate(
        grade=analysis['grade'],
        domain=analysis['detected_domain'],
        topic="Numbers",
        learning_objective=analysis['learning_objective'],
        nipun_reference=mapping['matched_outcome_id'],
        topics=analysis['detected_topics'],
        skills=analysis['detected_skills']
    )
    assert len(worksheet['questions']) > 0
    print(f"   ✓ Generated worksheet with {len(worksheet['questions'])} questions")
    
    # Step 5: Generate flashcards
    print("5. Generating flashcards...")
    flashcards = flashcard_gen.generate(
        grade=analysis['grade'],
        domain=analysis['detected_domain'],
        topic="Numbers",
        topics=analysis['detected_topics'],
        skills=analysis['detected_skills']
    )
    assert len(flashcards['flashcards']) > 0
    print(f"   ✓ Generated {len(flashcards['flashcards'])} flashcards")
    
    # Step 6: Generate assessment
    print("6. Generating assessment...")
    assessment = assessment_gen.generate(
        grade=analysis['grade'],
        domain=analysis['detected_domain'],
        topic="Numbers",
        learning_objective=analysis['learning_objective'],
        topics=analysis['detected_topics'],
        skills=analysis['detected_skills'],
        nipun_outcome_id=mapping['matched_outcome_id']
    )
    assert len(assessment['questions']) > 0
    print(f"   ✓ Generated assessment with {len(assessment['questions'])} questions")
    
    print("\n✅ Complete pipeline test passed!")


if __name__ == "__main__":
    print("Running Complete Pipeline Test...\n")
    test_complete_pipeline()
