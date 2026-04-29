"""
Lightweight code simulator for output comparison.
Supports a constrained subset of C/C++/Java style assignments and print statements.
"""

import re
from typing import Dict, List


class CodeSimulator:
    """Simulate code execution for simple assignment/print programs."""

    def __init__(self, language: str):
        self.language = language.lower()

    def simulate(self, code: str) -> Dict:
        env: Dict[str, int] = {}
        outputs: List[str] = []
        errors: List[str] = []

        lines = code.split("\n")
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("#"):
                continue

            if stripped.startswith(("if", "for", "while", "switch", "do ", "class ", "public class")):
                continue

            if self._is_print_line(stripped):
                value = self._evaluate_print_value(stripped, env)
                if value is None:
                    errors.append(f"Line {idx}: unable to evaluate print expression")
                    continue
                outputs.append(str(value))
                continue

            assignments = self._extract_assignments(stripped)
            if not assignments:
                continue

            for var_name, expr in assignments:
                evaluated = self._eval_expr(expr, env)
                if evaluated is None:
                    errors.append(f"Line {idx}: unable to evaluate assignment for {var_name}")
                    continue

                env[var_name] = evaluated

        return {
            "output": "\n".join(outputs),
            "stdout_lines": outputs,
            "simulated": len(errors) == 0,
            "errors": errors,
        }

    def _is_print_line(self, line: str) -> bool:
        return (
            "System.out.println" in line
            or "System.out.print" in line
            or re.search(r"\bprintf\s*\(", line) is not None
            or re.search(r"\bcout\b", line) is not None
        )

    def _evaluate_print_value(self, line: str, env: Dict[str, int]):
        if "System.out.println" in line or "System.out.print" in line:
            match = re.search(r"System\.out\.print(?:ln)?\s*\((.*?)\)\s*;?", line)
            if not match:
                return None
            return self._eval_expr(match.group(1), env)

        if re.search(r"\bprintf\s*\(", line):
            match = re.search(r"printf\s*\((.*?)\)\s*;?", line)
            if not match:
                return None
            args = [part.strip() for part in self._split_args(match.group(1))]
            if len(args) >= 2:
                return self._eval_expr(args[1], env)
            if len(args) == 1:
                return self._eval_expr(args[0], env)
            return None

        if re.search(r"\bcout\b", line):
            if "<<" not in line:
                return None
            segments = [seg.strip() for seg in line.split("<<")][1:]
            values = []
            for segment in segments:
                normalized = segment.replace(";", "").strip()
                if normalized in ("endl", "std::endl"):
                    continue
                val = self._eval_expr(normalized, env)
                if val is None:
                    return None
                values.append(str(val))
            return "".join(values)

        return None

    def _extract_assignments(self, line: str):
        if "=" not in line or "==" in line:
            return []

        cleaned = line.rstrip(";")

        # Handle declarations with multiple assignments: int a = 1, b = 2
        type_match = re.match(
            r"^\s*(int|double|float|long|short|char|boolean|String)\s+(.+)$",
            cleaned,
        )
        if type_match and "," in type_match.group(2):
            assignments = []
            for segment in self._split_args(type_match.group(2)):
                if "=" not in segment:
                    continue
                left, right = segment.split("=", 1)
                var_name = left.strip().split()[-1]
                if re.match(r"^[A-Za-z_]\w*$", var_name):
                    assignments.append((var_name, right.strip()))
            return assignments

        left, right = cleaned.split("=", 1)
        var_name = left.strip().split()[-1] if left.strip() else ""
        if not re.match(r"^[A-Za-z_]\w*$", var_name):
            return []

        return [(var_name, right.strip())]

    def _eval_expr(self, expr: str, env: Dict[str, int]):
        cleaned = expr.strip()
        if not cleaned:
            return None

        cleaned = cleaned.replace("std::", "")

        if cleaned.startswith('"') and cleaned.endswith('"'):
            return cleaned[1:-1]

        safe_expr = re.sub(r"\b[A-Za-z_]\w*\b", lambda m: str(env.get(m.group(0), 0)), cleaned)

        if re.search(r"[^0-9\s\+\-\*/%\(\)]", safe_expr):
            return None

        try:
            value = eval(safe_expr, {"__builtins__": {}}, {})
            if isinstance(value, bool):
                return int(value)
            return value
        except Exception:
            return None

    def _split_args(self, arg_str: str) -> List[str]:
        args = []
        current = []
        depth = 0

        for ch in arg_str:
            if ch == ',' and depth == 0:
                args.append("".join(current).strip())
                current = []
                continue
            if ch == '(':
                depth += 1
            elif ch == ')' and depth > 0:
                depth -= 1
            current.append(ch)

        if current:
            args.append("".join(current).strip())

        return args
