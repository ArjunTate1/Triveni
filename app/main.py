"""
Main FastAPI application
Runs ONLY on localhost - NO INTERNET ACCESS
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn

from app.models.schemas import CurriculumInput, GeneratedContent, AnalysisResult, NIPUNMapping
from app.services.curriculum_analyzer import CurriculumAnalyzer
from app.services.nipun_mapper import NIPUNMapper
from app.services.activity_generator import ActivityGenerator
from app.services.worksheet_generator import WorksheetGenerator
from app.services.flashcard_generator import FlashcardGenerator
from app.services.assessment_generator import AssessmentGenerator
from app.services.assignment_generator import AssignmentGenerator
from app.services.study_material_generator import StudyMaterialGenerator
from app.services.quiz_generator import QuizGenerator
from app.services.pdf_generator import PDFGenerator

# Initialize FastAPI app
app = FastAPI(
    title="NIPUN Offline Learning Material Generator",
    description="Offline, rule-based NIPUN/FLN curriculum mapping and learning-material generation engine",
    version="2.0.0"
)

# CORS for local development - ONLY localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services with base path
BASE_PATH = Path(__file__).parent.parent

# Mount frontend static files
frontend_path = BASE_PATH / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

analyzer = CurriculumAnalyzer(str(BASE_PATH))
mapper = NIPUNMapper(str(BASE_PATH))
activity_gen = ActivityGenerator(str(BASE_PATH))
worksheet_gen = WorksheetGenerator(str(BASE_PATH))
flashcard_gen = FlashcardGenerator(str(BASE_PATH))
assessment_gen = AssessmentGenerator(str(BASE_PATH))
assignment_gen = AssignmentGenerator(str(BASE_PATH))
study_material_gen = StudyMaterialGenerator(str(BASE_PATH))
quiz_gen = QuizGenerator(str(BASE_PATH))
pdf_gen = PDFGenerator(str(BASE_PATH))


# ─────────────────────────────────────────────
# CORE ANALYSIS & MAPPING
# ─────────────────────────────────────────────

@app.get("/")
async def root():
    """Serve the frontend"""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "NIPUN Offline Application - API is running", "docs": "/docs"}

@app.post("/api/analyze")
async def analyze_curriculum(input_data: CurriculumInput):
    """
    Analyze Hindi curriculum text
    NO INTERNET - All processing is local
    """
    try:
        analysis = analyzer.analyze(
            curriculum_text=input_data.curriculum_text,
            grade=input_data.grade,
            user_domain=input_data.domain
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.post("/api/map")
async def map_to_nipun(analysis: dict):
    """
    Map analyzed curriculum to NIPUN learning outcomes
    NO INTERNET - All matching is local
    """
    try:
        mapping = mapper.find_best_match(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective']
        )
        return mapping
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mapping error: {str(e)}")


# ─────────────────────────────────────────────
# GENERATION ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/api/generate/complete")
async def generate_all_materials(input_data: CurriculumInput):
    """
    Complete pipeline: Analyze → Map → Generate all core materials
    (activities, worksheet, flashcards, assessment)
    NO INTERNET - Everything is local
    """
    try:
        # Step 1: Analyze
        analysis = analyzer.analyze(
            curriculum_text=input_data.curriculum_text,
            grade=input_data.grade,
            user_domain=input_data.domain
        )

        # Step 2: Map to NIPUN
        nipun_mapping = mapper.find_best_match(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective']
        )

        # Step 3: Generate activities
        activities = activity_gen.generate(
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            grade=analysis['grade']
        )

        # Step 4: Generate worksheet
        worksheet = worksheet_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=input_data.topic or ", ".join(analysis['detected_topics'][:2]),
            learning_objective=analysis['learning_objective'],
            nipun_reference=nipun_mapping['matched_outcome_id'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills']
        )

        # Step 5: Generate flashcards
        flashcards = flashcard_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=input_data.topic or ", ".join(analysis['detected_topics'][:2]),
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills']
        )

        # Step 6: Generate assessment
        assessment = assessment_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=input_data.topic or ", ".join(analysis['detected_topics'][:2]),
            learning_objective=analysis['learning_objective'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            nipun_outcome_id=nipun_mapping['matched_outcome_id']
        )

        # Step 7: Generate quiz
        quiz = quiz_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=input_data.topic or ", ".join(analysis['detected_topics'][:2]),
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            num_questions=10
        )

        return {
            "analysis": analysis,
            "nipun_mapping": nipun_mapping,
            "activities": activities,
            "worksheet": worksheet,
            "flashcards": flashcards,
            "assessment": assessment,
            "quiz": quiz
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@app.post("/api/generate/assignment")
async def generate_assignment(input_data: CurriculumInput):
    """
    Generate a homework assignment
    NO INTERNET - Completely local
    """
    try:
        # Analyze first to get domain/topics/skills
        analysis = analyzer.analyze(
            curriculum_text=input_data.curriculum_text,
            grade=input_data.grade,
            user_domain=input_data.domain
        )

        nipun_mapping = mapper.find_best_match(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective']
        )

        assignment = assignment_gen.generate(
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            grade=analysis['grade'],
            learning_objective=analysis['learning_objective'],
            nipun_reference=nipun_mapping['matched_outcome_id']
        )

        return {
            "analysis": analysis,
            "nipun_mapping": nipun_mapping,
            "assignment": assignment
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assignment generation error: {str(e)}")


@app.post("/api/generate/lesson-plan")
async def generate_lesson_plan(input_data: CurriculumInput):
    """
    Generate a teacher lesson plan
    NO INTERNET - Completely local
    """
    try:
        analysis = analyzer.analyze(
            curriculum_text=input_data.curriculum_text,
            grade=input_data.grade,
            user_domain=input_data.domain
        )

        nipun_mapping = mapper.find_best_match(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective']
        )

        lesson_plan = study_material_gen.generate_lesson_plan(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective'],
            nipun_reference=nipun_mapping['matched_outcome_id']
        )

        return {
            "analysis": analysis,
            "nipun_mapping": nipun_mapping,
            "lesson_plan": lesson_plan
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesson plan generation error: {str(e)}")


@app.post("/api/generate/study-guide")
async def generate_study_guide(input_data: CurriculumInput):
    """
    Generate a student study guide
    NO INTERNET - Completely local
    """
    try:
        analysis = analyzer.analyze(
            curriculum_text=input_data.curriculum_text,
            grade=input_data.grade,
            user_domain=input_data.domain
        )

        study_guide = study_material_gen.generate_study_guide(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective']
        )

        return {
            "analysis": analysis,
            "study_guide": study_guide
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Study guide generation error: {str(e)}")


@app.post("/api/generate/quiz")
async def generate_quiz(input_data: CurriculumInput):
    """
    Generate an MCQ quiz
    NO INTERNET - Completely local
    """
    try:
        analysis = analyzer.analyze(
            curriculum_text=input_data.curriculum_text,
            grade=input_data.grade,
            user_domain=input_data.domain
        )

        quiz = quiz_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=input_data.topic or ", ".join(analysis['detected_topics'][:2]),
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            num_questions=10
        )

        return {
            "analysis": analysis,
            "quiz": quiz
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation error: {str(e)}")


@app.post("/api/generate/all-extended")
async def generate_all_extended(input_data: CurriculumInput):
    """
    Extended pipeline: Analyze → Map → Generate ALL materials including
    activities, worksheet, flashcards, assessment, assignment, lesson plan, study guide
    NO INTERNET - Everything is local
    """
    try:
        # Step 1: Analyze
        analysis = analyzer.analyze(
            curriculum_text=input_data.curriculum_text,
            grade=input_data.grade,
            user_domain=input_data.domain
        )

        # Step 2: Map to NIPUN
        nipun_mapping = mapper.find_best_match(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective']
        )

        topic_label = input_data.topic or ", ".join(analysis['detected_topics'][:2])

        # Step 3: Core materials
        activities = activity_gen.generate(
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            grade=analysis['grade']
        )

        worksheet = worksheet_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=topic_label,
            learning_objective=analysis['learning_objective'],
            nipun_reference=nipun_mapping['matched_outcome_id'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills']
        )

        flashcards = flashcard_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=topic_label,
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills']
        )

        assessment = assessment_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=topic_label,
            learning_objective=analysis['learning_objective'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            nipun_outcome_id=nipun_mapping['matched_outcome_id']
        )

        # Step 4: Extended materials
        assignment = assignment_gen.generate(
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            grade=analysis['grade'],
            learning_objective=analysis['learning_objective'],
            nipun_reference=nipun_mapping['matched_outcome_id']
        )

        lesson_plan = study_material_gen.generate_lesson_plan(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective'],
            nipun_reference=nipun_mapping['matched_outcome_id']
        )

        study_guide = study_material_gen.generate_study_guide(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            learning_objective=analysis['learning_objective']
        )

        # Generate quiz
        quiz = quiz_gen.generate(
            grade=analysis['grade'],
            domain=analysis['detected_domain'],
            topic=topic_label,
            topics=analysis['detected_topics'],
            skills=analysis['detected_skills'],
            num_questions=10
        )

        return {
            "analysis": analysis,
            "nipun_mapping": nipun_mapping,
            "activities": activities,
            "worksheet": worksheet,
            "flashcards": flashcards,
            "assessment": assessment,
            "assignment": assignment,
            "lesson_plan": lesson_plan,
            "study_guide": study_guide,
            "quiz": quiz
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extended generation error: {str(e)}")


# ─────────────────────────────────────────────
# EXPORT ENDPOINTS
# ─────────────────────────────────────────────

@app.post("/api/export/worksheet")
async def export_worksheet(worksheet: dict):
    """Export worksheet as PDF - NO INTERNET"""
    try:
        filename = f"worksheet_{worksheet.get('grade', 'output').replace(' ', '_')}_{worksheet.get('domain', 'content')}.pdf"
        filepath = str(BASE_PATH / filename)
        pdf_gen.generate_worksheet_pdf(worksheet, filepath)
        
        # Return file for download
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@app.post("/api/export/flashcards")
async def export_flashcards(flashcards: dict):
    """Export flashcards as PDF - NO INTERNET"""
    try:
        filename = f"flashcards_{flashcards.get('grade', 'output').replace(' ', '_')}_{flashcards.get('domain', 'content')}.pdf"
        filepath = str(BASE_PATH / filename)
        pdf_gen.generate_flashcard_pdf(flashcards, filepath)
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@app.post("/api/export/assessment")
async def export_assessment(assessment: dict):
    """Export assessment as PDF - NO INTERNET"""
    try:
        filename = f"assessment_{assessment.get('grade', 'output').replace(' ', '_')}_{assessment.get('domain', 'content')}.pdf"
        filepath = str(BASE_PATH / filename)
        pdf_gen.generate_assessment_pdf(assessment, filepath)
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@app.post("/api/export/assignment")
async def export_assignment(assignment: dict):
    """Export assignment as PDF - NO INTERNET"""
    try:
        filename = f"assignment_{assignment.get('grade', 'output').replace(' ', '_')}_{assignment.get('domain', 'content')}.pdf"
        filepath = str(BASE_PATH / filename)
        pdf_gen.generate_assignment_pdf(assignment, filepath)
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@app.post("/api/export/lesson-plan")
async def export_lesson_plan(lesson_plan: dict):
    """Export lesson plan as PDF - NO INTERNET"""
    try:
        filename = f"lesson_plan_{lesson_plan.get('grade', 'output').replace(' ', '_')}_{lesson_plan.get('domain', 'content')}.pdf"
        filepath = str(BASE_PATH / filename)
        pdf_gen.generate_lesson_plan_pdf(lesson_plan, filepath)
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@app.post("/api/export/study-guide")
async def export_study_guide(study_guide: dict):
    """Export study guide as PDF - NO INTERNET"""
    try:
        filename = f"study_guide_{study_guide.get('grade', 'output').replace(' ', '_')}_{study_guide.get('domain', 'content')}.pdf"
        filepath = str(BASE_PATH / filename)
        pdf_gen.generate_study_guide_pdf(study_guide, filepath)
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "offline",
        "version": "2.0.0",
        "message": "NIPUN Offline Application is running locally",
        "endpoints": {
            "core": ["/api/analyze", "/api/map", "/api/generate/complete"],
            "extended": [
                "/api/generate/assignment",
                "/api/generate/lesson-plan",
                "/api/generate/study-guide",
                "/api/generate/all-extended"
            ],
            "export": [
                "/api/export/worksheet",
                "/api/export/flashcards",
                "/api/export/assessment",
                "/api/export/assignment",
                "/api/export/lesson-plan",
                "/api/export/study-guide"
            ]
        }
    }


if __name__ == "__main__":
    # Run ONLY on localhost - NO external access
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
