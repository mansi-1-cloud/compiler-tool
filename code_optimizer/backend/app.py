"""
Flask Backend API
Multi-Language Code Optimization Tool API Server

Endpoints:
    POST /optimize - Optimize source code
    GET /health - Server health check
    POST/detect-language - Detect code language
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add optimizer module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'optimizer'))

from optimizer import (
    CodeOptimizer,
    LanguageSpecificOptimizer,
    LanguageDetector,
    LanguageValidator
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload
SUPPORTED_LANGUAGES = ['python', 'java', 'c', 'cpp', 'c++']


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Code Optimizer API',
        'version': '1.0.0'
    }), 200


@app.route('/optimize', methods=['POST'])
def optimize():
    """
    Main optimization endpoint
    
    Request JSON:
    {
        "code": "source code string",
        "language": "python|java|c|cpp",
        "auto_detect": true (optional, default: false)
    }
    
    Response JSON:
    {
        "success": true,
        "optimized_code": "optimized code string",
        "language": "detected language",
        "optimizations_applied": [
            {
                "type": "constant_folding",
                "line": "original line",
                "optimization": "description"
            }
        ],
        "statistics": {
            "original_lines": 20,
            "optimized_lines": 18,
            "lines_saved": 2,
            "total_optimizations": 5
        }
    }
    """
    try:
        # Validate request
        if not request.json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        # Extract parameters
        code = request.json.get('code', '').strip()
        language = request.json.get('language', 'python').lower()
        auto_detect = request.json.get('auto_detect', False)
        
        # Validate code
        if not code:
            return jsonify({
                'success': False,
                'error': 'Code cannot be empty'
            }), 400
        
        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            return jsonify({
                'success': False,
                'error': f'Unsupported language: {language}. Supported: {", ".join(SUPPORTED_LANGUAGES)}'
            }), 400
        
        # Auto-detect language if requested
        if auto_detect:
            detector = LanguageDetector()
            detected_lang, confidence = detector.detect(code)
            
            if confidence > 0.6:
                language = detected_lang
                language_info = {
                    'detected_language': detected_lang,
                    'confidence': round(confidence, 2),
                    'original_language': request.json.get('language', 'unknown')
                }
            else:
                language_info = {
                    'detected_language': detected_lang,
                    'confidence': round(confidence, 2),
                    'original_language': request.json.get('language', 'unknown'),
                    'note': 'Low confidence, using specified or detected language'
                }
        else:
            language_info = {'specified_language': language}
        
        # Perform optimization
        optimizer = CodeOptimizer(language)
        result = optimizer.optimize(code)
        
        # Generate report
        report = optimizer.get_optimization_report(code, result['optimized_code'])
        
        return jsonify({
            'success': True,
            'optimized_code': result['optimized_code'],
            'language': language,
            'language_info': language_info,
            'optimizations_applied': result['optimizations_applied'],
            'statistics': {
                'total_optimizations': report['total_optimizations'],
                'original_lines': report['original_lines'],
                'optimized_lines': report['optimized_lines'],
                'lines_saved': report['lines_saved'],
                'optimization_categories': report['optimization_categories']
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Optimization failed: {str(e)}'
        }), 500


@app.route('/detect-language', methods=['POST'])
def detect_language():
    """
    Detect programming language from code
    
    Request JSON:
    {
        "code": "source code string",
        "user_language": "python" (optional)
    }
    
    Response JSON:
    {
        "success": true,
        "detected_language": "python",
        "confidence": 0.85,
        "all_scores": {
            "python": 92.5,
            "java": 10.0,
            ...
        },
        "recommendations": []
    }
    """
    try:
        if not request.json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        code = request.json.get('code', '').strip()
        user_language = request.json.get('user_language', None)
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'Code cannot be empty'
            }), 400
        
        # Detect language
        detector = LanguageDetector()
        detected_lang, confidence = detector.detect(code)
        
        # Get detailed info
        details = detector.get_detection_details()
        
        return jsonify({
            'success': True,
            'detected_language': detected_lang,
            'confidence': round(confidence, 2),
            'all_scores': details['scores_detailed'],
            'is_confident': detector.is_confident(0.6)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Language detection failed: {str(e)}'
        }), 500


@app.route('/supported-languages', methods=['GET'])
def supported_languages():
    """Get list of supported languages"""
    return jsonify({
        'supported_languages': SUPPORTED_LANGUAGES,
        'optimizations': [
            'constant_folding',
            'dead_code_elimination',
            'redundant_assignment_removal',
            'unused_variable_removal'
        ]
    }), 200


@app.route('/sample-code', methods=['GET'])
def sample_code():
    """Get sample code for each language"""
    language = request.args.get('language', 'python').lower()
    
    samples = {
        'python': '''# Sample Python code
x = 5 + 3  # Will be constant folded to 8
y = 10
unused_var = 42  # Unused variable

def calculate(a, b):
    result = a * 2 * 3  # Can be folded to 6
    temp = 100  # Redundant assignment
    temp = result + b
    return temp

print(calculate(5, 10))
''',
        'java': '''// Sample Java code
public class Calculator {
    public static void main(String[] args) {
        int x = 5 + 3;  // Will be constant folded to 8
        int y = 10;
        int unused = 42;  // Unused variable
        
        int result = 2 * 5 * 10;  // Can be folded
        System.out.println(result);
        return;
        System.out.println("Dead code");  // Unreachable
    }
}
''',
        'cpp': '''// Sample C++ code
#include <iostream>
using namespace std;

int main() {
    int x = 5 + 3;  // Will be constant folded to 8
    int y = 10;
    int unused = 42;  // Unused variable
    
    int result = 2 * 5 * 10;  // Can be folded
    cout << result << endl;
    
    return 0;
}
''',
        'c': '''// Sample C code
#include <stdio.h>

int main() {
    int x = 5 + 3;  // Will be constant folded to 8
    int y = 10;
    int unused = 42;  // Unused variable
    
    int result = 2 * 5 * 10;  // Can be folded
    printf("%d\\n", result);
    
    return 0;
}
'''
    }
    
    code = samples.get(language, samples['python'])
    
    return jsonify({
        'language': language,
        'sample_code': code
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Run Flask development server
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )
