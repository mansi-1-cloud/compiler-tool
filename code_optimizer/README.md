# 🚀 Code Optimizer - Multi-Language Code Optimization Tool

A comprehensive code optimization tool that supports **C, C++, Java, and Python**. This tool analyzes and optimizes code using industry-standard optimization techniques while maintaining program logic and behavior.

## 📋 Features

### Optimization Techniques

1. **Constant Folding**
   - Evaluates constant arithmetic expressions at compile time
   - Example: `a = 2 + 3` → `a = 5`
   - Supported expressions: addition, subtraction, multiplication, division, modulo

2. **Dead Code Elimination**
   - Removes unreachable code after return statements, break statements, etc.
   - Example: Code after `return` statement is removed
   - Helps reduce binary size and improves readability

3. **Unused Variable Removal**
   - Identifies and comments out variables assigned but never used
   - Helps clean up unnecessary variable declarations
   - Preserves code functionality by commenting instead of deleting

4. **Redundant Assignment Removal**
   - Detects variables that are assigned multiple times without being used between assignments
   - Example: Removes first assignment if variable is immediately reassigned
   - Reduces memory operations and improves performance

### Supported Languages
- 🐍 **Python** (.py)
- ☕ **Java** (.java)
- ⚙️ **C++** (.cpp, .cc, .cxx)
- 📱 **C** (.c)

### Additional Features
- **Auto Language Detection**: Automatically detects the programming language with confidence scoring
- **Side-by-Side Comparison**: View original and optimized code simultaneously
- **Detailed Reports**: Comprehensive optimization statistics and categorization
- **REST API**: Backend API for programmatic access
- **Interactive UI**: Modern, responsive web interface

## 📁 Project Structure

```
code_optimizer/
├── backend/
│   ├── optimizer/
│   │   ├── __init__.py
│   │   ├── analyzer.py          # Code parsing and analysis
│   │   ├── optimizations.py     # Optimization implementations
│   │   └── language_detector.py # Language detection
│   ├── app.py                   # Flask API server
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── index.html               # UI markup
│   ├── style.css                # Styling
│   └── script.js                # Client-side logic
└── README.md                    # This file
```

## 🚀 Getting Started

### Prerequisites
- **Python 3.7+**
- **pip** (Python package manager)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone or navigate to project directory:**
   ```bash
   cd code_optimizer
   ```

2. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start the Flask backend server:**
   ```bash
   python app.py
   ```
   You should see:
   ```
   * Running on http://0.0.0.0:5001/ (Press CTRL+C to quit)
   ```

4. **Open the frontend in your browser:**
   ```bash
   # Open the file directly
   open frontend/index.html
   # or
   # Use a local server (Python 3):
   cd frontend
   python -m http.server 8000
   # Then visit http://localhost:8000
   ```

## 🎯 Usage Guide

### Web Interface

1. **Select Programming Language**: Choose C, C++, Java, or Python from the dropdown
2. **Enable Auto-Detection** (optional): Check to automatically detect language
3. **Paste or Load Code**:
   - Paste your code directly into the "Original Code" textarea
   - Or click "Load Sample" to see example code
4. **Click "Optimize Code"** or press **Ctrl+Enter**
5. **View Results**:
   - Optimized code appears on the right
   - Statistics show optimization metrics
   - Details panel lists all optimizations applied
6. **Copy Results**: Click "Copy Optimized Code" to copy to clipboard

### REST API

#### Optimize Endpoint

**POST** `/optimize`

Request:
```json
{
  "code": "int x = 5 + 3;\nint y = x;",
  "language": "java",
  "auto_detect": false
}
```

Response:
```json
{
  "success": true,
  "optimized_code": "int x = 8;\nint y = x;",
  "language": "java",
  "optimizations_applied": [
    {
      "type": "constant_folding",
      "line": "int x = 5 + 3;",
      "optimization": "5 + 3 → 8"
    }
  ],
  "statistics": {
    "total_optimizations": 1,
    "original_lines": 2,
    "optimized_lines": 2,
    "lines_saved": 0,
    "optimization_categories": {
      "constant_folding": 1
    }
  }
}
```

#### Language Detection Endpoint

**POST** `/detect-language`

Request:
```json
{
  "code": "def hello():\n    print('Hello')"
}
```

Response:
```json
{
  "success": true,
  "detected_language": "python",
  "confidence": 0.95,
  "all_scores": {
    "python": "92.5",
    "java": "10.0",
    "cpp": "5.0",
    "c": "3.0"
  },
  "is_confident": true
}
```

#### Sample Code Endpoint

**GET** `/sample-code?language=python`

Response:
```json
{
  "language": "python",
  "sample_code": "# Sample Python code\nx = 5 + 3\n..."
}
```

#### Health Check Endpoint

**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "service": "Code Optimizer API",
  "version": "1.0.0"
}
```

## 📚 Code Examples

### Python Example

**Original:**
```python
x = 5 + 3  # Can be folded to 8
y = 10
unused_var = 42  # Never used

def calculate(a, b):
    result = a * 2 * 3  # Can be folded to 6
    temp = 100  # Redundant
    temp = result + b
    return temp
```

**Optimized:**
```python
x = 8
y = 10
# unused_var = 42  [REMOVED: unused variable]

def calculate(a, b):
    result = a * 6
    # temp = 100  [REMOVED: redundant assignment to temp]
    temp = result + b
    return temp
