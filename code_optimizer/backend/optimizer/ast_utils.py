"""
Partial AST utilities for simple assignment and arithmetic expression handling.
Only supports the subset required by optimizer passes.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


@dataclass
class NumberNode:
    value: int


@dataclass
class VariableNode:
    name: str


@dataclass
class BinaryOpNode:
    op: str
    left: "AstNode"
    right: "AstNode"


AstNode = Union[NumberNode, VariableNode, BinaryOpNode]


@dataclass
class AssignmentNode:
    var_type: Optional[str]
    variable: str
    expression: AstNode


_TOKEN_NUMBER = "NUMBER"
_TOKEN_IDENT = "IDENT"
_TOKEN_OP = "OP"
_TOKEN_LPAREN = "LPAREN"
_TOKEN_RPAREN = "RPAREN"


def parse_assignment(line: str) -> Optional[AssignmentNode]:
    """Parse lines like: int x = 2 + y; or x = a + 1;"""
    cleaned = line.strip()
    if not cleaned or cleaned.startswith("//") or cleaned.startswith("#"):
        return None

    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()

    if "=" not in cleaned:
        return None

    left, right = cleaned.split("=", 1)
    left = left.strip()
    right = right.strip()

    if not left or not right:
        return None

    parts = left.split()
    if len(parts) == 1:
        var_type = None
        variable = parts[0]
    elif len(parts) == 2:
        var_type, variable = parts
    else:
        return None

    if not _is_identifier(variable):
        return None

    expr_ast = parse_expression(right)
    if expr_ast is None:
        return None

    return AssignmentNode(var_type=var_type, variable=variable, expression=expr_ast)


def parse_expression(expr: str) -> Optional[AstNode]:
    """Build a simple AST for arithmetic expressions with +,-,*,/,%."""
    tokens = _tokenize(expr)
    if not tokens:
        return None

    output: List[Tuple[str, str]] = []
    operators: List[Tuple[str, str]] = []

    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}

    for token_type, token_value in tokens:
        if token_type in (_TOKEN_NUMBER, _TOKEN_IDENT):
            output.append((token_type, token_value))
        elif token_type == _TOKEN_OP:
            while operators and operators[-1][0] == _TOKEN_OP:
                top_op = operators[-1][1]
                if precedence.get(top_op, 0) >= precedence.get(token_value, 0):
                    output.append(operators.pop())
                else:
                    break
            operators.append((token_type, token_value))
        elif token_type == _TOKEN_LPAREN:
            operators.append((token_type, token_value))
        elif token_type == _TOKEN_RPAREN:
            while operators and operators[-1][0] != _TOKEN_LPAREN:
                output.append(operators.pop())
            if not operators:
                return None
            operators.pop()

    while operators:
        token = operators.pop()
        if token[0] in (_TOKEN_LPAREN, _TOKEN_RPAREN):
            return None
        output.append(token)

    stack: List[AstNode] = []
    for token_type, token_value in output:
        if token_type == _TOKEN_NUMBER:
            stack.append(NumberNode(int(token_value)))
        elif token_type == _TOKEN_IDENT:
            stack.append(VariableNode(token_value))
        elif token_type == _TOKEN_OP:
            if len(stack) < 2:
                return None
            right = stack.pop()
            left = stack.pop()
            stack.append(BinaryOpNode(op=token_value, left=left, right=right))

    if len(stack) != 1:
        return None

    return stack[0]


def simplify_ast(node: AstNode) -> AstNode:
    """Apply local algebraic simplification rules on AST."""
    if isinstance(node, BinaryOpNode):
        left = simplify_ast(node.left)
        right = simplify_ast(node.right)

        if isinstance(left, NumberNode) and isinstance(right, NumberNode):
            return NumberNode(_eval_op(left.value, node.op, right.value))

        if node.op == "+":
            if isinstance(right, NumberNode) and right.value == 0:
                return left
            if isinstance(left, NumberNode) and left.value == 0:
                return right
        elif node.op == "-":
            if isinstance(right, NumberNode) and right.value == 0:
                return left
        elif node.op == "*":
            if isinstance(right, NumberNode) and right.value == 1:
                return left
            if isinstance(left, NumberNode) and left.value == 1:
                return right
            if isinstance(right, NumberNode) and right.value == 0:
                return NumberNode(0)
            if isinstance(left, NumberNode) and left.value == 0:
                return NumberNode(0)
        elif node.op == "/":
            if isinstance(right, NumberNode) and right.value == 1:
                return left
            if isinstance(left, NumberNode) and left.value == 0:
                return NumberNode(0)

        return BinaryOpNode(op=node.op, left=left, right=right)

    return node


def ast_to_expression(node: AstNode) -> str:
    """Convert AST back to a compact infix expression string."""
    if isinstance(node, NumberNode):
        return str(node.value)
    if isinstance(node, VariableNode):
        return node.name
    if isinstance(node, BinaryOpNode):
        left = ast_to_expression(node.left)
        right = ast_to_expression(node.right)
        return f"{_wrap_if_needed(node.left, node.op, left)} {node.op} {_wrap_if_needed(node.right, node.op, right)}"
    return ""


def _wrap_if_needed(child: AstNode, parent_op: str, text: str) -> str:
    if not isinstance(child, BinaryOpNode):
        return text

    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}
    if precedence[child.op] < precedence[parent_op]:
        return f"({text})"
    return text


def _eval_op(left: int, op: str, right: int) -> int:
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        if right == 0:
            return left
        return int(left / right)
    if op == "%":
        if right == 0:
            return left
        return left % right
    return left


def _tokenize(expr: str) -> List[Tuple[str, str]]:
    tokens: List[Tuple[str, str]] = []
    i = 0

    while i < len(expr):
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append((_TOKEN_NUMBER, expr[i:j]))
            i = j
            continue

        if ch.isalpha() or ch == "_":
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            tokens.append((_TOKEN_IDENT, expr[i:j]))
            i = j
            continue

        if ch in "+-*/%":
            tokens.append((_TOKEN_OP, ch))
            i += 1
            continue

        if ch == "(":
            tokens.append((_TOKEN_LPAREN, ch))
            i += 1
            continue

        if ch == ")":
            tokens.append((_TOKEN_RPAREN, ch))
            i += 1
            continue

        return []

    return tokens


def _is_identifier(value: str) -> bool:
    if not value:
        return False
    if not (value[0].isalpha() or value[0] == "_"):
        return False
    return all(ch.isalnum() or ch == "_" for ch in value)
