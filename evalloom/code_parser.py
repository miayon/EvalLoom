import re
import ast

class CodeParser:
    """Extracts and validates code blocks from LLM output."""

    @staticmethod
    def extract_code(raw_text: str, target_language: str = "python") -> str:
        """
        Extract code block from raw LLM output.
        Looks for markdown fenced code blocks (```python ... ```) or returns raw text if cleaned.
        """
        if not raw_text:
            return ""

        # Pattern for markdown code block
        pattern = rf"```(?:{target_language}|py|js|cpp)?\s*\n(.*?)```"
        matches = re.findall(pattern, raw_text, re.DOTALL | re.IGNORECASE)

        if matches:
            return matches[0].strip()

        # Fallback: if text starts with code lines without fences
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()

        return cleaned

    @staticmethod
    def validate_python_syntax(code: str) -> tuple[bool, str]:
        """
        Validates Python syntax using Python's AST parser.
        Returns (is_valid, error_message).
        """
        if not code.strip():
            return False, "Empty code snippet"
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"SyntaxError line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
