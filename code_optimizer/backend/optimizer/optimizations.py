"""
Code Optimizations Module - ADVANCED VERSION WITH LINE NUMBERS
Implements aggressive optimization techniques for C, C++, and Java
"""

import re
from typing import List, Set, Dict, Tuple, Optional
from .analyzer import CodeAnalyzer
from .ast_utils import (
    parse_assignment,
    simplify_ast,
    ast_to_expression,
    BinaryOpNode,
    NumberNode,
    VariableNode,
)


class CodeOptimizer:
    """Applies advanced optimization techniques to source code"""
    
    def __init__(self, language: str):
        self.language = language.lower()
        self.analyzer = CodeAnalyzer(language)
        self.optimizations_applied = []
        self.ast_insights = {
            'enabled': False,
            'reason': 'No algebraic expressions detected.',
            'items': []
        }

    def _record_optimization(
        self,
        opt_type: str,
        line_number: int,
        before: str,
        after: str,
        optimization_text: Optional[str] = None
    ):
        """Store optimization details with before/after snippets for UI reporting."""
        self.optimizations_applied.append({
            'type': opt_type,
            'line_number': line_number,
            'before': before,
            'after': after,
            'optimization': optimization_text or f'{before} -> {after}'
        })

    def _count_effective_lines(self, code: str) -> int:
        return len([line for line in code.split('\n') if line.strip()])

    def _normalize_optimization_entries(self):
        """Backfill before/after for entries produced by older optimization methods."""
        normalized = []
        for entry in self.optimizations_applied:
            if 'before' not in entry:
                entry['before'] = entry.get('optimization', '')
            if 'after' not in entry:
                entry['after'] = entry.get('optimization', '')
            normalized.append(entry)
        self.optimizations_applied = normalized
    
    def optimize(self, code: str) -> Dict:
        """Apply all optimizations to code"""
        self.optimizations_applied = []
        self.ast_insights = self._collect_partial_ast_insights(code)
        optimized_code = code
        original_effective_lines = self._count_effective_lines(code)
        
        self.analyzer.parse_code(optimized_code)
        
        # Apply optimizations in sequence (most aggressive first)
        optimized_code = self.remove_duplicate_function_calls(optimized_code)
        optimized_code = self.inline_simple_functions(optimized_code)
        optimized_code = self.eliminate_redundant_loops(optimized_code)
        optimized_code = self.perform_loop_invariant_code_motion(optimized_code)
        optimized_code = self.ast_simplify_assignments(optimized_code)
        optimized_code = self.simplify_redundant_expressions(optimized_code)
        optimized_code = self.remove_redundant_variables(optimized_code)
        optimized_code = self.remove_unused_functions(optimized_code)
        optimized_code = self.remove_unused_variables(optimized_code)
        optimized_code = self.eliminate_dead_code(optimized_code)
        optimized_code = self.remove_redundant_assignments(optimized_code)
        optimized_code = self.fold_constants(optimized_code)
        optimized_code = self.combine_variable_declarations(optimized_code)
        optimized_code = self.remove_blank_lines(optimized_code)

        # Never return a version with more effective lines than the input.
        if self._count_effective_lines(optimized_code) > original_effective_lines:
            optimized_code = code

        self._normalize_optimization_entries()
        
        return {
            'optimized_code': optimized_code,
            'optimizations_applied': self.optimizations_applied,
            'ast_insights': self.ast_insights,
            'line_optimization_stats': self._build_line_optimization_stats(),
            'count': len(self.optimizations_applied)
        }

    def _collect_partial_ast_insights(self, code: str) -> Dict:
        """Build a small AST view for assignment algebraic expressions only."""
        items = []

        for i, line in enumerate(code.split('\n'), 1):
            parsed = parse_assignment(line)
            if parsed is None:
                continue

            original_rhs = line.strip().rstrip(';').split('=', 1)[1].strip() if '=' in line else ''
            if not original_rhs or not re.search(r'[\+\-\*/%]', original_rhs):
                continue

            if not isinstance(parsed.expression, BinaryOpNode):
                continue

            simplified = simplify_ast(parsed.expression)
            items.append({
                'line_number': i,
                'target': parsed.variable,
                'original_expression': original_rhs,
                'ast': self._ast_to_compact_string(parsed.expression),
                'simplified_expression': ast_to_expression(simplified)
            })

        if not items:
            return {
                'enabled': False,
                'reason': 'No algebraic expressions detected; AST view is shown only for algebraic assignments.',
                'items': []
            }

        return {
            'enabled': True,
            'reason': 'Partial AST generated for assignment expressions to explain constant folding/algebraic simplification.',
            'items': items
        }

    def _ast_to_compact_string(self, node) -> str:
        """Serialize AST in a compact prefix-like format for UI display."""
        if isinstance(node, NumberNode):
            return str(node.value)
        if isinstance(node, VariableNode):
            return node.name
        if isinstance(node, BinaryOpNode):
            left = self._ast_to_compact_string(node.left)
            right = self._ast_to_compact_string(node.right)
            return f"({node.op} {left} {right})"
        return '<unknown>'

    def _build_line_optimization_stats(self) -> List[Dict]:
        """Aggregate where optimizations were applied (line-wise)."""
        grouped: Dict[int, Dict] = {}

        for opt in self.optimizations_applied:
            line_number = opt.get('line_number')
            if not isinstance(line_number, int):
                continue

            if line_number not in grouped:
                grouped[line_number] = {
                    'line_number': line_number,
                    'count': 0,
                    'types': set(),
                }

            grouped[line_number]['count'] += 1
            grouped[line_number]['types'].add(opt.get('type', 'unknown'))

        stats = []
        for line_number in sorted(grouped.keys()):
            item = grouped[line_number]
            stats.append({
                'line_number': item['line_number'],
                'count': item['count'],
                'types': sorted(item['types'])
            })

        return stats

    def ast_simplify_assignments(self, code: str) -> str:
        """Simplify assignment RHS expressions through a partial AST pass."""
        lines = code.split('\n')
        out_lines = []

        for i, line in enumerate(lines, 1):
            assignment = parse_assignment(line)
            if assignment is None:
                out_lines.append(line)
                continue

            simplified = simplify_ast(assignment.expression)
            new_rhs = ast_to_expression(simplified)

            if assignment.var_type:
                rewritten = f"{assignment.var_type} {assignment.variable} = {new_rhs};"
            else:
                rewritten = f"{assignment.variable} = {new_rhs};"

            if line.strip().endswith(';') and line.strip() != rewritten.strip():
                self._record_optimization(
                    'algebraic_simplification',
                    i,
                    line.strip(),
                    rewritten.strip(),
                    f'Simplified expression for {assignment.variable}'
                )
                out_lines.append(rewritten)
            else:
                out_lines.append(line)

        return '\n'.join(out_lines)

    def simplify_redundant_expressions(self, code: str) -> str:
        """Remove no-op assignments and simplify basic algebraic identities."""
        lines = code.split('\n')
        optimized_lines = []

        patterns = [
            # x = x + 0; or x = x - 0;
            (re.compile(r'^\s*([A-Za-z_]\w*)\s*=\s*\1\s*[\+\-]\s*0\s*;\s*$'), 'self_identity_add_sub'),
            # x = x * 1; or x = x / 1;
            (re.compile(r'^\s*([A-Za-z_]\w*)\s*=\s*\1\s*[\*/]\s*1\s*;\s*$'), 'self_identity_mul_div'),
            # x = x;
            (re.compile(r'^\s*([A-Za-z_]\w*)\s*=\s*\1\s*;\s*$'), 'self_assignment')
        ]

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Keep comments/preprocessor directives intact
            if not stripped or stripped.startswith('//') or stripped.startswith('#'):
                optimized_lines.append(line)
                continue

            removed = False
            for pattern, reason in patterns:
                match = pattern.match(stripped)
                if match:
                    var_name = match.group(1)
                    opt_type = 'redundant_assignment_removal' if reason == 'self_assignment' else 'algebraic_simplification'
                    self._record_optimization(
                        opt_type,
                        i,
                        stripped,
                        '<removed>',
                        f'Removed no-op assignment for {var_name}'
                    )
                    removed = True
                    break

            if not removed:
                optimized_lines.append(line)

        return '\n'.join(optimized_lines)

    def perform_loop_invariant_code_motion(self, code: str) -> str:
        """Hoist loop-invariant assignments from simple for-loops."""
        lines = code.split('\n')
        result_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped.startswith('for'):
                result_lines.append(line)
                i += 1
                continue

            header_match = re.match(r'^\s*for\s*\((.*?)\)\s*\{\s*$', stripped)
            if not header_match:
                result_lines.append(line)
                i += 1
                continue

            loop_header = header_match.group(1)
            iterator_match = re.search(r'(?:int|long|size_t)?\s*([A-Za-z_]\w*)\s*=', loop_header)
            loop_iterator = iterator_match.group(1) if iterator_match else None

            # Collect loop block lines up to matching closing brace
            block_start = i + 1
            brace_depth = 1
            j = block_start
            loop_block = []

            while j < len(lines):
                current = lines[j]
                brace_depth += current.count('{')
                brace_depth -= current.count('}')

                if brace_depth == 0:
                    break

                loop_block.append(current)
                j += 1

            if j >= len(lines):
                # Unbalanced braces, leave unchanged
                result_lines.append(line)
                i += 1
                continue

            assigned_in_loop = set()
            assign_pattern = re.compile(r'^\s*(?:[A-Za-z_]\w*\s+)?([A-Za-z_]\w*)\s*=')

            for block_line in loop_block:
                assign_match = assign_pattern.match(block_line.strip())
                if assign_match:
                    assigned_in_loop.add(assign_match.group(1))

            hoisted_lines = []
            kept_loop_lines = []
            invariant_pattern = re.compile(
                r'^(\s*)([A-Za-z_]\w*(?:\s+[A-Za-z_]\w*)?)\s+([A-Za-z_]\w*)\s*=\s*([^;]+);\s*$'
            )

            for block_line in loop_block:
                stripped_block = block_line.strip()
                inv_match = invariant_pattern.match(block_line)

                if not inv_match or stripped_block.startswith('//'):
                    kept_loop_lines.append(block_line)
                    continue

                indent, var_decl, target_var, expr = inv_match.groups()
                tokens = re.findall(r'\b[A-Za-z_]\w*\b', expr)

                # Allow constants and symbols; reject expressions tied to iterator or mutated vars.
                depends_on_mutated = any(token in assigned_in_loop for token in tokens)
                depends_on_iterator = loop_iterator is not None and loop_iterator in tokens

                if depends_on_mutated or depends_on_iterator:
                    kept_loop_lines.append(block_line)
                    continue

                hoisted_lines.append(block_line)
                self.optimizations_applied.append({
                    'type': 'loop_invariant_code_motion',
                    'line_number': i + 1,
                    'optimization': f'Hoisted loop-invariant assignment: {target_var} = {expr.strip()}'
                })

            if hoisted_lines:
                result_lines.extend(hoisted_lines)

            result_lines.append(line)
            result_lines.extend(kept_loop_lines)
            result_lines.append(lines[j])
            i = j + 1

        return '\n'.join(result_lines)
    
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
        """Remove assignments/declarations for variables that are never used."""
        lines = code.split('\n')
        assigned_vars: Dict[str, List[int]] = {}
        used_vars: Set[str] = set()

        assign_pattern = re.compile(r'^\s*(?:int|double|float|String|boolean|long|char|short)\s+([A-Za-z_]\w*)\s*=|^\s*([A-Za-z_]\w*)\s*=')
        ident_pattern = re.compile(r'\b[A-Za-z_]\w*\b')

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('#'):
                continue

            match = assign_pattern.search(stripped)
            assigned_var = None
            if match:
                assigned_var = match.group(1) or match.group(2)
                assigned_vars.setdefault(assigned_var, []).append(i)

            rhs = stripped.split('=', 1)[1] if '=' in stripped else stripped
            for name in ident_pattern.findall(rhs):
                if name not in {'int', 'double', 'float', 'String', 'boolean', 'long', 'char', 'short', 'return'}:
                    used_vars.add(name)

        removable_vars = {var for var in assigned_vars if var not in used_vars}
        if not removable_vars:
            return code

        optimized_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            match = assign_pattern.search(stripped) if stripped else None
            target = (match.group(1) or match.group(2)) if match else None

            if target and target in removable_vars:
                self._record_optimization(
                    'unused_variable_removal',
                    i,
                    line.strip(),
                    '<removed>',
                    f'Removed unused variable assignment: {target}'
                )
                continue

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
        """Remove overwritten assignments that are never read before reassignment."""
        lines = code.split('\n')
        keep_flags = [True] * len(lines)
        promoted_declarations: Dict[int, Tuple[str, str]] = {}

        assign_pattern = re.compile(
            r'^\s*(?:(int|double|float|String|boolean|long|char|short)\s+)?([A-Za-z_]\w*)\s*=(?!=)'
        )
        ident_pattern = re.compile(r'\b[A-Za-z_]\w*\b')

        next_read_index: Dict[str, int] = {}
        next_write_index: Dict[str, int] = {}

        for idx in range(len(lines) - 1, -1, -1):
            line = lines[idx]
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('#'):
                continue

            assignment_match = assign_pattern.match(stripped)
            declared_type = assignment_match.group(1) if assignment_match else None
            target_var = assignment_match.group(2) if assignment_match else None

            rhs = stripped.split('=', 1)[1] if '=' in stripped else stripped
            for name in ident_pattern.findall(rhs):
                if name != target_var:
                    next_read_index[name] = idx

            if target_var:
                has_future_read = target_var in next_read_index
                has_future_write = target_var in next_write_index

                if has_future_write and (not has_future_read or next_write_index[target_var] < next_read_index[target_var]):
                    keep_flags[idx] = False
                    self._record_optimization(
                        'redundant_assignment_removal',
                        idx + 1,
                        stripped,
                        '<removed>',
                        f'Removed overwritten assignment to {target_var}'
                    )

                    # Preserve declaration semantics for C/C++/Java by promoting
                    # the next assignment to a declaration when needed.
                    next_write = next_write_index[target_var]
                    if declared_type and next_write is not None and next_write not in promoted_declarations:
                        next_match = assign_pattern.match(lines[next_write].strip())
                        if next_match and not next_match.group(1):
                            promoted_declarations[next_write] = (target_var, declared_type)

                next_write_index[target_var] = idx

        optimized_lines = []
        for i, line in enumerate(lines):
            if not keep_flags[i]:
                continue

            if i in promoted_declarations:
                var_name, var_type = promoted_declarations[i]
                assignment_match = assign_pattern.match(line.strip())
                if assignment_match and assignment_match.group(2) == var_name:
                    leading_ws = re.match(r'^\s*', line).group(0)
                    rhs = line.split('=', 1)[1].strip() if '=' in line else ''
                    normalized_rhs = rhs[:-1].strip() if rhs.endswith(';') else rhs
                    line = f"{leading_ws}{var_type} {var_name} = {normalized_rhs};"

            optimized_lines.append(line)

        return '\n'.join(optimized_lines)
    
    def fold_constants(self, code: str) -> str:
        """Fold constants in assignment expressions through the partial AST parser."""
        lines = code.split('\n')
        out_lines = []

        for i, line in enumerate(lines, 1):
            assignment = parse_assignment(line)
            if assignment is None:
                out_lines.append(line)
                continue

            before_rhs = ast_to_expression(assignment.expression)
            simplified = simplify_ast(assignment.expression)
            after_rhs = ast_to_expression(simplified)

            if before_rhs == after_rhs:
                out_lines.append(line)
                continue

            rewritten = f"{assignment.variable} = {after_rhs};"
            if assignment.var_type:
                rewritten = f"{assignment.var_type} {assignment.variable} = {after_rhs};"

            self._record_optimization(
                'constant_folding',
                i,
                line.strip(),
                rewritten.strip(),
                f'Folded constants: {before_rhs} -> {after_rhs}'
            )
            out_lines.append(rewritten)

        return '\n'.join(out_lines)
    
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
        lines_saved = original_lines - optimized_lines
        reduction_percentage = 0.0
        if original_lines > 0:
            reduction_percentage = round((lines_saved / original_lines) * 100.0, 2)
        
        return {
            'total_optimizations': len(self.optimizations_applied),
            'original_lines': original_lines,
            'optimized_lines': optimized_lines,
            'lines_saved': lines_saved,
            'line_reduction_percentage': reduction_percentage,
            'line_optimization_stats': self._build_line_optimization_stats(),
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