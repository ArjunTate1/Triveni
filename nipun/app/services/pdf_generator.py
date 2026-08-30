"""
PDF Generator - Generate PDFs with Hindi/Devanagari support
NO INTERNET | NO AI MODEL | COMPLETELY OFFLINE
"""
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, List
import os
from datetime import datetime


class PDFGenerator:
    """
    Generate PDFs for worksheets, flashcards, assessments, assignments, and study materials
    with enhanced Hindi/Devanagari support and rich formatting
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        self._register_hindi_font()
        self._create_styles()
    
    def _register_hindi_font(self):
        """
        Register a Unicode font that supports Devanagari
        Uses system fonts or fallback to Helvetica
        """
        try:
            # Try to use Windows system font for Devanagari
            font_paths = [
                ("C:/Windows/Fonts/mangal.ttf", "HindiFont"),
                ("C:/Windows/Fonts/Nirmala.ttc", "HindiFont"),  # Nirmala UI (TTC format)
                ("C:/Windows/Fonts/Kokila.ttf", "HindiFont"),
                ("C:/Windows/Fonts/mangalb.ttf", "HindiFont"),  # Mangal Bold
            ]
            
            font_registered = False
            for font_path, font_name in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        self.font_name = font_name
                        font_registered = True
                        print(f"[OK] Hindi font registered: {font_path}", flush=True)
                        break
                    except Exception as e:
                        print(f"[WARN] Could not register {font_path}: {e}", flush=True)
                        continue
            
            if not font_registered:
                # Use default Helvetica which has some Unicode support
                self.font_name = 'Helvetica'
                print("[WARN] Warning: Using Helvetica font (limited Hindi support)", flush=True)
                
        except Exception as e:
            self.font_name = 'Helvetica'
            print(f"[WARN] Font registration warning: {e}. Using Helvetica.", flush=True)
    
    def _create_styles(self):
        """Create custom paragraph styles for better formatting"""
        self.styles = {}
        
        # Title style
        self.styles['Title'] = ParagraphStyle(
            'Title',
            fontName=self.font_name,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=16,
            textColor=colors.HexColor('#1a237e'),
            bold=True
        )
        
        # Heading style
        self.styles['Heading1'] = ParagraphStyle(
            'Heading1',
            fontName=self.font_name,
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=12,
            textColor=colors.HexColor('#283593'),
            bold=True
        )
        
        # Subheading style
        self.styles['Heading2'] = ParagraphStyle(
            'Heading2',
            fontName=self.font_name,
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=10,
            textColor=colors.HexColor('#3949ab')
        )
        
        # Normal text style
        self.styles['Normal'] = ParagraphStyle(
            'Normal',
            fontName=self.font_name,
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=8,
            leading=14
        )
        
        # Meta information style
        self.styles['Meta'] = ParagraphStyle(
            'Meta',
            fontName=self.font_name,
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6,
            textColor=colors.HexColor('#424242')
        )
        
        # Question style
        self.styles['Question'] = ParagraphStyle(
            'Question',
            fontName=self.font_name,
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=8,
            leftIndent=10
        )
        
        # Instructions style
        self.styles['Instructions'] = ParagraphStyle(
            'Instructions',
            fontName=self.font_name,
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=12,
            textColor=colors.HexColor('#d32f2f'),
            backColor=colors.HexColor('#ffebee'),
            borderPadding=6
        )
    
    def generate_worksheet_pdf(self, worksheet: Dict, filename: str) -> str:
        """Generate worksheet PDF with enhanced formatting"""
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        
        # Title
        story.append(Paragraph(f"📝 वर्कशीट - {worksheet['domain']}", self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata table
        meta_data = [
            ["कक्षा:", worksheet['grade'], "विषय:", worksheet['topic']],
            ["दिनांक:", datetime.now().strftime("%d/%m/%Y"), "नाम:", "_______________"]
        ]
        meta_table = Table(meta_data, colWidths=[1*inch, 2*inch, 1*inch, 2*inch])
        meta_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e3f2fd')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Learning objective
        story.append(Paragraph(f"<b>सीखने का उद्देश्य:</b> {worksheet['learning_objective']}", self.styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        # Instructions
        story.append(Paragraph(f"<b>निर्देश:</b> {worksheet['instructions']}", self.styles['Instructions']))
        story.append(Spacer(1, 0.2*inch))
        
        # Questions
        story.append(Paragraph("प्रश्न:", self.styles['Heading1']))
        
        for q in worksheet['questions']:
            q_text = f"<b>Q{q['question_number']}.</b> {q['question_text']}"
            story.append(Paragraph(q_text, self.styles['Question']))
            story.append(Paragraph("उत्तर: _______________________________", self.styles['Normal']))
            story.append(Spacer(1, 0.25*inch))
        
        # Answer key (on separate section)
        story.append(PageBreak())
        story.append(Paragraph("🔑 उत्तर कुंजी (Answer Key)", self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        answer_data = [[f"Q{num}", answer] for num, answer in worksheet['answer_key'].items()]
        answer_table = Table(answer_data, colWidths=[1*inch, 5*inch])
        answer_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c8e6c9')),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(answer_table)
        
        doc.build(story)
        print(f"[OK] Worksheet PDF generated: {filename}", flush=True)
        return filename
    
    def generate_flashcard_pdf(self, flashcards: Dict, filename: str) -> str:
        """Generate flashcard PDF with enhanced layout"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph(flashcards['title'], self.styles['Title']))
        story.append(Spacer(1, 0.3*inch))
        
        # Flashcards in table format
        for i, card in enumerate(flashcards['flashcards'], 1):
            # Card container
            card_data = [
                [Paragraph(f"<b>फ्लैशकार्ड {i}</b>", self.styles['Heading2'])],
                [Paragraph(f"<b>सामने (Front):</b>", self.styles['Normal'])],
                [Paragraph(f"<font size=16>{card['front_text']}</font>", self.styles['Normal'])],
                [Paragraph(f"<b>पीछे (Back):</b>", self.styles['Normal'])],
                [Paragraph(f"{card['back_text']}", self.styles['Normal'])]
            ]
            
            card_table = Table(card_data, colWidths=[6*inch])
            card_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 11),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#3f51b5')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eaf6')),
                ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fff9c4')),
                ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#c8e6c9')),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(card_table)
            story.append(Spacer(1, 0.25*inch))
            
            # Page break after every 3 cards
            if i % 3 == 0 and i < len(flashcards['flashcards']):
                story.append(PageBreak())
        
        doc.build(story)
        print(f"[OK] Flashcards PDF generated: {filename}", flush=True)
        return filename
    
    def generate_assessment_pdf(self, assessment: Dict, filename: str) -> str:
        """Generate assessment PDF with enhanced formatting"""
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch)
        story = []
        
        # Title
        story.append(Paragraph(assessment['title'], self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata table
        meta_data = [
            ["कक्षा:", assessment['grade'], "विषय:", assessment['topic']],
            ["कुल अंक:", str(assessment['total_marks']), "समय:", "30-40 मिनट"],
            ["छात्र का नाम:", "_______________", "दिनांक:", datetime.now().strftime("%d/%m/%Y")]
        ]
        meta_table = Table(meta_data, colWidths=[1.5*inch, 1.75*inch, 1.25*inch, 2*inch])
        meta_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e1f5fe')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e1f5fe')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Instructions
        story.append(Paragraph(f"<b>निर्देश:</b> {assessment['instructions']}", self.styles['Instructions']))
        story.append(Spacer(1, 0.2*inch))
        
        # Questions
        for q in assessment['questions']:
            q_text = f"<b>प्रश्न {q['question_number']}.</b> {q['question']} <i>(2 अंक)</i>"
            story.append(Paragraph(q_text, self.styles['Question']))
            story.append(Paragraph(f"<i>कठिनाई: {q['difficulty']} | कौशल: {q['skill']}</i>", self.styles['Meta']))
            story.append(Spacer(1, 0.4*inch))
        
        doc.build(story)
        print(f"[OK] Assessment PDF generated: {filename}", flush=True)
        return filename
    
    def generate_assignment_pdf(self, assignment: Dict, filename: str) -> str:
        """Generate assignment PDF with enhanced formatting"""
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch)
        story = []
        
        # Title
        story.append(Paragraph(f"📚 {assignment['title']}", self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        meta_data = [
            ["कक्षा:", assignment['grade'], "विषय:", assignment['topic']],
            ["कुल प्रश्न:", str(assignment['total_questions']), "जमा करने की तारीख:", assignment['due_date']]
        ]
        meta_table = Table(meta_data, colWidths=[1.5*inch, 1.75*inch, 2*inch, 2.25*inch])
        meta_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#fff3e0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Learning objective
        story.append(Paragraph(f"<b>सीखने का उद्देश्य:</b> {assignment['learning_objective']}", self.styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        # Instructions
        story.append(Paragraph(f"<b>निर्देश:</b> {assignment['instructions']}", self.styles['Instructions']))
        story.append(Spacer(1, 0.2*inch))
        
        # Sections
        for section in assignment['sections']:
            story.append(Paragraph(section['section_title'], self.styles['Heading1']))
            story.append(Paragraph(section['section_instructions'], self.styles['Meta']))
            story.append(Spacer(1, 0.1*inch))
            
            # Problems
            if 'problems' in section:
                for problem in section['problems']:
                    p_text = f"<b>{problem['problem_number']}.</b> {problem['question']}"
                    story.append(Paragraph(p_text, self.styles['Question']))
                    
                    if 'answer_space' in problem and problem['answer_space']:
                        story.append(Paragraph(problem['answer_space'], self.styles['Normal']))
                    
                    if 'work_space' in problem:
                        story.append(Paragraph(problem['work_space'], self.styles['Normal']))
                        story.append(Spacer(1, 0.5*inch))  # Space for work
                    else:
                        story.append(Spacer(1, 0.3*inch))
            
            # Creative activity
            elif 'activity_description' in section:
                story.append(Paragraph(f"<b>गतिविधि:</b> {section['activity_description']}", self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(f"<b>उदाहरण:</b> {section['example']}", self.styles['Meta']))
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(section['instruction'], self.styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)
        print(f"[OK] Assignment PDF generated: {filename}", flush=True)
        return filename
    
    def generate_lesson_plan_pdf(self, lesson_plan: Dict, filename: str) -> str:
        """Generate lesson plan PDF for teachers"""
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch)
        story = []
        
        # Title
        story.append(Paragraph(f"👨‍🏫 {lesson_plan['title']}", self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        meta_text = f"""
        <b>कक्षा:</b> {lesson_plan['grade']} | <b>विषय:</b> {lesson_plan['topic']}<br/>
        <b>अवधि:</b> {lesson_plan['duration']} | <b>NIPUN संदर्भ:</b> {lesson_plan['nipun_reference']}
        """
        story.append(Paragraph(meta_text, self.styles['Meta']))
        story.append(Spacer(1, 0.15*inch))
        
        # Learning objective
        story.append(Paragraph(f"<b>सीखने का उद्देश्य:</b> {lesson_plan['learning_objective']}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Materials needed
        story.append(Paragraph("🎒 आवश्यक सामग्री:", self.styles['Heading1']))
        materials_list = ListFlowable(
            [ListItem(Paragraph(mat, self.styles['Normal']), bulletColor=colors.HexColor('#ff6f00'))
             for mat in lesson_plan['materials_needed']],
            bulletType='bullet'
        )
        story.append(materials_list)
        story.append(Spacer(1, 0.2*inch))
        
        # Lesson structure
        story.append(Paragraph("📖 पाठ की संरचना:", self.styles['Heading1']))
        
        for phase_name, phase_data in lesson_plan['lesson_structure'].items():
            phase_title = {
                'introduction': '1. परिचय (Introduction)',
                'main_teaching': '2. मुख्य शिक्षण (Main Teaching)',
                'guided_practice': '3. मार्गदर्शित अभ्यास (Guided Practice)',
                'independent_practice': '4. स्वतंत्र अभ्यास (Independent Practice)',
                'closure': '5. समापन (Closure)'
            }.get(phase_name, phase_name)
            
            story.append(Paragraph(f"{phase_title} - {phase_data['duration']}", self.styles['Heading2']))
            
            activities_list = ListFlowable(
                [ListItem(Paragraph(act, self.styles['Normal']), bulletColor=colors.HexColor('#1976d2'))
                 for act in phase_data['activities']],
                bulletType='bullet'
            )
            story.append(activities_list)
            
            if 'example' in phase_data:
                story.append(Paragraph(f"<i>{phase_data['example']}</i>", self.styles['Meta']))
            
            if 'teaching_points' in phase_data:
                story.append(Paragraph("<b>मुख्य बिंदु:</b>", self.styles['Normal']))
                points_list = ListFlowable(
                    [ListItem(Paragraph(pt, self.styles['Normal']), bulletColor=colors.HexColor('#388e3c'))
                     for pt in phase_data['teaching_points']],
                    bulletType='bullet'
                )
                story.append(points_list)
            
            story.append(Spacer(1, 0.15*inch))
        
        # Assessment strategies
        story.append(PageBreak())
        story.append(Paragraph("📊 मूल्यांकन रणनीतियाँ:", self.styles['Heading1']))
        
        for assess_type, strategies in lesson_plan['assessment_strategies'].items():
            type_title = {
                'formative_assessment': 'निर्माणात्मक मूल्यांकन:',
                'summative_assessment': 'योगात्मक मूल्यांकन:',
                'observation_points': 'अवलोकन बिंदु:'
            }.get(assess_type, assess_type)
            
            story.append(Paragraph(type_title, self.styles['Heading2']))
            strategies_list = ListFlowable(
                [ListItem(Paragraph(s, self.styles['Normal']))
                 for s in strategies],
                bulletType='bullet'
            )
            story.append(strategies_list)
            story.append(Spacer(1, 0.1*inch))
        
        # Differentiation
        story.append(PageBreak())
        story.append(Paragraph("🎯 विभेदन युक्तियाँ (Differentiation):", self.styles['Heading1']))
        
        for learner_type, tips_data in lesson_plan['differentiation_tips'].items():
            story.append(Paragraph(tips_data['title'], self.styles['Heading2']))
            tips_list = ListFlowable(
                [ListItem(Paragraph(tip, self.styles['Normal']))
                 for tip in tips_data['tips']],
                bulletType='bullet'
            )
            story.append(tips_list)
            story.append(Spacer(1, 0.15*inch))
        
        # Homework
        story.append(Paragraph("📝 होमवर्क सुझाव:", self.styles['Heading2']))
        story.append(Paragraph(lesson_plan['homework_suggestion'], self.styles['Normal']))
        
        doc.build(story)
        print(f"[OK] Lesson plan PDF generated: {filename}", flush=True)
        return filename
    
    def generate_study_guide_pdf(self, study_guide: Dict, filename: str) -> str:
        """Generate study guide PDF for students"""
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch)
        story = []
        
        # Title
        story.append(Paragraph(f"📖 {study_guide['title']}", self.styles['Title']))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        story.append(Paragraph(f"<b>कक्षा:</b> {study_guide['grade']} | <b>विषय:</b> {study_guide['topic']}", self.styles['Meta']))
        story.append(Spacer(1, 0.15*inch))
        
        # Learning objective
        story.append(Paragraph(f"<b>सीखने का उद्देश्य:</b> {study_guide['learning_objective']}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Key concepts
        story.append(Paragraph("🔑 मुख्य अवधारणाएं (Key Concepts):", self.styles['Heading1']))
        for concept in study_guide['key_concepts']:
            story.append(Paragraph(f"{concept['emoji']} <b>{concept['concept']}</b>", self.styles['Heading2']))
            story.append(Paragraph(concept['explanation'], self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Examples
        story.append(Paragraph("💡 उदाहरण (Examples):", self.styles['Heading1']))
        for example in study_guide['examples']:
            story.append(Paragraph(f"• {example}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Practice tips
        story.append(Paragraph("✍️ अभ्यास युक्तियाँ (Practice Tips):", self.styles['Heading1']))
        tips_list = ListFlowable(
            [ListItem(Paragraph(tip, self.styles['Normal']))
             for tip in study_guide['practice_tips']],
            bulletType='bullet'
        )
        story.append(tips_list)
        story.append(Spacer(1, 0.2*inch))
        
        # Common mistakes
        story.append(PageBreak())
        story.append(Paragraph("⚠️ सामान्य गलतियाँ और समाधान:", self.styles['Heading1']))
        for mistake in study_guide['common_mistakes']:
            story.append(Paragraph(mistake['mistake'], self.styles['Normal']))
            story.append(Paragraph(mistake['solution'], self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Quick revision
        story.append(Paragraph("⚡ त्वरित पुनरावलोकन (Quick Revision):", self.styles['Heading1']))
        revision_list = ListFlowable(
            [ListItem(Paragraph(point, self.styles['Normal']))
             for point in study_guide['quick_revision']],
            bulletType='bullet'
        )
        story.append(revision_list)
        
        doc.build(story)
        print(f"[OK] Study guide PDF generated: {filename}", flush=True)
        return filename

