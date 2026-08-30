"""
PDF Generator - Generate PDFs with Hindi/Devanagari support
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, List
import os


class PDFGenerator:
    """Generate PDFs for worksheets, flashcards, and assessments"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self.font_name = self._register_hindi_font()
    
    def _register_hindi_font(self):
        """Register a Unicode font that supports Devanagari"""
        try:
            font_paths = [
                "C:/Windows/Fonts/mangal.ttf",
                "C:/Windows/Fonts/NirmalaS.ttf",
                "C:/Windows/Fonts/Kokila.ttf"
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('HindiFont', font_path))
                        print(f"[OK] Using Hindi font: {os.path.basename(font_path)}")
                        return 'HindiFont'
                    except:
                        continue
            
            print("[!] Hindi font not found, using Helvetica (limited Hindi support)")
            return 'Helvetica'
                
        except Exception as e:
            print(f"[!] Font registration warning: Using Helvetica")
            return 'Helvetica'
    
    def generate_worksheet_pdf(self, worksheet: Dict, filename: str) -> str:
        """Generate worksheet PDF"""
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Title
        c.setFont(self.font_name, 16)
        c.drawCentredString(width/2, height-50, f"Worksheet - {worksheet['domain']}")
        
        # Metadata
        c.setFont(self.font_name, 10)
        y = height - 90
        c.drawString(50, y, f"Grade: {worksheet['grade']}")
        y -= 20
        c.drawString(50, y, f"Topic: {worksheet['topic']}")
        y -= 20
        c.drawString(50, y, f"NIPUN Ref: {worksheet['nipun_reference']}")
        y -= 30
        
        # Instructions
        c.setFont(self.font_name, 10)
        c.drawString(50, y, f"Instructions: {worksheet['instructions']}")
        y -= 40
        
        # Questions
        c.setFont(self.font_name, 11)
        for q in worksheet['questions']:
            if y < 100:  # New page if needed
                c.showPage()
                y = height - 50
                c.setFont(self.font_name, 11)
            
            question_text = f"{q['question_number']}. {q['question_text']}"
            c.drawString(50, y, question_text)
            y -= 40
        
        # Answer key
        if y < 200:
            c.showPage()
            y = height - 50
        
        y -= 30
        c.setFont(self.font_name, 12)
        c.drawString(50, y, "Answer Key:")
        y -= 30
        
        c.setFont(self.font_name, 10)
        for num, answer in worksheet['answer_key'].items():
            c.drawString(50, y, f"{num}. {answer}")
            y -= 20
        
        c.save()
        return filename
    
    def generate_flashcard_pdf(self, flashcards: Dict, filename: str) -> str:
        """Generate flashcard PDF"""
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Title
        c.setFont(self.font_name, 16)
        c.drawCentredString(width/2, height-50, flashcards['title'])
        
        c.setFont(self.font_name, 10)
        c.drawString(50, height-80, f"Grade: {flashcards['grade']} | Domain: {flashcards['domain']}")
        
        y = height - 120
        
        # Flashcards
        for i, card in enumerate(flashcards['flashcards'], 1):
            if y < 100:
                c.showPage()
                y = height - 50
            
            c.setFont(self.font_name, 12)
            c.drawString(50, y, f"Flashcard {i}:")
            y -= 25
            
            c.setFont(self.font_name, 14)
            c.drawString(70, y, f"Front: {card['front_text']}")
            y -= 25
            c.drawString(70, y, f"Back: {card['back_text']}")
            y -= 40
        
        c.save()
        return filename
    
    def generate_assessment_pdf(self, assessment: Dict, filename: str) -> str:
        """Generate assessment PDF"""
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Title
        c.setFont(self.font_name, 16)
        c.drawCentredString(width/2, height-50, assessment['title'])
        
        # Metadata
        c.setFont(self.font_name, 10)
        y = height - 90
        c.drawString(50, y, f"Grade: {assessment['grade']} | Topic: {assessment['topic']}")
        y -= 20
        c.drawString(50, y, f"Total Marks: {assessment['total_marks']}")
        y -= 30
        c.drawString(50, y, f"Instructions: {assessment['instructions']}")
        y -= 50
        
        # Questions
        c.setFont(self.font_name, 11)
        for q in assessment['questions']:
            if y < 100:
                c.showPage()
                y = height - 50
                c.setFont(self.font_name, 11)
            
            question_text = f"{q['question_number']}. {q['question']}"
            c.drawString(50, y, question_text)
            y -= 20
            c.setFont(self.font_name, 9)
            c.drawString(70, y, f"(Difficulty: {q['difficulty']} | Skill: {q['skill']})")
            y -= 40
            c.setFont(self.font_name, 11)
        
        c.save()
        return filename
