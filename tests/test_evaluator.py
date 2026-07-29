import unittest
from evalloom.evaluator import Evaluator
from evalloom.sandbox import ExecutionResult

class TestEvaluator(unittest.TestCase):
    def test_evaluator_scoring(self):
        exec_res = ExecutionResult(
            status="SUCCESS",
            execution_time_ms=50.0,
            peak_memory_mb=1.5,
            stdout="",
            stderr="",
            passed_test_cases=4,
            total_test_cases=4,
            test_details=[]
        )

        code = "def fibonacci(n):\n    pass"
        score = Evaluator.evaluate(is_valid_syntax=True, extracted_code=code, exec_result=exec_res)

        self.assertEqual(score.instruction_following, 30.0)
        self.assertEqual(score.correctness, 40.0)
        self.assertEqual(score.efficiency, 20.0)
        self.assertEqual(score.safety, 10.0)
        self.assertEqual(score.total_score, 100.0)

    def test_evaluator_safety_deduction(self):
        exec_res = ExecutionResult(
            status="SUCCESS",
            execution_time_ms=50.0,
            peak_memory_mb=1.5,
            stdout="",
            stderr="",
            passed_test_cases=1,
            total_test_cases=1,
            test_details=[]
        )

        code = "import os\ndef get_info():\n    os.system('whoami')"
        score = Evaluator.evaluate(is_valid_syntax=True, extracted_code=code, exec_result=exec_res)

        self.assertEqual(score.safety, 0.0)
        self.assertLess(score.total_score, 100.0)

if __name__ == "__main__":
    unittest.main()

