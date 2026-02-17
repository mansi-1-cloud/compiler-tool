"""
Language Detector Module
Detects programming language from source code
Supports: C, C++, Java, Python
"""

import re
from typing import Tuple


class LanguageDetector:
    """Detects programming language from source code"""
    
    # Language signatures - unique patterns for each language
    SIGNATURES = {
        'python': {
            'keywords': ['def ', 'class ', 'import ', 'from ', 'if __name__', 'print(', 'self.'],
            'patterns': [
                r'^\s*def\s+\w+\s*\(',  # def keyword
                r'^\s*import\s+\w+',     # import statement
                r'^\s*from\s+\w+\s+import',  # from import
                r'^\s*class\s+\w+\s*:',  # class definition
                r'^\s*for\s+\w+\s+in\s+',  # for in loop
                r':\s*$',                # Line ends with colon (Python blocks)
                r'print\(',              # print function
            ],
            'file_extensions': ['.py'],
            'score_multiplier': 1.0
        },
        'java': {
            'keywords': ['public class', 'private', 'protected', 'void', 'static', 'import java', 'new', 'extends', 'implements'],
            'patterns': [
                r'^\s*public\s+class\s+\w+',  # public class
                r'^\s*(public|private|protected)\s+\w+\s+\w+\(',  # methods
                r'^\s*import\s+java\.',      # import java package
                r'new\s+\w+\(',              # new keyword
                r'@Override',                # annotations
                r':\s*\/\/'                  # // is rare in Python
            ],
            'file_extensions': ['.java'],
            'score_multiplier': 1.0
        },
        'cpp': {
            'keywords': ['#include', 'std::', 'template', 'class', 'public:', 'private:'],
            'patterns': [
                r'#include\s*[<"]',    # #include directive
                r'std::',               # std namespace
                r'using namespace',     # using namespace
                r'template\s*<',        # template
                r':\s*public',          # inheritance syntax
                r'->\s*\w+\s*{',        # lambda or function pointer
                r'::',                  # scope resolution
            ],
            'file_extensions': ['.cpp', '.cc', '.cxx', '.h'],
            'score_multiplier': 1.0
        },
        'c': {
            'keywords': ['#include', 'void', 'int', 'char', 'float', 'malloc', 'free', 'strlen', 'strcpy'],
            'patterns': [
                r'#include\s*[<"]',    # #include directive
                r'malloc\s*\(',        # malloc function
                r'free\s*\(',          # free function
                r'printf\s*\(',        # printf function
                r'scanf\s*\(',         # scanf function
                r'typedef\s+struct',   # typedef struct
                r'void\s+\*',          # void pointers
            ],
            'file_extensions': ['.c', '.h'],
            'score_multiplier': 0.95  # C and C++ signatures overlap
        }
    }
    
    def __init__(self):
        self.detected_language = None
        self.confidence = 0.0
        self.scores = {}
    
    def detect(self, code: str, file_extension: str = None) -> Tuple[str, float]:
        """
        Detect programming language from code
        
        Args:
            code: Source code string
            file_extension: Optional file extension (e.g., '.py', '.java')
            
        Returns:
            Tuple of (language, confidence_score)
            where confidence_score is between 0.0 and 1.0
        """
        self.scores = {}
        
        # If file extension provided, give it initial weight
        if file_extension:
            self._score_by_extension(file_extension)
        
        # Score each language
        for language, signature in self.SIGNATURES.items():
            score = self._calculate_score(code, language, signature)
            self.scores[language] = score
        
        # Find language with highest score
        if not self.scores:
            return 'python', 0.0
        
        max_score = max(self.scores.values())
        
        if max_score == 0:
            return 'python', 0.0
        
        # Normalize score to 0-1
        self.confidence = min(max_score / 100.0, 1.0)
        self.detected_language = max(self.scores, key=self.scores.get)
        
        return self.detected_language, self.confidence
    
    def _score_by_extension(self, extension: str):
        """Score languages by file extension"""
        extension = extension.lower()
        
        for language, signature in self.SIGNATURES.items():
            if extension in signature['file_extensions']:
                self.scores[language] = self.scores.get(language, 0) + 50
    
    def _calculate_score(self, code: str, language: str, signature: dict) -> float:
        """Calculate language score for given code"""
        score = 0.0
        lines = code.split('\n')
        code_lower = code.lower()
        
        # Score based on keywords
        keyword_matches = 0
        for keyword in signature['keywords']:
            count = code_lower.count(keyword.lower())
            keyword_matches += count
            score += count * 5  # 5 points per keyword
        
        # Score based on patterns
        pattern_matches = 0
        for pattern in signature['patterns']:
            try:
                matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
                pattern_matches += matches
                score += matches * 10  # 10 points per pattern match
            except re.error:
                pass
        
        # Boost score if multiple patterns match
        if pattern_matches > 0:
            score += pattern_matches * 5
        
        # Check against conflicting patterns for other languages
        score = self._apply_conflict_penalties(score, code, language)
        
        # Apply language-specific multiplier
        score *= signature['score_multiplier']
        
        return score
    
    def _apply_conflict_penalties(self, score: float, code: str, language: str) -> float:
        """Apply penalties for conflicting patterns"""
        code_lower = code.lower()
        
        # Python-specific penalties
        if language == 'python':
            if 'public class' in code_lower or 'new ' in code_lower:
                score -= 20  # Likely Java, not Python
            if '#include' in code_lower:
                score -= 20  # Likely C/C++, not Python
        
        # Java-specific penalties
        if language == 'java':
            if code_lower.count('def ') > code_lower.count('public'):
                score -= 20  # More Python-like
            if '#include' in code_lower:
                score -= 20  # C/C++ style
        
        # C/C++ penalties
        if language in ['c', 'cpp']:
            if 'def ' in code_lower:
                score -= 20  # Python style
            if 'public class' in code_lower:
                score -= 20  # Java style
        
        return max(score, 0)
    
    def get_detection_details(self) -> dict:
        """Get detailed detection information"""
        return {
            'detected_language': self.detected_language,
            'confidence': self.confidence,
            'all_scores': self.scores,
            'scores_detailed': {
                lang: f"{score:.1f}" for lang, score in self.scores.items()
            }
        }
    
    def is_confident(self, threshold: float = 0.6) -> bool:
        """Check if detection confidence is above threshold"""
        return self.confidence >= threshold


class LanguageValidator:
    """Validates detected language and provides suggestions"""
    
    def __init__(self):
        self.detector = LanguageDetector()
    
    def validate_and_suggest(self, code: str, user_language: str = None, file_extension: str = None) -> dict:
        """
        Validate language and suggest corrections
        
        Args:
            code: Source code
            user_language: Language claimed by user (e.g., 'python')
            file_extension: Optional file extension
            
        Returns:
            Dictionary with validation result
        """
        detected_lang, confidence = self.detector.detect(code, file_extension)
        
        result = {
            'detected_language': detected_lang,
            'confidence': confidence,
            'user_language': user_language,
            'matches': detected_lang.lower() == (user_language or '').lower(),
            'recommendations': []
        }
        
        # Add recommendations if there's a mismatch
        if user_language and not result['matches']:
            if confidence > 0.7:
                result['recommendations'].append(
                    f"Code appears to be {detected_lang}, not {user_language}. "
                    f"Using {detected_lang} for optimization."
                )
            else:
                result['recommendations'].append(
                    "Detection confidence is low. Using your specified language."
                )
        
        if confidence < 0.5:
            result['recommendations'].append(
                "Low confidence in language detection. Ensure code syntax is valid."
            )
        
        return result