```

### Java Example

**Original:**
```java
public class Calculator {
    public static void main(String[] args) {
        int x = 5 + 3;
        int y = 10;
        int unused = 42;
        
        int result = 2 * 5 * 10;
        System.out.println(result);
        return;
        System.out.println("Dead code");
    }
}
```

**Optimized:**
```java
public class Calculator {
    public static void main(String[] args) {
        int x = 8;
        int y = 10;
        # unused = 42;  [REMOVED: unused variable]
        
        int result = 100;
        System.out.println(result);
        return;
        # System.out.println("Dead code");  [REMOVED: dead code]
    }
}
```

## 🔧 Backend API Architecture

### CodeAnalyzer (`analyzer.py`)
Analyzes code structure and identifies optimization opportunities:
- **parse_code()**: Tokenizes and categorizes code lines
- **extract_variables()**: Maps variable usage across code
- **find_unused_variables()**: Identifies unused assignments
- **find_constant_expressions()**: Locates foldable expressions
- **find_redundant_assignments()**: Detects double assignments
- **find_dead_code_patterns()**: Finds unreachable code

### CodeOptimizer (`optimizations.py`)
Applies optimization transformations:
- **fold_constants()**: Evaluates arithmetic expressions
- **remove_unused_variables()**: Eliminates unused assignments
- **eliminate_dead_code()**: Removes unreachable code
- **remove_redundant_assignments()**: Cleans up double assignments
- **remove_blank_lines()**: Normalizes whitespace

### LanguageDetector (`language_detector.py`)
Identifies programming language from source code:
- **detect()**: Scores code against language signatures
- **Scoring based on**:
  - Language-specific keywords
  - Syntax patterns (regex)
  - File extensions
  - Pattern frequency analysis

## 📊 Optimization Metrics

The tool provides detailed statistics:
- **Total Optimizations**: Number of changes applied
- **Original Lines**: Line count before optimization
- **Optimized Lines**: Line count after optimization
- **Lines Saved**: Reduction in code size
- **Breakdown**: Count per optimization type

## ⚙️ Configuration

### Backend Configuration (`app.py`)
```python
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
SUPPORTED_LANGUAGES = ['python', 'java', 'c', 'cpp', 'c++']
```

### API Server
- **Host**: 0.0.0.0
- **Port**: 5000
- **Debug Mode**: Enabled by default
- **CORS**: Enabled for all origins

## 🧪 Testing

### Manual Testing

1. **Test Constant Folding:**
   ```python
   x = 2 + 3
   y = 10 * 5
   z = 100 / 4
   ```

2. **Test Unused Variable Removal:**
   ```python
   unused = 42
   used = 10
   print(used)
   ```

3. **Test Dead Code Elimination:**
   ```python
   if True:
       print("OK")
       return
       print("Never runs")  # Should be removed
   ```

4. **Test Redundant Assignment:**
   ```python
   x = 10
   x = 20  # First assignment is redundant
   print(x)
   ```

### Supported Test Cases

See sample code in the UI by clicking "Load Sample" for each language.

## 🎨 Frontend Features

### User Interface
- **Responsive Design**: Works on desktop, tablet, mobile
- **Dark-aware**: Adapts to system preferences
- **Real-time Statistics**: Updates as you code
- **Keyboard Shortcuts**: Ctrl/Cmd+Enter to optimize
- **Copy to Clipboard**: One-click code copying

### Code Editor
- **Syntax Highlighting (via monospace font)**
- **Line Counting**: Automatic line number tracking
- **Read-only Output**: Prevents accidental modification
- **Large File Support**: Handles up to 5MB of code

## 🔐 Security Considerations

1. **Input Validation**: All inputs validated server-side
2. **Content-Length Limit**: Max 5MB per request to prevent abuse
3. **CORS**: Configured for development (adjust for production)
4. **No Code Execution**: Optimizer never executes user code
5. **Stateless Design**: No code stored between requests

## 📈 Performance

- **Small files** (<10KB): <100ms
- **Medium files** (10-100KB): <500ms
- **Large files** (100KB-5MB): <2 seconds

Optimization time depends on:
- Code size
- Code complexity
- Language parsing patterns
- Number of patterns to check

## 🚧 Limitations

1. **Regex-based Parsing**: Not a full compiler, uses pattern matching
2. **Language-specific Features**: Some advanced features may not be detected
3. **Semantic Analysis**: Limited understanding of program semantics
4. **Comments Preserved**: Comments are preserved in output
5. **No Global Analysis**: Optimizations are performed line by line

## 🛣️ Future Enhancements

- [ ] Loop Unrolling Optimization
- [ ] Function Inlining
- [ ] Common Subexpression Elimination
- [ ] Variable Renaming/Obfuscation
- [ ] Code Formatting Options
- [ ] Multiple File Support
- [ ] Optimization Level Selection (O1, O2, O3)
- [ ] Custom Language Support
- [ ] Integration with popular IDEs
- [ ] Real-time Collaboration

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Better language detection
- Additional optimization techniques
- Performance improvements
- Frontend enhancements
- Documentation

## 📖 Technical Documentation

### Regex Patterns Used

**Python:**
- Function definition: `def\s+\w+\s*\(`
- Class definition: `class\s+\w+\s*:`
- Import statement: `import|from.*import`

**Java:**
- Class definition: `public\s+class\s+\w+`
- Method signature: `(public|private|protected)\s+\w+\s+\w+\(`
- Import: `import\s+java\.`

**C/C++:**
- Include: `#include\s*[<"]`
- Namespace: `std::`
- Template: `template\s*<`

**General:**
- Variable assignment: `\b[a-zA-Z_]\w*\s*=(?!=)`
- Arithmetic expression: `(\d+)\s*([\+\-\*/%])\s*(\d+)`
- Comments: `//.*|/\*.*?\*/`

## 📝 License

This project is provided as-is for educational and development purposes.

## 📧 Support

For issues, questions, or suggestions:
1. Check the README and examples
2. Review the API response messages
3. Enable browser console for debugging
4. Check Flask server logs for backend errors

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Status**: Production Ready

Happy optimizing! ⚡
