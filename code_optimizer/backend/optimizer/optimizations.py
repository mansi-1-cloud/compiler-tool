"""
Code Optimizations Module
Implements various optimization techniques for code optimization:
- Constant Folding
- Dead Code Elimination
- Redundant Assignment Removal
- Unused Variable Removal
"""

import re
from typing import List, Set, Dict, Tuple
from .analyzer import CodeAnalyzer


class CodeOptimizer:
    """Applies optimization techniques to source code"""
    
    def __init__(self, language: str):
        self.language = language.lower()
        self.analyzer = CodeAnalyzer(language)
        self.optimizations_applied = []
    
    def optimize(self, code: str) -> Dict:
        """
        Apply all optimizations to code
        
        Args:
            code: Source code string
            
        Returns:
            Dictionary with optimized_code and optimizations_applied
        """
        self.optimizations_applied = []
        optimized_code = code
        
        # Parse and analyze code
        self.analyzer.parse_code(optimized_code)
        
        # Apply optimizations in sequence
        optimized_code = self.remove_unused_variables(optimized_code)
        optimized_code = self.eliminate_dead_code(optimized_code)
        optimized_code = self.remove_redundant_assignments(optimized_code)
        optimized_code = self.fold_constants(optimized_code)
        optimized_code = self.remove_blank_lines(optimized_code)
        
        return {
            'optimized_code': optimized_code,
            'optimizations_applied': self.optimizations_applied,
            'count': len(self.optimizations_applied)
        }
    
    def fold_constants(self, code: str) -> str:
        """
        Constant Folding Optimization
        Evaluates constant expressions at compile time
        
        Example: a = 2 + 3 → a = 5
        Example: x = 10 * 5 → x = 50
        
        Args:
            code: Source code string
            
        Returns:
            Code with constant expressions folded
        """
        lines = code.split('\n')
        optimized_lines = []
        
        for line in lines:
            optimized_line = line
            
            # Find all constant expressions: number operator number
            pattern = r'(\d+)\s*([\+\-\*/%])\s*(\d+)'
            
            def fold_expression(match):
                left = int(match.group(1))
                op = match.group(2)
                right = int(match.group(3))
                
                try:
                    if op == '+':
                        result = left + right
                    elif op == '-':
                        result = left - right
                    elif op == '*':
                        result = left * right
                    elif op == '/':
                        # Integer division for most languages
                        result = int(left / right)
                    elif op == '%':
                        result = left % right
                    else:
                        return match.group(0)
                    
                    self.optimizations_applied.append({
                        'type': 'constant_folding',
                        'line': line.strip(),
                        'optimization': f'{match.group(0)} → {result}'
                    })
                    
                    return str(result)
                except Exception:
                    return match.group(0)
            
            optimized_line = re.sub(pattern, fold_expression, optimized_line)
            optimized_lines.append(optimized_line)
        
        return '\n'.join(optimized_lines)
    
    def remove_unused_variables(self, code: str) -> str:
        """
        Unused Variable Removal
        Removes assignments to variables that are never used
        
        Example:
            x = 10  # removed if x is never used
            print(x)  # x is used, so kept
        
        Args:
            code: Source code string
            
        Returns:
            Code with unused variable assignments removed
        """
        self.analyzer.parse_code(code)
        unused_vars = self.analyzer.find_unused_variables()
        
        if not unused_vars:
            return code
        
        lines = code.split('\n')
        optimized_lines = []
        
        for line in lines:
            should_remove = False
            stripped = line.strip()
            
            if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                for var_name in unused_vars:
                    # Check if this line assigns to an unused variable
                    pattern = rf'^\s*{var_name}\s*=|\b{var_name}\s*=(?!=)'
                    if re.search(pattern, line):
                        # Make sure it's not a comparison or function call
                        if '==' not in line and '!=' not in line and '(' not in line.split('=')[0]:
                            optimized_lines.append('# ' + line.strip() + '  [REMOVED: unused variable]')
                            self.optimizations_applied.append({
                                'type': 'unused_variable_removal',
                                'variable': var_name,
                                'removed_line': line.strip()
                            })
                            should_remove = True
                            break
            
            if not should_remove:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def eliminate_dead_code(self, code: str) -> str:
        """
        Dead Code Elimination
        Removes unreachable code (code after return, break, etc.)
        
        Example:
            if (x > 0) {
                return 42;
                print("never executes");  # removed
            }
        
        Args:
            code: Source code string
            
        Returns:
            Code with dead code removed
        """
        self.analyzer.parse_code(code)
        dead_code_lines = self.analyzer.find_dead_code_patterns()
        dead_line_nums = {line_num for line_num, _ in dead_code_lines}
        
        lines = code.split('\n')
        optimized_lines = []
        
        for i, line in enumerate(lines, 1):
            if i in dead_line_nums:
                optimized_lines.append('# ' + line.strip() + '  [REMOVED: dead code]')
                self.optimizations_applied.append({
                    'type': 'dead_code_elimination',
                    'removed_line': line.strip()
                })
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def remove_redundant_assignments(self, code: str) -> str:
        """
        Redundant Assignment Removal
        Removes assignments that are immediately overwritten
        
        Example:
            x = 10  # removed
            x = 20  # kept (this is the actual assignment)
        
        Args:
            code: Source code string
            
        Returns:
            Code with redundant assignments removed
        """
        self.analyzer.parse_code(code)
        redundant_assignments = self.analyzer.find_redundant_assignments()
        redundant_line_nums = {first_line for first_line, _, _ in redundant_assignments}
        
        lines = code.split('\n')
        optimized_lines = []
        
        for i, line in enumerate(lines, 1):
            if i in redundant_line_nums:
                # Find which variable was redundantly assigned
                for first_line, _, var_name in redundant_assignments:
                    if first_line == i:
                        optimized_lines.append('# ' + line.strip() + '  [REMOVED: redundant assignment to ' + var_name + ']')
                        self.optimizations_applied.append({
                            'type': 'redundant_assignment_removal',
                            'variable': var_name,
                            'removed_line': line.strip()
                        })
                        break
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def remove_blank_lines(self, code: str) -> str:
        """
        Whitespace Optimization
        Removes excessive blank lines (keeps one blank line for readability)
        
        Args:
            code: Source code string
            
        Returns:
            Code with optimized whitespace
        """
        lines = code.split('\n')
        optimized_lines = []
        prev_blank = False
        
        for line in lines:
            is_blank = len(line.strip()) == 0
            
            # Keep blank line only if previous wasn't blank (max one consecutive)
            if is_blank:
                if not prev_blank:
                    optimized_lines.append(line)
                prev_blank = True
            else:
                optimized_lines.append(line)
                prev_blank = False
        
        # Remove trailing blank lines
        while optimized_lines and len(optimized_lines[-1].strip()) == 0:
            optimized_lines.pop()
        
        return '\n'.join(optimized_lines)
    
    def get_optimization_report(self, original_code: str, optimized_code: str) -> Dict:
        """
        Generate optimization report with statistics
        
        Args:
            original_code: Original source code
            optimized_code: Optimized source code
            
        Returns:
            Dictionary with optimization statistics
        """
        original_lines = len(original_code.split('\n'))
        optimized_lines = len(optimized_code.split('\n'))
        
        return {
            'total_optimizations': len(self.optimizations_applied),
            'original_lines': original_lines,
            'optimized_lines': optimized_lines,
            'lines_saved': original_lines - optimized_lines,
            'optimizations': self.optimizations_applied,
            'optimization_categories': self._categorize_optimizations()
        }
    
    def _categorize_optimizations(self) -> Dict[str, int]:
        """Count optimizations by category"""
        categories = {}
        
        for opt in self.optimizations_applied:
            opt_type = opt.get('type', 'unknown')
            categories[opt_type] = categories.get(opt_type, 0) + 1
        
        return categories


