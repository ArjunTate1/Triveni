# NIPUN Offline Learning Material Generator

**🔴 100% OFFLINE | NO INTERNET REQUIRED | NO AI MODEL | NO CLOUD SERVICES**

An offline, lightweight, rule-based NIPUN/FLN (Foundational Literacy and Numeracy) curriculum mapping and learning-material generation engine.

---

## ✨ Key Features

- ✅ **Completely Offline** - Works without internet connection
- ✅ **No External APIs** - No OpenAI, Gemini, or any cloud service
- ✅ **Rule-Based NLP** - Lightweight Hindi text processing
- ✅ **Local Knowledge Base** - All NIPUN data stored locally in JSON
- ✅ **Template-Based Generation** - Activities, worksheets, flashcards, assessments
- ✅ **Hindi/Devanagari Support** - PDF generation with Unicode fonts
- ✅ **Low Resource** - Designed for 2GB RAM devices
- ✅ **Privacy First** - No data sent anywhere

---

## 🎯 What It Does

1. **Analyze** Hindi curriculum text using rule-based NLP
2. **Detect** domain (Literacy/Numeracy), topics, and skills
3. **Map** to NIPUN/FLN learning outcomes
4. **Generate** learning materials:
   - Activities (गतिविधियाँ)
   - Worksheets (वर्कशीट)
   - Flashcards (फ्लैशकार्ड)
   - Assessments (मूल्यांकन)
5. **Export** as PDF with Hindi support

---

## 📋 System Requirements

- **Operating System**: Windows, Linux, or macOS
- **Python**: 3.8 or higher
- **RAM**: Minimum 512 MB (designed for 2GB target)
- **Storage**: ~50 MB for application + data
- **Internet**: **NOT REQUIRED** at runtime

---

## 🚀 Installation

### Step 1: Install Python
Ensure Python 3.8+ is installed:
```bash
python --version
```

