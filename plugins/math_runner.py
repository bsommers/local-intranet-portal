"""Math Runner and Formula Evaluation Plugin - AST-Hardened Safe Calculator"""
import ast
import math
import operator

ALLOWED_METHODS = ["GET", "POST"]

# Safe math operators map
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Whitelist safe math functions and constants
SAFE_MATH = {
    k: getattr(math, k) for k in dir(math) if not k.startswith("_")
}
SAFE_MATH.update({
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow
})

def safe_eval_node(node):
    """Recursively evaluates strictly safe mathematical AST nodes. No bytecode or eval() execution."""
    if isinstance(node, ast.Expression):
        return safe_eval_node(node.body)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, complex)):
            return node.value
        raise TypeError("Only numeric constants are permitted")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left = safe_eval_node(node.left)
        right = safe_eval_node(node.right)
        return OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return OPERATORS[op_type](safe_eval_node(node.operand))
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct mathematical function calls are permitted")
        fn_name = node.func.id
        if fn_name not in SAFE_MATH:
            raise ValueError(f"Function '{fn_name}' is not in the safe mathematical whitelist")
        args = [safe_eval_node(arg) for arg in node.args]
        return SAFE_MATH[fn_name](*args)
    elif isinstance(node, ast.Name):
        if node.id in SAFE_MATH:
            return SAFE_MATH[node.id]
        raise ValueError(f"Identifier '{node.id}' is not permitted")
    else:
        raise TypeError(f"Unsafe expression construct: {type(node).__name__}")

def handle_request(method, query_params, body_payload):
    expr = ""
    if method == "POST" and body_payload:
        expr = body_payload.get("expression", "")
    elif query_params and "expr" in query_params:
        expr = query_params["expr"][0]

    if not expr:
        return {
            "plugin": "math_runner",
            "engine": "ast-hardened-evaluator",
            "available_functions": list(SAFE_MATH.keys()),
            "usage": "Send POST with JSON {'expression': 'sqrt(144) + sin(pi/2)'}"
        }

    try:
        # Parse into AST; evaluate with strict node whitelist without invoking Python eval()
        parsed = ast.parse(expr, mode="eval")
        result = safe_eval_node(parsed)
        return {
            "plugin": "math_runner",
            "expression": expr,
            "result": result,
            "type": type(result).__name__,
            "engine": "ast-hardened"
        }
    except Exception as e:
        return {
            "plugin": "math_runner",
            "expression": expr,
            "error": str(e)
        }