class LanguageSpecificOptimizer:
    """Language-specific optimization strategies"""
    
    def __init__(self, language: str):
        self.language = language.lower()
        self.optimizer = CodeOptimizer(language)
    
    def optimize_python(self, code: str) -> Dict:
        """Python-specific optimizations"""
        result = self.optimizer.optimize(code)
        
        # Additional Python optimizations
        optimized_code = result['optimized_code']
        optimized_code = self._optimize_list_comprehensions(optimized_code)
        optimized_code = self._optimize_imports(optimized_code)
        
        result['optimized_code'] = optimized_code
        return result
    
    def optimize_java(self, code: str) -> Dict:
        """Java-specific optimizations"""
        result = self.optimizer.optimize(code)
        
        # Additional Java optimizations
        optimized_code = result['optimized_code']
        optimized_code = self._optimize_string_concatenation(optimized_code)
        
        result['optimized_code'] = optimized_code
        return result
    
    def optimize_cpp(self, code: str) -> Dict:
        """C++-specific optimizations"""
        result = self.optimizer.optimize(code)
        return result
    
    def optimize_c(self, code: str) -> Dict:
        """C-specific optimizations"""
        result = self.optimizer.optimize(code)
        return result
    
    def _optimize_list_comprehensions(self, code: str) -> str:
        """Optimize loop patterns to list comprehensions (Python)"""
        # This would require more sophisticated parsing
        return code
    
    def _optimize_imports(self, code: str) -> str:
        """Remove unused imports (Python)"""
        lines = code.split('\n')
        return '\n'.join(lines)
    
    def _optimize_string_concatenation(self, code: str) -> str:
        """Optimize string concatenation (Java)"""
        # Suggest using StringBuilder for multiple concatenations
        return code
