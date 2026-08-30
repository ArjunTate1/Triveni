"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CurriculumInput(BaseModel):
    """Input from teacher"""
    grade: str = Field(..., description="Grade level (Balvatika, Grade 1, Grade 2, Grade 3)")
    domain: Optional[str] = Field(None, description="Literacy or Numeracy")
    topic: Optional[str] = Field(None, description="Optional topic specification")
    curriculum_text: str = Field(..., description="Hindi curriculum content")


class AnalysisResult(BaseModel):
    """Analysis output from curriculum analyzer"""
    grade: str
    detected_domain: str
    detected_topics: List[str]
    detected_skills: List[str]
    learning_objective: str
    numbers_found: List[int]
    confidence: Dict[str, float]


class NIPUNMapping(BaseModel):
    """NIPUN outcome mapping result"""
    matched_outcome_id: str
    competency: str
    learning_outcome: str
    matched_skills: List[str]
    confidence: float


class Activity(BaseModel):
    """Generated activity"""
    title: str
    instructions: str
    materials: List[str]
    steps: List[str]
    duration: str


class Question(BaseModel):
    """Worksheet question"""
    question_number: int
    question_type: str
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    skill: str


class Worksheet(BaseModel):
    """Generated worksheet"""
    grade: str
    domain: str
    topic: str
    learning_objective: str
    nipun_reference: str
    instructions: str
    questions: List[Question]
    answer_key: Dict[int, str]


class Flashcard(BaseModel):
    """Single flashcard"""
    front_text: str
    front_image: Optional[str] = None
    back_text: str
    back_image: Optional[str] = None


class FlashcardSet(BaseModel):
    """Set of flashcards"""
    title: str
    grade: str
    domain: str
    topic: str
    flashcards: List[Flashcard]


class AssessmentQuestion(BaseModel):
    """Assessment question"""
    question_number: int
    question: str
    question_type: str
    expected_answer: str
    skill: str
    difficulty: str
    learning_outcome_reference: str


class Assessment(BaseModel):
    """Generated assessment"""
    title: str
    grade: str
    domain: str
    topic: str
    instructions: str
    questions: List[AssessmentQuestion]
    total_marks: int


class GeneratedContent(BaseModel):
    """Complete generated learning material"""
    analysis: AnalysisResult
    nipun_mapping: NIPUNMapping
    activities: List[Activity]
    worksheet: Worksheet
    flashcards: FlashcardSet
    assessment: Assessment
