"""
Code Optimizations Module - ADVANCED VERSION WITH LINE NUMBERS
Implements aggressive optimization techniques for C, C++, and Java
"""

import re
from typing import List, Set, Dict, Tuple
from .analyzer import CodeAnalyzer


class CodeOptimizer:
    """Applies advanced optimization techniques to source code"""
    
    def __init__(self, language: str):
        self.language = language.lower()
        self.analyzer = CodeAnalyzer(language)
        self.optimizations_applied = []
    
    def optimize(self, code: str) -> Dict:
        """Apply all optimizations to code"""
        self.optimizations_applied = []
        optimized_code = code
        
        self.analyzer.parse_code(optimized_code)
        
        # Apply optimizations in sequence (most aggressive first)
        optimized_code = self.remove_duplicate_function_calls(optimized_code)
        optimized_code = self.inline_simple_functions(optimized_code)
        optimized_code = self.eliminate_redundant_loops(optimized_code)
        optimized_code = self.combine_variable_declarations(optimized_code)
        optimized_code = self.remove_redundant_variables(optimized_code)
        optimized_code = self.remove_unused_functions(optimized_code)
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
    
    def validate_syntax(self, code: str) -> bool:
        """Validate syntax: matching braces and variables in main()"""
        lines = code.split('\n')
        
        # Check brace matching
        open_braces = 0
        for line in lines:
            open_braces += line.count('{')
            open_braces -= line.count('}')
        
        if open_braces != 0:
            return False
        
        # Check if main function exists
        has_main = False
        for line in lines:
            if 'main' in line and '(' in line:
                has_main = True
                break
        
        if not has_main:
            return False
        
        return True
    
    def remove_duplicate_function_calls(self, code: str) -> str:
        """Remove duplicate function calls and store in variable"""
        lines = code.split('\n')
        
        # Find all function calls and their arguments
        call_map = {}
        
        for i, line in enumerate(lines):
            match = re.search(r'(\w+)\s*=\s*(\w+)\s*\(([^)]+)\)\s*;', line)
            if match:
                var_name = match.group(1)
                func_name = match.group(2)
                args = match.group(3)
                
                call_key = f"{func_name}({args})"
                
                if call_key not in call_map:
                    call_map[call_key] = []
                
                call_map[call_key].append((i, var_name))
        
        # Find duplicate calls
        result_lines = []
        skip_lines = set()
        replacement_map = {}
        
        for call_key, occurrences in call_map.items():
            if len(occurrences) > 1:
                first_line_num, first_var = occurrences[0]
                
                self.optimizations_applied.append({
                    'type': 'duplicate_call_removal',
                    'line_number': first_line_num + 1,
                    'optimization': f'Removed duplicate call: {call_key}'
                })
                
                for line_num, var_name in occurrences[1:]:
                    replacement_map[var_name] = first_var
                    skip_lines.add(line_num)
        
        # Build result with replacements
        for i, line in enumerate(lines):
            if i in skip_lines:
                continue
            
            new_line = line
            for old_var, new_var in replacement_map.items():
                new_line = re.sub(rf'\b{old_var}\b', new_var, new_line)
            
            result_lines.append(new_line)
        
        return '\n'.join(result_lines)
    
    def inline_simple_functions(self, code: str) -> str:
        """Inline simple functions"""
        lines = code.split('\n')
        
        function_map = {}
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            type_pattern = r'(public\s+)?(static\s+)?(int|double|float|String|void|boolean|long)\s+(\w+)\s*\((.*?)\)'
            match = re.match(type_pattern, stripped)
            
            if match:
                func_name = match.group(4)
                params_str = match.group(5).strip() if match.group(5) else ""
                
                if func_name == 'main':
                    i += 1
                    continue
                
                if i + 1 < len(lines) and '{' in stripped:
                    try:
                        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                        
                        if next_line and 'return' in next_line:
                            return_expr = next_line.replace('return', '').replace(';', '').strip()
                            
                            if return_expr and ('+' in return_expr or '-' in return_expr or '*' in return_expr or 
                                              'a' in return_expr or 'b' in return_expr or 
                                              'x' in return_expr or 'y' in return_expr):
                                
                                for j in range(i + 1, min(i + 5, len(lines))):
                                    if '}' in lines[j]:
                                        function_map[func_name] = {
                                            'params': params_str,
                                            'body': return_expr,
                                            'start': i,
                                            'end': j,
                                            'line_number': i + 1
                                        }
                                        break
                    except Exception as e:
                        pass
            
            i += 1
        
        result_lines = []
        
        for idx, line in enumerate(lines):
            inlined_line = line
            
            for func_name, func_info in function_map.items():
                try:
                    call_pattern = rf'{func_name}\s*\(([^)]+)\)'
                    match = re.search(call_pattern, inlined_line)
                    
                    if match:
                        args_str = match.group(1)
                        args = [arg.strip() for arg in args_str.split(',')]
                        
                        params_str = func_info.get('params', '')
                        params = []
                        
                        if params_str:
                            for param in params_str.split(','):
                                parts = param.strip().split()
                                if len(parts) > 0:
                                    params.append(parts[-1])
                        
                        substitution = {}
                        for param, arg in zip(params, args):
                            substitution[param] = arg
                        
                        inlined = func_info.get('body', '')
                        if inlined:
                            for param, arg in substitution.items():
                                inlined = re.sub(rf'\b{param}\b', arg, inlined)
                            
                            inlined_line = re.sub(call_pattern, inlined, inlined_line)
                            
                            self.optimizations_applied.append({
                                'type': 'function_inlining',
                                'line_number': idx + 1,
                                'optimization': f'Inlined {func_name}() call'
                            })
                except Exception as e:
                    pass
            
            result_lines.append(inlined_line)
        
        final_result = []
        i = 0
        while i < len(result_lines):
            skip = False
            
            for func_name, func_info in function_map.items():
                if i >= func_info['start'] and i <= func_info['end']:
                    skip = True
                    break
            
            if not skip:
                final_result.append(result_lines[i])
            
            i += 1
        
        return '\n'.join(final_result)
    
    def eliminate_redundant_loops(self, code: str) -> str:
        """Eliminate simple increment loops"""
        lines = code.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if stripped.startswith('for') and '(' in stripped and '<' in stripped:
                matched = False
                
                try:
                    if '{' in stripped and i + 2 < len(lines):
                        next_line = lines[i + 1].strip()
                        close_line = lines[i + 2].strip()
                        
                        if '++' in next_line and close_line == '}':
                            counter = next_line.replace('++', '').replace(';', '').strip()
                            limit = stripped.split('<')[1].split(';')[0].strip()
                            
                            opt_line = f"{counter} = {counter} + {limit};"
                            result_lines.append(opt_line)
                            
                            self.optimizations_applied.append({
                                'type': 'loop_elimination',
                                'line_number': i + 1,
                                'optimization': f'Loop eliminated: {opt_line}'
                            })
                            
                            i += 3
                            matched = True
                    
                    if not matched and '{' in stripped and '++' in stripped:
                        counter = stripped.split('{')[1].split('++')[0].strip()
                        limit = stripped.split('<')[1].split(';')[0].strip()
                        
                        opt_line = f"{counter} = {counter} + {limit};"
                        result_lines.append(opt_line)
                        
                        self.optimizations_applied.append({
                            'type': 'loop_elimination',
                            'line_number': i + 1,
                            'optimization': f'Loop eliminated: {opt_line}'
                        })
                        
                        i += 1
                        matched = True
                
                except Exception as e:
                    pass
                
                if matched:
                    continue
            
            result_lines.append(line)
            i += 1
        
        return '\n'.join(result_lines)
    
    def combine_variable_declarations(self, code: str) -> str:
        """Combine multiple variable declarations on same line"""
        lines = code.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            try:
                type_match = re.match(r'^(int|double|float|String|boolean|long)\s+(\w+)\s*=\s*(.+?);', stripped)
                
                if type_match and i + 1 < len(lines):
                    var_type = type_match.group(1)
                    var1 = type_match.group(2)
                    val1 = type_match.group(3)
                    
                    next_line = lines[i + 1].strip()
                    next_match = re.match(rf'^{var_type}\s+(\w+)\s*=\s*(.+?);', next_line)
                    
                    if next_match:
                        var2 = next_match.group(1)
                        val2 = next_match.group(2)
                        
                        combined = f"{var_type} {var1} = {val1}, {var2} = {val2};"
                        result_lines.append(combined)
                        
                        self.optimizations_applied.append({
                            'type': 'variable_combination',
                            'line_number': i + 1,
                            'optimization': f'Combined declarations: {var1}, {var2}'
                        })
                        
                        i += 2
                        continue
            except Exception as e:
                pass
            
            result_lines.append(line)
            i += 1
        
        return '\n'.join(result_lines)
    
    def remove_redundant_variables(self, code: str) -> str:
        """Remove unused variables"""
        lines = code.split('\n')
        
        var_usage = {}
        for i, line in enumerate(lines):
            if '=' in line and not 'return' in line:
                try:
                    matches = re.findall(r'(\w+)\s*=', line)
                    for var in matches:
                        if var not in var_usage:
                            var_usage[var] = {'assigned': 0, 'used': 0, 'line': i}
                        var_usage[var]['assigned'] += 1
                except:
                    pass
            
            for var in list(var_usage.keys()):
                try:
                    if re.search(rf'\b{var}\b', line) and '=' not in line.split(var)[0]:
                        var_usage[var]['used'] += 1
                except:
                    pass
        
        result_lines = []
        for i, line in enumerate(lines):
            remove = False
            try:
                for var, usage in var_usage.items():
                    if usage['assigned'] > 0 and usage['used'] == 0:
                        if re.search(rf'^\s*(int|double|float|String|boolean|long)\s+{var}\s*=', line):
                            remove = True
                            self.optimizations_applied.append({
                                'type': 'dead_code_removal',
                                'line_number': i + 1,
                                'optimization': f'Removed unused variable: {var}'
                            })
                            break
            except:
                pass
            
            if not remove:
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def remove_unused_functions(self, code: str) -> str:
        """Remove unused functions"""
        lines = code.split('\n')
        
        functions = {}
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            try:
                func_match = re.search(r'(public|private|static|protected)?\s*(int|double|float|String|void|boolean|long)\s+(\w+)\s*\(', stripped)
                if func_match:
                    func_name = func_match.group(3)
                    if func_name not in ['main', 'Main']:
                        functions[func_name] = i
            except:
                pass
            
            i += 1
        
        if not functions:
            return code
        
        called_functions = set()
        for i, line in enumerate(lines):
            for func_name in functions:
                try:
                    if i != functions[func_name]:
                        if re.search(rf'\b{func_name}\s*\(', line):
                            called_functions.add(func_name)
                except:
                    pass
        
        result_lines = []
        skip_until = -1
        
        for i, line in enumerate(lines):
            if i <= skip_until:
                continue
            
            stripped = line.strip()
            
            remove_func = False
            for func_name, func_line in functions.items():
                if i == func_line and func_name not in called_functions:
                    remove_func = True
                    
                    try:
                        brace_count = 0
                        started = False
                        for j in range(i, len(lines)):
                            if '{' in lines[j]:
                                started = True
                                brace_count += lines[j].count('{')
                            if '}' in lines[j]:
                                brace_count -= lines[j].count('}')
                            
                            if started and brace_count == 0:
                                skip_until = j
                                self.optimizations_applied.append({
                                    'type': 'dead_code_removal',
                                    'line_number': i + 1,
                                    'optimization': f'Removed unused function: {func_name}'
                                })
                                break
                    except:
                        pass
                    break
            
            if not remove_func:
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def remove_unused_variables(self, code: str) -> str:
        """Remove unused variable declarations"""
        try:
            self.analyzer.parse_code(code)
            unused_vars = self.analyzer.find_unused_variables()
        except:
            unused_vars = []
        
        if not unused_vars:
            return code
        
        lines = code.split('\n')
        optimized_lines = []
        
        for i, line in enumerate(lines):
            should_remove = False
            stripped = line.strip()
            
            if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                for var_name in unused_vars:
                    try:
                        pattern = rf'^\s*(int|double|float|String|boolean|long)\s+{var_name}\s*=|^\s*{var_name}\s*='
                        if re.search(pattern, line):
                            if '==' not in line and '!=' not in line:
                                self.optimizations_applied.append({
                                    'type': 'dead_code_removal',
                                    'line_number': i + 1,
                                    'optimization': f'Removed unused variable: {var_name}'
                                })
                                should_remove = True
                                break
                    except:
                        pass
            
            if not should_remove:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def eliminate_dead_code(self, code: str) -> str:
        """Eliminate unreachable code"""
        try:
            self.analyzer.parse_code(code)
            dead_code_lines = self.analyzer.find_dead_code_patterns()
            dead_line_nums = {line_num for line_num, _ in dead_code_lines}
        except:
            dead_line_nums = set()
        
        lines = code.split('\n')
        optimized_lines = []
        
        for i, line in enumerate(lines, 1):
            if i not in dead_line_nums:
                optimized_lines.append(line)
            else:
                try:
                    self.optimizations_applied.append({
                        'type': 'dead_code_removal',
                        'line_number': i,
                        'optimization': f'Removed dead code: {line.strip()}'
                    })
                except:
                    pass
        
        return '\n'.join(optimized_lines)
    
    def remove_redundant_assignments(self, code: str) -> str:
        """Remove redundant assignments"""
        try:
            self.analyzer.parse_code(code)
            redundant_assignments = self.analyzer.find_redundant_assignments()
            redundant_line_nums = {first_line for first_line, _, _ in redundant_assignments}
        except:
            redundant_line_nums = set()
        
        lines = code.split('\n')
        optimized_lines = []
        
        for i, line in enumerate(lines, 1):
            if i not in redundant_line_nums:
                optimized_lines.append(line)
            else:
                try:
                    for first_line, _, var_name in redundant_assignments:
                        if first_line == i:
                            self.optimizations_applied.append({
                                'type': 'dead_code_removal',
                                'line_number': i,
                                'optimization': f'Removed redundant assignment to: {var_name}'
                            })
                            break
                except:
                    pass
        
        return '\n'.join(optimized_lines)
    
    def fold_constants(self, code: str) -> str:
        """Fold constant expressions"""
        lines = code.split('\n')
        optimized_lines = []
        
        for i, line in enumerate(lines):
            optimized_line = line
            pattern = r'(\d+)\s*([\+\-\*/%])\s*(\d+)'
            
            def fold_expression(match):
                try:
                    left = int(match.group(1))
                    op = match.group(2)
                    right = int(match.group(3))
                    
                    if op == '+':
                        result = left + right
                    elif op == '-':
                        result = left - right
                    elif op == '*':
                        result = left * right
                    elif op == '/':
                        result = int(left / right)
                    elif op == '%':
                        result = left % right
                    else:
                        return match.group(0)
                    
                    self.optimizations_applied.append({
                        'type': 'constant_folding',
                        'line_number': i + 1,
                        'optimization': f'{match.group(0)} → {result}'
                    })
                    
                    return str(result)
                except:
                    return match.group(0)
            
            try:
                optimized_line = re.sub(pattern, fold_expression, optimized_line)
            except:
                pass
            
            optimized_lines.append(optimized_line)
        
        return '\n'.join(optimized_lines)
    
    def remove_blank_lines(self, code: str) -> str:
        """Remove excessive blank lines"""
        lines = code.split('\n')
        optimized_lines = []
        prev_blank = False
        
        for line in lines:
            is_blank = len(line.strip()) == 0
            
            if is_blank:
                if not prev_blank:
                    optimized_lines.append(line)
                prev_blank = True
            else:
                optimized_lines.append(line)
                prev_blank = False
        
        while optimized_lines and len(optimized_lines[-1].strip()) == 0:
            optimized_lines.pop()
        
        return '\n'.join(optimized_lines)
    
    def get_optimization_report(self, original_code: str, optimized_code: str) -> Dict:
        """Generate optimization report"""
        original_lines = len([l for l in original_code.split('\n') if l.strip()])
        optimized_lines = len([l for l in optimized_code.split('\n') if l.strip()])
        
        return {
            'total_optimizations': len(self.optimizations_applied),
            'original_lines': original_lines,
            'optimized_lines': optimized_lines,
            'lines_saved': original_lines - optimized_lines,
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
    
    def optimize_java(self, code: str) -> Dict:
        return self.optimizer.optimize(code)
    
    def optimize_cpp(self, code: str) -> Dict:
        return self.optimizer.optimize(code)
    
    def optimize_c(self, code: str) -> Dict:
        return self.optimizer.optimize(code)