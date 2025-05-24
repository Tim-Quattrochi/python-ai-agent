"""Calculator tool for mathematical operations."""

import ast
import operator
from typing import Dict, Any
from .base import Tool


class CalculatorTool(Tool):
    """A tool for performing mathematical calculations."""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations. Supports basic arithmetic operations (+, -, *, /), exponentiation (**), and common math functions."
        )

        # Safe operators for evaluation
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
            ast.USub: operator.neg,
        }

    def execute(self, expression: str) -> str:
        """Execute a mathematical calculation."""
        try:
            # Parse and evaluate the expression safely
            result = self._safe_eval(expression)
            return f"The result of '{expression}' is: {result}"
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"

    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate a mathematical expression."""
        try:
            node = ast.parse(expression, mode='eval')
            return self._eval_node(node.body)
        except Exception as e:
            raise ValueError(f"Invalid mathematical expression: {e}")

    def _eval_node(self, node):
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](
                self._eval_node(node.left),
                self._eval_node(node.right)
            )
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self._eval_node(node.operand))
        else:
            raise TypeError(f"Unsupported operation: {type(node)}")

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's parameters."""
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to calculate (e.g., '2 + 3 * 4', '10 ** 2', '(5 + 3) / 2')"
                }
            },
            "required": ["expression"]
        }
