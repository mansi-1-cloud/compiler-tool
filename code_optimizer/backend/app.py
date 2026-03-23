"""
Flask Backend API
Multi-Language Code Optimization Tool API Server

Endpoints:
    POST /optimize - Optimize source code
    GET /health - Server health check
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
SUPPORTED_LANGUAGES = ['java', 'c', 'cpp', 'c++']


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
        "language": "java|c|cpp|c++",
        "extension": ".java" (optional)
    }
    
    Response JSON:
    {
        "success": true,
        "optimized_code": "optimized code string",
        "language": "detected language",
        "optimizations_applied": [
            {
                "type": "constant_folding",
                "line_number": 5,
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
        language = request.json.get('language', 'java').lower()
        file_extension = request.json.get('extension', '').lower()
        
        # Validate code
        if not code:
            return jsonify({
                'success': False,
                'error': 'Code cannot be empty'
            }), 400
        
        # Detect language from extension if provided
        if file_extension:
            ext_map = {
                '.java': 'java',
                '.cpp': 'cpp',
                '.cc': 'cpp',
                '.cxx': 'cpp',
                '.c': 'c',
                '.h': 'c'
            }
            if file_extension in ext_map:
                language = ext_map[file_extension]
        
        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            return jsonify({
                'success': False,
                'error': f'Unsupported language: {language}. Supported: {", ".join(SUPPORTED_LANGUAGES)}'
            }), 400
        
        # Perform optimization
        optimizer = CodeOptimizer(language)
        result = optimizer.optimize(code)
        
        # Generate report
        report = optimizer.get_optimization_report(code, result['optimized_code'])
        
        return jsonify({
            'success': True,
            'optimized_code': result['optimized_code'],
            'language': language,
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


@app.route('/supported-languages', methods=['GET'])
def supported_languages():
    """Get list of supported languages"""
    return jsonify({
        'supported_languages': SUPPORTED_LANGUAGES,
        'optimizations': [
            'constant_folding',
            'dead_code_elimination',
            'redundant_assignment_removal',
            'algebraic_simplification',
            'loop_invariant_code_motion',
            'unused_variable_removal',
            'loop_elimination',
            'function_inlining',
            'duplicate_call_removal'
        ]
    }), 200


@app.route('/sample-code', methods=['GET'])
def sample_code():
    """Get sample code for each language"""
    language = request.args.get('language', 'java').lower()
    
    samples = {
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
    
    code = samples.get(language, samples['java'])
    
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