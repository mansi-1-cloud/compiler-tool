"""
Code Analyzer Module
Analyzes source code to identify inefficient patterns and opportunities for optimization.
Supports: C, C++, Java
"""

import re
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass


@dataclass
class Line:
    """Represents a line of code with metadata"""
    number: int
    content: str
    stripped: str
    is_comment: bool
    is_blank: bool


class CodeAnalyzer:
    """Analyzes code for optimization opportunities"""
    
    def __init__(self, language: str):
        self.language = language.lower()
        self.lines: List[Line] = []
        self.variables: Dict[str, List[int]] = {}  # var_name -> [line_numbers where used]
        
    def parse_code(self, code: str) -> List[Line]:
        """
        Parse code into lines with metadata
        
        Args:
            code: Source code string
            
        Returns:
            List of Line objects
        """
        lines = code.split('\n')
        parsed_lines = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            is_blank = len(stripped) == 0
            is_comment = self._is_comment(stripped)
            
            parsed_lines.append(Line(
                number=i,
                content=line,
                stripped=stripped,
                is_comment=is_comment,
                is_blank=is_blank
            ))
        
        self.lines = parsed_lines
        return parsed_lines
    
    def _is_comment(self, line: str) -> bool:
        """Check if line is a comment"""
        # C, C++, Java all use // and /* */
        return line.startswith('//') or line.startswith('/*')
    
    def extract_variables(self) -> Dict[str, List[int]]:
        """
        Extract all variable names and their usage locations
        
        Returns:
            Dictionary mapping variable names to list of line numbers where used
        """
        variables: Dict[str, List[int]] = {}
        
        for line in self.lines:
            if line.is_blank or line.is_comment:
                continue
            
            # Simple pattern: word characters that look like variable names
            var_pattern = r'\b[a-zA-Z_]\w*\b'
            matches = re.finditer(var_pattern, line.stripped)
            
            for match in matches:
                var_name = match.group()
                # Skip keywords
                if not self._is_keyword(var_name):
                    if var_name not in variables:
                        variables[var_name] = []
                    variables[var_name].append(line.number)
        
        self.variables = variables
        return variables
    
    def _is_keyword(self, word: str) -> bool:
        """Check if word is a language keyword"""
        
        c_cpp_keywords = {
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'int', 'float', 'double', 'char', 'void', 'bool', 'return',
            'struct', 'union', 'enum', 'typedef', 'static', 'const', 'extern',
            'volatile', 'signed', 'unsigned', 'auto', 'register', 'inline',
            'continue', 'break', 'goto', 'sizeof', 'typeof', 'long', 'short'
        }
        
        java_keywords = {
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'int', 'float', 'double', 'char', 'void', 'boolean', 'byte', 'short',
            'long', 'return', 'class', 'interface', 'extends', 'implements', 'new',
            'this', 'super', 'public', 'private', 'protected', 'static', 'final',
            'abstract', 'synchronized', 'volatile', 'transient', 'native', 'strictfp',
            'continue', 'break', 'goto', 'instanceof', 'import', 'package', 'throws',
            'try', 'catch', 'finally', 'throw', 'assert', 'enum', 'true', 'false',
            'null', 'String', 'Object', 'System'
        }
        
        if self.language in ['c', 'cpp', 'c++']:
            return word in c_cpp_keywords
        elif self.language == 'java':
            return word in java_keywords
        
        return False
    
    def find_unused_variables(self) -> Set[str]:
        """
        Find variables that are assigned but never used
        
        Returns:
            Set of unused variable names
        """
        unused = set()
        self.extract_variables()
        
        for var_name, line_numbers in self.variables.items():
            # If variable appears only once (just assignment), it's likely unused
            if len(line_numbers) == 1:
                line_num = line_numbers[0]
                if line_num > 0 and line_num <= len(self.lines):
                    line_content = self.lines[line_num - 1].stripped
                    
                    # Check if it's an assignment (not a declaration without assignment)
                    if self._is_assignment(line_content, var_name):
                        unused.add(var_name)
        
        return unused
    
    def _is_assignment(self, line: str, var_name: str) -> bool:
        """Check if line contains an assignment to variable"""
        # Look for var_name = ... pattern
        pattern = rf'\b{var_name}\s*=(?!=)'  # = but not ==
        return bool(re.search(pattern, line))
    
    def find_constant_expressions(self) -> List[Tuple[int, str]]:
        """
        Find expressions that can be constant folded
        
        Returns:
            List of (line_number, expression) tuples
        """
        constant_exprs = []
        
        for line in self.lines:
            if line.is_blank or line.is_comment:
                continue
            
            # Pattern for arithmetic operations with constants
            # e.g., a = 2 + 3, x = 10 * 5
            pattern = r'(\d+\s*[+\-*/%]\s*\d+)'
            matches = re.finditer(pattern, line.stripped)
            
            for match in matches:
                expr = match.group(1)
                constant_exprs.append((line.number, expr))
        
        return constant_exprs
    
    def find_redundant_assignments(self) -> List[Tuple[int, int, str]]:
        """
        Find redundant assignments (variable assigned multiple times without use between them)
        
        Returns:
            List of (line_num, next_line_num, var_name) tuples
        """
        redundant = []
        
        for i, line in enumerate(self.lines):
            if line.is_blank or line.is_comment:
                continue
            
            # Find assignments in this line
            assignments = self._find_assignments_in_line(line.stripped)
            
            if not assignments:
                continue
            
            # Check if variable is assigned again before being used
            for var_name in assignments:
                for j in range(i + 1, len(self.lines)):
                    next_line = self.lines[j]
                    
                    if next_line.is_blank or next_line.is_comment:
                        continue
                    
                    # If same variable is assigned again without being used
                    if self._contains_assignment_to(next_line.stripped, var_name):
                        if not self._uses_variable(next_line.stripped, var_name):
                            redundant.append((i + 1, j + 1, var_name))
                            break
                    
                    # If variable is used, stop checking this variable
                    if self._uses_variable(next_line.stripped, var_name, exclude_assignment=True):
                        break
        
        return redundant
    
    def _find_assignments_in_line(self, line: str) -> Set[str]:
        """Find all variable assignments in a line"""
        assignments = set()
        # Pattern: var_name = ... (but not ==, !=, <=, >=)
        pattern = r'(\b[a-zA-Z_]\w*)\s*=(?!=)'
        matches = re.finditer(pattern, line)
        
        for match in matches:
            var_name = match.group(1)
            if not self._is_keyword(var_name):
                assignments.add(var_name)
        
        return assignments
    
    def _contains_assignment_to(self, line: str, var_name: str) -> bool:
        """Check if line assigns to variable"""
        pattern = rf'\b{var_name}\s*=(?!=)'
        return bool(re.search(pattern, line))
    
    def _uses_variable(self, line: str, var_name: str, exclude_assignment=False) -> bool:
        """Check if variable is used in line"""
        if exclude_assignment:
            # Remove assignment part
            line = re.sub(rf'\b{var_name}\s*=(?!=)[^;,\n]*', '', line)
        
        # Check if variable name appears (not as part of another word)
        pattern = rf'\b{var_name}\b'
        return bool(re.search(pattern, line))
    
    def find_dead_code_patterns(self) -> List[Tuple[int, str]]:
        """
        Find dead code patterns (unreachable code)
        
        Returns:
            List of (line_number, pattern_type) tuples
        """
        dead_code = []
        
        for i, line in enumerate(self.lines):
            if line.is_blank or line.is_comment:
                continue
            
            stripped = line.stripped
            
            # Check for return statements followed by code
            if 'return' in stripped and not stripped.startswith('//'):
                for j in range(i + 1, len(self.lines)):
                    next_line = self.lines[j]
                    if next_line.is_blank or next_line.is_comment:
                        continue
                    # Code after return
                    if not self._is_closing_brace(next_line.stripped):
                        dead_code.append((j + 1, 'unreachable_after_return'))
                        break
            
            # Check for break in last iteration
            if stripped in ['break', 'break;']:
                for j in range(i + 1, len(self.lines)):
                    next_line = self.lines[j]
                    if next_line.is_blank or next_line.is_comment:
                        continue
                    if not self._is_closing_brace(next_line.stripped):
                        dead_code.append((j + 1, 'unreachable_after_break'))
                        break
        
        return dead_code
    
    def _is_closing_brace(self, line: str) -> bool:
        """Check if line is just a closing brace"""
        return line in ['}', '};', '):']
    
    def get_analysis_summary(self) -> Dict:
        """Get summary of code analysis"""
        self.extract_variables()
        
        return {
            'total_lines': len(self.lines),
            'code_lines': sum(1 for l in self.lines if not l.is_blank and not l.is_comment),
            'blank_lines': sum(1 for l in self.lines if l.is_blank),
            'comment_lines': sum(1 for l in self.lines if l.is_comment),
            'total_variables': len(self.variables),
            'unused_variables': len(self.find_unused_variables()),
            'constant_expressions': len(self.find_constant_expressions()),
            'redundant_assignments': len(self.find_redundant_assignments()),
        }