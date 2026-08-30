"""
NIPUN Offline - Terminal Prototype
100% OFFLINE | NO INTERNET | NO WEB FRONTEND
All interaction through command line
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.curriculum_analyzer import CurriculumAnalyzer
from app.services.nipun_mapper import NIPUNMapper
from app.services.activity_generator import ActivityGenerator
from app.services.worksheet_generator import WorksheetGenerator
from app.services.flashcard_generator import FlashcardGenerator
from app.services.assessment_generator import AssessmentGenerator
from app.services.pdf_generator import PDFGenerator


def print_header():
    """Print application header"""
    print("\n" + "="*70)
    print("  NIPUN OFFLINE LEARNING MATERIAL GENERATOR")
    print("  100% OFFLINE | NO INTERNET REQUIRED")
    print("="*70 + "\n")


def print_section(title):
    """Print section header"""
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}")


def get_grade_input():
    """Get grade selection from user"""
    print("\nSelect Grade / कक्षा चुनें:")
    print("1. Balvatika")
    print("2. Grade 1")
    print("3. Grade 2")
    print("4. Grade 3")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    grades = {
        "1": "Balvatika",
        "2": "Grade 1",
        "3": "Grade 2",
        "4": "Grade 3"
    }
    
    return grades.get(choice, "Grade 1")


def get_domain_input():
    """Get domain selection from user"""
    print("\nSelect Domain / क्षेत्र चुनें (optional):")
    print("1. Auto-detect / स्वचालित")
    print("2. Numeracy / संख्यात्मक")
    print("3. Literacy / साक्षरता")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    domains = {
        "1": None,
        "2": "Numeracy",
        "3": "Literacy"
    }
    
    return domains.get(choice, None)


def get_curriculum_input():
    """Get curriculum text from user"""
    print("\nEnter Hindi Curriculum Text / हिंदी पाठ्यक्रम दर्ज करें:")
    print("(Examples below - you can type your own)")
    print("  • बच्चे 1 से 10 तक की संख्याओं को पहचानेंगे और वस्तुओं को गिनेंगे।")
    print("  • बच्चे अक्षरों को पहचानेंगे और उनसे बनने वाले सरल शब्दों को पढ़ेंगे।")
    print("  • बच्चे दो समूहों में वस्तुओं की संख्या की तुलना करेंगे।")
    print()
    
    curriculum = input("Enter curriculum: ").strip()
    
    if not curriculum:
        print("⚠️  Using default example...")
        curriculum = "बच्चे 1 से 10 तक की संख्याओं को पहचानेंगे और वस्तुओं को गिनेंगे।"
    
    return curriculum


def display_analysis(analysis):
    """Display analysis results"""
    print_section("[ANALYSIS RESULTS]")
    
    print(f"\n✓ Grade: {analysis['grade']}")
    print(f"✓ Detected Domain: {analysis['detected_domain']}")
    print(f"✓ Topics: {', '.join(analysis['detected_topics']) if analysis['detected_topics'] else 'None'}")
    print(f"✓ Skills: {', '.join(analysis['detected_skills']) if analysis['detected_skills'] else 'None'}")
    print(f"✓ Numbers Found: {', '.join(map(str, analysis['numbers_found'])) if analysis['numbers_found'] else 'None'}")
    print(f"\n✓ Learning Objective:")
    print(f"  {analysis['learning_objective']}")
    
    print(f"\n✓ Confidence Scores:")
    print(f"  - Domain: {analysis['confidence']['domain']}")
    print(f"  - Topics: {analysis['confidence']['topics']}")
    print(f"  - Skills: {analysis['confidence']['skills']}")
    print(f"  - Overall: {analysis['confidence']['overall']}")


def display_mapping(mapping):
    """Display NIPUN mapping results"""
    print_section("[NIPUN MAPPING]")
    
    print(f"\n✓ Matched Outcome ID: {mapping['matched_outcome_id']}")
    print(f"✓ Competency: {mapping['competency']}")
    print(f"✓ Learning Outcome:")
    print(f"  {mapping['learning_outcome']}")
    print(f"✓ Matched Skills: {', '.join(mapping['matched_skills']) if mapping['matched_skills'] else 'None'}")
    print(f"✓ Confidence: {mapping['confidence']*100:.0f}%")


def display_activities(activities):
    """Display generated activities"""
    print_section("[GENERATED ACTIVITIES]")
    
    for i, activity in enumerate(activities, 1):
        print(f"\n📌 Activity {i}: {activity['title']}")
        print(f"   Instructions: {activity['instructions']}")
        print(f"   Materials: {', '.join(activity['materials'])}")
        print(f"   Duration: {activity['duration']}")
        print(f"   Steps:")
        for j, step in enumerate(activity['steps'], 1):
            print(f"     {j}. {step}")


def display_worksheet(worksheet):
    """Display generated worksheet"""
    print_section("[GENERATED WORKSHEET]")
    
    print(f"\n✓ Grade: {worksheet['grade']}")
    print(f"✓ Domain: {worksheet['domain']}")
    print(f"✓ Topic: {worksheet['topic']}")
    print(f"✓ Learning Objective: {worksheet['learning_objective']}")
    print(f"✓ NIPUN Reference: {worksheet['nipun_reference']}")
    print(f"\nInstructions: {worksheet['instructions']}")
    
    print(f"\nQuestions ({len(worksheet['questions'])}):")
    for q in worksheet['questions']:
        print(f"\n  Q{q['question_number']}. {q['question_text']}")
        print(f"      Type: {q['question_type']}")
        print(f"      Answer: {q['correct_answer']}")


def display_flashcards(flashcards):
    """Display generated flashcards"""
    print_section("[GENERATED FLASHCARDS]")
    
    print(f"\n✓ Title: {flashcards['title']}")
    print(f"✓ Grade: {flashcards['grade']}")
    print(f"✓ Domain: {flashcards['domain']}")
    
    print(f"\nFlashcards ({len(flashcards['flashcards'])}):")
    for i, card in enumerate(flashcards['flashcards'][:5], 1):  # Show first 5
        print(f"\n  Card {i}:")
        print(f"    Front: {card['front_text']}")
        print(f"    Back:  {card['back_text']}")
    
    if len(flashcards['flashcards']) > 5:
        print(f"\n  ... and {len(flashcards['flashcards']) - 5} more cards")


def display_assessment(assessment):
    """Display generated assessment"""
    print_section("[GENERATED ASSESSMENT]")
    
    print(f"\n✓ Title: {assessment['title']}")
    print(f"✓ Grade: {assessment['grade']}")
    print(f"✓ Domain: {assessment['domain']}")
    print(f"✓ Total Marks: {assessment['total_marks']}")
    print(f"\nInstructions: {assessment['instructions']}")
    
    print(f"\nQuestions ({len(assessment['questions'])}):")
    for q in assessment['questions']:
        print(f"\n  Q{q['question_number']}. {q['question']}")
        print(f"      Type: {q['question_type']}")
        print(f"      Difficulty: {q['difficulty']}")
        print(f"      Expected Answer: {q['expected_answer']}")


def export_pdfs(worksheet, flashcards, assessment, pdf_gen, base_path):
    """Export all materials as PDFs"""
    print_section("[EXPORTING PDFs]")
    
    try:
        # Export worksheet
        worksheet_file = str(base_path / f"worksheet_{worksheet['grade'].replace(' ', '_')}_{worksheet['domain']}.pdf")
        pdf_gen.generate_worksheet_pdf(worksheet, worksheet_file)
        print(f"✓ Worksheet PDF: {worksheet_file}")
        
        # Export flashcards
        flashcards_file = str(base_path / f"flashcards_{flashcards['grade'].replace(' ', '_')}_{flashcards['domain']}.pdf")
        pdf_gen.generate_flashcard_pdf(flashcards, flashcards_file)
        print(f"✓ Flashcards PDF: {flashcards_file}")
        
        # Export assessment
        assessment_file = str(base_path / f"assessment_{assessment['grade'].replace(' ', '_')}_{assessment['domain']}.pdf")
        pdf_gen.generate_assessment_pdf(assessment, assessment_file)
        print(f"✓ Assessment PDF: {assessment_file}")
        
        print(f"\n[OK] All PDFs exported successfully!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] PDF Export Error: {e}")
        return False


def main():
    """Main application flow"""
    print_header()
    
    # Initialize services
    base_path = Path(__file__).parent
    print("[*] Initializing services (offline)...")
    
    try:
        analyzer = CurriculumAnalyzer(str(base_path))
        mapper = NIPUNMapper(str(base_path))
        activity_gen = ActivityGenerator(str(base_path))
        worksheet_gen = WorksheetGenerator(str(base_path))
        flashcard_gen = FlashcardGenerator(str(base_path))
        assessment_gen = AssessmentGenerator(str(base_path))
        pdf_gen = PDFGenerator(str(base_path))
        
        print("[OK] All services initialized successfully!\n")
        
    except Exception as e:
        print(f"[ERROR] Initialization Error: {e}")
        print("Please check that all data files exist in F:/nipun-offline/data/")
        return
    
    # Get user inputs
    grade = get_grade_input()
    domain_hint = get_domain_input()
    curriculum = get_curriculum_input()
    
    print("\n[*] Processing curriculum (offline)...")
    
    # Step 1: Analyze curriculum
    try:
        analysis = analyzer.analyze(curriculum, grade, domain_hint)
        display_analysis(analysis)
    except Exception as e:
        print(f"[ERROR] Analysis Error: {e}")
        return
    
    # Step 2: Map to NIPUN
    try:
        mapping = mapper.find_best_match(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective']
        )
        display_mapping(mapping)
    except Exception as e:
        print(f"[ERROR] Mapping Error: {e}")
        return
    
    # Ask if user wants to generate materials
    print("\n" + "─"*70)
    response = input("\nGenerate learning materials? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\n[*] Exiting. No materials generated.")
        return
    
    print("\n[*] Generating learning materials (offline)...")
    
    # Step 3: Generate activities
    try:
        activities = activity_gen.generate(
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            grade=analysis['grade']
        )
        display_activities(activities)
    except Exception as e:
        print(f"[ERROR] Activity Generation Error: {e}")
        activities = []
    
    # Step 4: Generate worksheet
    try:
        worksheet = worksheet_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=", ".join(analysis['detected_topics'][:2]) if analysis['detected_topics'] else "General",
            learning_objective=analysis['learning_objective'],
            nipun_reference=mapping['matched_outcome_id'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills']
        )
        display_worksheet(worksheet)
    except Exception as e:
        print(f"[ERROR] Worksheet Generation Error: {e}")
        worksheet = None
    
    # Step 5: Generate flashcards
    try:
        flashcards = flashcard_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=", ".join(analysis['detected_topics'][:2]) if analysis['detected_topics'] else "General",
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills']
        )
        display_flashcards(flashcards)
    except Exception as e:
        print(f"[ERROR] Flashcard Generation Error: {e}")
        flashcards = None
    
    # Step 6: Generate assessment
    try:
        assessment = assessment_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=", ".join(analysis['detected_topics'][:2]) if analysis['detected_topics'] else "General",
            learning_objective=analysis['learning_objective'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            nipun_outcome_id=mapping['matched_outcome_id']
        )
        display_assessment(assessment)
    except Exception as e:
        print(f"[ERROR] Assessment Generation Error: {e}")
        assessment = None
    
    # Ask if user wants to export PDFs
    print("\n" + "─"*70)
    response = input("\nExport all materials as PDFs? (y/n): ").strip().lower()
    
    if response == 'y' and worksheet and flashcards and assessment:
        export_pdfs(worksheet, flashcards, assessment, pdf_gen, base_path)
    
    # Final summary
    print("\n" + "="*70)
    print("  [OK] COMPLETE - All processing done offline!")
    print("  [*] PDFs saved in: F:/nipun-offline/")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
