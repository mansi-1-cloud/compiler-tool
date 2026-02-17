# 🚀 Quick Start Guide - Code Optimizer

## Prerequisites
- Python 3.7+
- pip
- Modern web browser

## Installation & Setup (2 minutes)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Start Backend Server
```bash
cd backend
python3 app.py
```
You'll see: `* Running on http://0.0.0.0:5001/`

### 3. Open Frontend
**Option A: Direct File**
```bash
open frontend/index.html
# or on Linux/Windows
# file:///path/to/code_optimizer/frontend/index.html
```

**Option B: Local Server**
```bash
cd frontend
python3 -m http.server 8000
# Visit http://localhost:8000
```

## Usage in 30 Seconds

1. **Select a language** (Python, Java, C++, C)
2. **Paste or load sample code** into the left panel
3. **Click "Optimize Code"** or press Ctrl+Enter
4. **View optimizations** on the right side
5. **Copy optimized code** if you want to use it

## Example

### Original Python Code
```python
x = 5 + 3
unused_var = 42
def calc(a):
    temp = 100
    temp = a + 10
    return temp
    print("unreachable")
calc(5)
```

### Optimized Code
```python
x = 8  # Constant folded
# unused_var = 42  [REMOVED: unused variable]
def calc(a):
    # temp = 100  [REMOVED: redundant assignment]
    temp = a + 10
    return temp
# print("unreachable")  [REMOVED: dead code]
calc(5)
```

## API Quick Reference

**Optimize Code**
```bash
curl -X POST http://localhost:5001/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = 2 + 3\ny = x",
    "language": "python"
  }'
```

**Detect Language**
```bash
curl -X POST http://localhost:5001/detect-language \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello():\n    print(\"Hi\")"}'
```

**Get Health Status**
```bash
curl http://localhost:5001/health
```

**Get Supported Languages**
```bash
curl http://localhost:5001/supported-languages
```

**Get Sample Code**
```bash
curl "http://localhost:5001/sample-code?language=python"
```

## Troubleshooting

**Port 5001 already in use?**
- Edit `backend/app.py` and change port = 5001 to another port
- Edit `frontend/script.js` and update API_BASE_URL

**Backend not responding?**
- Make sure Flask server is running: `cd backend && python3 app.py`
- Check that port 5001 is open
- Try `curl http://localhost:5001/health`

**No optimizations found?**
- Some code may already be optimized
- Try the "Load Sample" button for examples with many optimizations

**Language detection not working?**
- Detection works best with clear language patterns
- Use "Select Language" dropdown instead
- Enable "Auto-detect" checkbox to have the tool guess

## Features at a Glance

✨ **4 Optimization Techniques:**
1. Constant Folding (2+3 → 5)
2. Dead Code Elimination (code after return)
3. Unused Variable Removal
4. Redundant Assignment Removal

🌍 **4 Programming Languages:**
- Python
- Java
- C++
- C

📊 **Detailed Reports:**
- Optimization statistics
- Category breakdown
- Before/after comparison
- Line count metrics

## Project Files

```
code_optimizer/
├── backend/
│   ├── optimizer/
│   │   ├── analyzer.py      # Code analysis engine
│   │   ├── optimizations.py # Optimization techniques
│   │   └── language_detector.py
│   ├── app.py               # Flask API server
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Web interface
│   ├── style.css            # Styling
│   └── script.js            # Client logic
├── test_backend.py          # Test suite
├── start.sh                 # Quick start script
├── README.md                # Full documentation
└── QUICKSTART.md            # This file
```

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🧪 Run tests: `python3 test_backend.py`
- 🔧 Modify optimizations in `backend/optimizer/optimizations.py`
- 🎨 Customize UI in `frontend/style.css`

## Common Tasks

**Test a specific optimization:**
```bash
cd backend
python3 test_backend.py
```

**Change the backend port:**
Edit `backend/app.py`, find `port=5001`, change to desired port
Edit `frontend/script.js`, find `API_BASE_URL`, update port

**Add a new optimization:**
1. Add detection method in `analyzer.py`
2. Add optimization method in `optimizations.py`
3. Call it from `optimize()` method in CodeOptimizer class

**Support a new language:**
1. Add language patterns to `LanguageDetector.SIGNATURES`
2. Add parsing logic to `CodeAnalyzer` if needed
3. Test with sample code

## Tips & Tricks

- Use **Ctrl+Enter** to quickly optimize code
- **Double-paste** to compare original vs optimized side-by-side
- Enable **Auto-detect** for mixed-language files
- Check **Optimization Details** panel for explanations
- Use **Load Sample** to learn what optimizations are possible

## Performance Notes

- Small files (<10KB): <100ms
- Medium files (10-100KB): <500ms  
- Large files (100KB-5MB): <2s

## Questions?

See the full [README.md](README.md) for:
- API endpoint documentation
- Code examples
- Architecture details
- Troubleshooting guide
- Future enhancements

---

**Happy optimizing!** ⚡ Last updated: February 2026