### Step 2: Navigate to Project Directory
```bash
cd F:/nipun-offline
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies Explanation:**
- `fastapi` (0.104.1) - Lightweight web framework for local API server
- `uvicorn` (0.24.0) - ASGI server to run FastAPI locally
- `reportlab` (4.0.7) - PDF generation library with Unicode support
- `pytest` (7.4.3) - Testing framework (development only)

**Total size**: ~15 MB
**No heavy ML libraries** - No PyTorch, TensorFlow, or Transformers

---

## 🏃 Running the Application

### Terminal Prototype (Recommended for MVP)
```bash
cd F:/nipun-offline
python cli_prototype.py
```

This runs the complete application in your terminal - **no web browser needed**.

### Web Interface (Optional - for future)
If you want to use the web interface:
```bash
python -m app.main
```
Then open: http://127.0.0.1:8000

---

## 🧪 Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Run specific test:
```bash
python tests/test_analyzer.py
python tests/test_mapper.py
python tests/test_integration.py
```

---

## 🔌 OFFLINE VERIFICATION

### How to Verify It Works Offline

1. **Start the application**:
   ```bash
   python -m app.main
   ```

2. **Disconnect from the Internet**:
   - Turn off Wi-Fi
   - Disable mobile hotspot
   - Disconnect ethernet cable

3. **Open the application** in browser:
   ```
   http://127.0.0.1:8000
   ```

4. **Test the complete workflow**:
   - Enter Hindi curriculum text
   - Click "Analyze Curriculum"
   - View detected domain, topics, skills
   - View NIPUN mapping
   - Click "Generate All Materials"
   - View activities, worksheet, flashcards, assessment
   - Export PDFs

5. **Everything should work perfectly** without internet!

### Why It Works Offline

- ✅ FastAPI server runs on **localhost (127.0.0.1)** only
- ✅ All data stored in **local JSON files**
- ✅ No external API calls anywhere in the code
- ✅ Hindi fonts loaded from **system fonts**
- ✅ Frontend uses **vanilla JavaScript** (no CDN)
- ✅ No telemetry, analytics, or remote logging

---

## 📁 Project Structure

```
F:/nipun-offline/
│
├── app/                          # Application code
│   ├── main.py                   # FastAPI server (localhost only)
│   │
│   ├── api/                      # API endpoints (future expansion)
│   │   └── __init__.py
│   │
│   ├── services/                 # Core business logic
│   │   ├── curriculum_analyzer.py    # Rule-based Hindi NLP
│   │   ├── nipun_mapper.py           # Local outcome matching
│   │   ├── activity_generator.py     # Template-based activities
│   │   ├── worksheet_generator.py    # Worksheet generation
│   │   ├── flashcard_generator.py    # Flashcard generation
│   │   ├── assessment_generator.py   # Assessment generation
│   │   └── pdf_generator.py          # PDF export with Hindi
│   │
│   ├── models/                   # Data models
│   │   └── schemas.py            # Pydantic schemas
│   │
│   └── utils/                    # Utility functions
│       ├── hindi_text.py         # Hindi text processing
│       └── file_loader.py        # Local JSON file loader
│
├── data/                         # Local data (NO INTERNET)
│   ├── nipun/                    # NIPUN knowledge base
│   │   ├── balvatika.json        # Balvatika outcomes (DEMO)
│   │   ├── grade1.json           # Grade 1 outcomes (DEMO)
│   │   ├── grade2.json           # Grade 2 outcomes (DEMO)
│   │   └── grade3.json           # Grade 3 outcomes (DEMO)
│   │
│   ├── dictionaries/             # Hindi keyword dictionaries
│   │   ├── literacy_keywords.json
│   │   ├── numeracy_keywords.json
│   │   ├── topic_keywords.json
│   │   └── skill_keywords.json
│   │
│   └── templates/                # Content generation templates
│       ├── literacy_activities.json
│       ├── numeracy_activities.json
│       ├── worksheet_templates.json
│       ├── flashcard_templates.json
│       └── assessment_templates.json
│
├── assets/                       # Static assets
│   ├── images/                   # (Placeholder for future images)
│   └── fonts/                    # (Uses system fonts)
│
├── frontend/                     # Web interface
│   ├── index.html                # Main UI
│   ├── style.css                 # Styling
│   └── app.js                    # JavaScript (no CDN dependencies)
│
├── tests/                        # Test suite
│   ├── test_analyzer.py
│   ├── test_mapper.py
│   └── test_integration.py
│
├── requirements.txt              # Python dependencies (minimal)
├── config.json                   # Configuration
├── .gitignore                    # Git ignore file
└── README.md                     # This file
```

---

## 📝 Example Usage

### Test Input 1: Numeracy
```
Grade: Grade 1
Domain: (auto-detect)
Curriculum: बच्चे 1 से 10 तक की संख्याओं को पहचानेंगे और वस्तुओं को गिनेंगे।
```

**Expected Output:**
- Domain: Numeracy
- Topics: counting, numbers, number_recognition
- Skills: counting, number_recognition
- NIPUN Outcome: Matched with confidence
- Materials: Generated activities, worksheet, flashcards, assessment

### Test Input 2: Literacy
```
Grade: Grade 1
Domain: (auto-detect)
Curriculum: बच्चे अक्षरों को पहचानेंगे और उनसे बनने वाले सरल शब्दों को पढ़ेंगे।
```

**Expected Output:**
- Domain: Literacy
- Topics: letters, letter_recognition, word_reading
- Skills: letter_recognition, reading
- Materials: Generated learning materials

### Test Input 3: Comparison
```
Grade: Grade 1
Domain: Numeracy
Curriculum: बच्चे दो समूहों में वस्तुओं की संख्या की तुलना करेंगे।
```

**Expected Output:**
- Topics: comparison
- Skills: comparison, number_sense
- Materials: Comparison-focused activities

---

## 🔧 Replacing DEMO Data with Official NIPUN Data

The application currently uses **DEMO data** (clearly marked with "DEMO_" prefix in IDs).

### To Replace with Official NIPUN Bharat Data:

1. **Locate the data files**:
   ```
   F:/nipun-offline/data/nipun/
   ```

2. **Edit each JSON file** (balvatika.json, grade1.json, grade2.json, grade3.json)

3. **Replace DEMO records** with verified official NIPUN Bharat learning outcomes

4. **Maintain the JSON structure**:
   ```json
   {
     "id": "OFFICIAL_ID",
     "grade": "Grade 1",
     "domain": "Numeracy",
     "topic": "Numbers",
     "competency": "Official competency text in Hindi",
     "learning_outcome": "Official learning outcome in Hindi",
     "skills": ["skill1", "skill2"],
     "activity_types": ["activity_type1"],
     "assessment_types": ["assessment_type1"]
   }
   ```

5. **No code changes needed** - The application will automatically use the updated data

---

## 📱 Android Porting Plan

The application is designed for future Android deployment.

### Current Architecture (Windows/Laptop):
- FastAPI backend (localhost)
- HTML/CSS/JavaScript frontend
- Python services

### Android Migration Path:

1. **Core Logic** (Already portable):
   - `app/services/` modules are pure Python
   - No FastAPI dependency in business logic
   - Can be used as-is or rewritten in Kotlin/Java

2. **Options for Android**:

   **Option A: Python on Android (Kivy/BeeWare)**
   - Package Python code with Kivy
   - Keep existing logic
   - Bundle JSON data files
   - ~20 MB app size

   **Option B: Native Android**
   - Rewrite UI in Kotlin/Java
   - Port core logic to Kotlin
   - Use Android's JSON parsing
   - Use iText or similar for PDF generation
   - Better performance, smaller size

   **Option C: Hybrid (Webview)**
   - Keep HTML/CSS/JS frontend
   - Create lightweight Android WebView wrapper
   - Expose Python backend through Android service

3. **What Needs Changing**:
   - Remove FastAPI server (not needed on Android)
   - Replace file paths with Android storage paths
   - Bundle fonts in APK assets
   - Adapt PDF generation for Android filesystem

4. **What Stays the Same**:
   - All JSON data files
   - Hindi keyword dictionaries
   - Templates
   - Core algorithms (analyzer, mapper, generators)

---

## 💾 Memory Optimization

Designed for **2 GB RAM** devices:

### Current Optimizations:
- ✅ **Lazy loading**: JSON files loaded only when needed
- ✅ **No large models**: No ML models loaded into memory
- ✅ **Small data files**: Each JSON < 50 KB
- ✅ **Minimal dependencies**: Only 3 runtime libraries
- ✅ **Template caching**: FileLoader caches loaded templates
- ✅ **Grade-specific loading**: Only load relevant grade data

### Estimated Memory Usage:
- Base Python: ~20 MB
- FastAPI + Uvicorn: ~15 MB
- Application code: ~5 MB
- Loaded data (per grade): ~2 MB
- ReportLab: ~10 MB
- **Total: ~50-60 MB** (well under 2 GB target)

### Future Optimizations for Android:
- Compress JSON files
- Use SQLite for faster queries
- Lazy load templates on demand
- Release memory after PDF generation

---

## 🔒 Privacy & Security

- ✅ **No data transmission**: Nothing sent over the internet
- ✅ **No telemetry**: No usage tracking
- ✅ **No analytics**: No Google Analytics or similar
- ✅ **No external fonts**: Uses system fonts only
- ✅ **No CDN**: All resources bundled locally
- ✅ **Localhost only**: Server binds to 127.0.0.1
- ✅ **No API keys**: No configuration needed

---

## 🐛 Troubleshooting

### Issue: Server won't start
**Solution**: Check if port 8000 is already in use:
```bash
# Windows
netstat -ano | findstr :8000

