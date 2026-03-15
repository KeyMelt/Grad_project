import ast
from typing import Any, Callable


SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "range": range,
    "round": round,
    "set": set,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}

FORBIDDEN_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.ClassDef,
    ast.AsyncFunctionDef,
    ast.With,
    ast.Try,
    ast.Raise,
    ast.Global,
    ast.Nonlocal,
)

FORBIDDEN_NAMES = {
    "__import__",
    "breakpoint",
    "compile",
    "delattr",
    "dir",
    "eval",
    "exec",
    "getattr",
    "globals",
    "help",
    "input",
    "locals",
    "open",
    "setattr",
    "vars",
}


def load_user_function(submitted_code: str, required_function: str) -> Callable[..., Any]:
    """Parse, validate, and load a user-defined function in a restricted namespace."""
    _validate_user_code(submitted_code)

    local_context = {"__builtins__": SAFE_BUILTINS}
    exec(submitted_code, local_context, local_context)

    function = local_context.get(required_function)
    if not callable(function):
        raise ValueError(
            f"Required function '{required_function}' was not defined.",
        )
    return function


def _validate_user_code(submitted_code: str) -> None:
    tree = ast.parse(submitted_code)
    for node in ast.walk(tree):
        if isinstance(node, FORBIDDEN_NODES):
            raise ValueError(
                f"Unsupported syntax '{type(node).__name__}' is not allowed in submitted code.",
            )

        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise ValueError(f"Use of '{node.id}' is not allowed in submitted code.")

        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise ValueError("Dunder attribute access is not allowed in submitted code.")
