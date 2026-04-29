"""
Code Optimizer Package
Multi-language code optimization tool
"""

from .analyzer import CodeAnalyzer
from .optimizations import CodeOptimizer, LanguageSpecificOptimizer
from .language_detector import LanguageDetector, LanguageValidator
from .simulator import CodeSimulator
from .ast_utils import parse_assignment, parse_expression

__all__ = [
    'CodeAnalyzer',
    'CodeOptimizer',
    'LanguageSpecificOptimizer',
    'LanguageDetector',
    'LanguageValidator',
    'CodeSimulator',
    'parse_assignment',
    'parse_expression'
]
