#!/usr/bin/env python3
"""
Test script for Code Optimizer components
Tests analyzer, optimizations, and language detector
"""

import sys
sys.path.insert(0, '/Users/vaibhavrawat/compiler/code_optimizer/backend')

from optimizer.analyzer import CodeAnalyzer
from optimizer.optimizations import CodeOptimizer
from optimizer.language_detector import LanguageDetector

def test_constant_folding():
    """Test constant folding optimization"""
    print("\n" + "="*60)
    print("TEST 1: Constant Folding")
    print("="*60)
    
    code = """x = 2 + 3
y = 10 * 5
z = 100 / 4
result = x + y + z"""
    
    print("Original code:")
    print(code)
    
    optimizer = CodeOptimizer('python')
    result = optimizer.optimize(code)
    
    print("\nOptimized code:")
    print(result['optimized_code'])
    
    print(f"\nOptimizations applied: {result['count']}")
    for opt in result['optimizations_applied']:
        print(f"  - {opt}")

def test_unused_variable_removal():
    """Test unused variable removal"""
    print("\n" + "="*60)
    print("TEST 2: Unused Variable Removal")
    print("="*60)
    
    code = """unused = 42
x = 10
print(x)"""
    
    print("Original code:")
    print(code)
    
    analyzer = CodeAnalyzer('python')
    analyzer.parse_code(code)
    unused = analyzer.find_unused_variables()
    
    print(f"\nUnused variables detected: {unused}")
    
    optimizer = CodeOptimizer('python')
    result = optimizer.optimize(code)
    
    print("\nOptimized code:")
    print(result['optimized_code'])

def test_dead_code_elimination():
    """Test dead code elimination"""
    print("\n" + "="*60)
    print("TEST 3: Dead Code Elimination")
    print("="*60)
    
    code = """def test():
    if True:
        print("OK")
        return 42
        print("Never runs")"""
    
    print("Original code:")
    print(code)
    
    optimizer = CodeOptimizer('python')
    result = optimizer.optimize(code)
    
    print("\nOptimized code:")
    print(result['optimized_code'])

def test_language_detection():
    """Test language detection"""
    print("\n" + "="*60)
    print("TEST 4: Language Detection")
    print("="*60)
    
    # Test Python
    python_code = """def hello():
    print('Hello World')
    
if __name__ == '__main__':
    hello()"""
    
    detector = LanguageDetector()
    lang, confidence = detector.detect(python_code)
    print(f"\nPython code detected as: {lang} (confidence: {confidence:.2f})")
    
    # Test Java
    java_code = """public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}"""
    
    lang, confidence = detector.detect(java_code)
    print(f"Java code detected as: {lang} (confidence: {confidence:.2f})")
    
    # Test C++
    cpp_code = """#include <iostream>
using namespace std;

int main() {
    cout << "Hello World" << endl;
    return 0;
}"""
    
    lang, confidence = detector.detect(cpp_code)
    print(f"C++ code detected as: {lang} (confidence: {confidence:.2f})")

def test_complete_optimization():
    """Test complete optimization pipeline"""
    print("\n" + "="*60)
    print("TEST 5: Complete Optimization Pipeline")
    print("="*60)
    
    code = """x = 5 + 3
y = 10
unused_var = 42

def calculate(a, b):
    result = a * 2 * 3
    temp = 100
    temp = result + b
    return temp
    print("unreachable")

print(calculate(5, 10))"""
    
    print("Original code:")
    print(code)
    print(f"Lines: {len(code.split(chr(10)))}")
    
    optimizer = CodeOptimizer('python')
    result = optimizer.optimize(code)
    report = optimizer.get_optimization_report(code, result['optimized_code'])
    
    print("\nOptimized code:")
    print(result['optimized_code'])
    print(f"Lines: {len(result['optimized_code'].split(chr(10)))}")
    
    print("\nOptimization Report:")
    print(f"  Total optimizations: {report['total_optimizations']}")
    print(f"  Original lines: {report['original_lines']}")
    print(f"  Optimized lines: {report['optimized_lines']}")
    print(f"  Lines saved: {report['lines_saved']}")
    print(f"  Breakdown:")
    for category, count in report['optimization_categories'].items():
        print(f"    - {category}: {count}")

def main():
    """Run all tests"""
    print("\n" + "🧪 CODE OPTIMIZER TEST SUITE 🧪".center(60))
    
    try:
        test_constant_folding()
        test_unused_variable_removal()
        test_dead_code_elimination()
        test_language_detection()
        test_complete_optimization()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