# Change port
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### Issue: Hindi text not displaying in PDF
**Solution**: The app uses Windows system fonts. Ensure Mangal, Nirmala, or Kokila fonts are installed.

### Issue: "Module not found" error
**Solution**: Make sure you're in the correct directory:
```bash
cd F:/nipun-offline
python -m app.main
```

### Issue: "File not found" error
**Solution**: Check that all data files exist in F:/nipun-offline/data/

---

## 🤝 Contributing

This is a government education project. To contribute:

1. Keep the offline-first principle
2. No external APIs or cloud services
3. Maintain lightweight architecture
4. Test thoroughly before submitting
5. Document all changes

---

## 📄 License

This project is developed for educational purposes under NIPUN Bharat initiative.

---

## 📞 Support

For issues or questions, refer to the documentation or run the test suite to verify installation.

---

## ✅ Final Acceptance Checklist

Can you do this with the application?

- [ ] Install dependencies
- [ ] Disconnect from internet
- [ ] Start the application
- [ ] Enter Hindi curriculum text
- [ ] Click Analyze
- [ ] See detected domain/topic/skills
- [ ] See NIPUN/FLN mapping
- [ ] Click Generate
- [ ] Get activities
- [ ] Get a Hindi worksheet
- [ ] Get Hindi visual flashcards
- [ ] Get Hindi assessment
- [ ] Export all three as PDFs
- [ ] Everything works without internet

**If all boxes can be checked: ✅ Application is ready!**

---

**Built with ❤️ for NIPUN Bharat Initiative**

*Empowering foundational learning through offline technology*
