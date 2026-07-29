import unittest
from evalloom.code_parser import CodeParser
from evalloom.sandbox import CodeSandbox

class TestSandbox(unittest.TestCase):
    def test_code_parser_extract(self):
        raw = "Here is your solution:\n```python\ndef add(a, b):\n    return a + b\n```\nHope this helps!"
        extracted = CodeParser.extract_code(raw, "python")
        self.assertEqual(extracted, "def add(a, b):\n    return a + b")

    def test_code_parser_valid_syntax(self):
        valid, err = CodeParser.validate_python_syntax("def foo(): pass")
        self.assertTrue(valid)
        self.assertEqual(err, "")

        invalid, err = CodeParser.validate_python_syntax("def foo():")
        self.assertFalse(valid_syntax if 'valid_syntax' in locals() else invalid)
        self.assertIn("SyntaxError", err)

    def test_sandbox_success(self):
        sandbox = CodeSandbox(timeout_seconds=2.0)
        code = "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)"
        test_cases = [{"input": "fibonacci(5)", "expected": "5"}]
        res = sandbox.execute_python_code(code, test_cases)
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.passed_test_cases, 1)

    def test_sandbox_timeout(self):
        sandbox = CodeSandbox(timeout_seconds=1.0)
        code = "import time\ntime.sleep(3)"
        test_cases = [{"input": "1", "expected": "1"}]
        res = sandbox.execute_python_code(code, test_cases)
        self.assertEqual(res.status, "TIMEOUT")
        self.assertEqual(res.passed_test_cases, 0)

if __name__ == "__main__":
    unittest.main()

