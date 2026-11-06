"""Math Runner and Formula Evaluation Plugin"""
import math

ALLOWED_METHODS = ["GET", "POST"]

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

def handle_request(method, query_params, body_payload):
    expr = ""
    if method == "POST" and body_payload:
        expr = body_payload.get("expression", "")
    elif query_params and "expr" in query_params:
        expr = query_params["expr"][0]

    if not expr:
        return {
            "plugin": "math_runner",
            "available_functions": list(SAFE_MATH.keys()),
            "usage": "Send POST with JSON {'expression': 'sqrt(144) + sin(pi/2)'}"
        }

    try:
        # Safe eval using restricted globals
        result = eval(expr, {"__builtins__": None}, SAFE_MATH)
        return {
            "plugin": "math_runner",
            "expression": expr,
            "result": result,
            "type": type(result).__name__
        }
    except Exception as e:
        return {
            "plugin": "math_runner",
            "expression": expr,
            "error": str(e)
        }
