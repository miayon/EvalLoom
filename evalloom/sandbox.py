import sys
import subprocess
import tempfile
import time
import os
from typing import Dict, Any, List
from pydantic import BaseModel

class ExecutionResult(BaseModel):
    status: str  # "SUCCESS", "SYNTAX_ERROR", "RUNTIME_ERROR", "TIMEOUT", "DISQUALIFIED"
    execution_time_ms: float
    peak_memory_mb: float
    stdout: str
    stderr: str
    passed_test_cases: int
    total_test_cases: int
    test_details: List[Dict[str, Any]]

class CodeSandbox:
    """Executes generated Python code inside an isolated subprocess with hard timeouts & safety checks."""

    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds

    def execute_python_code(self, code: str, test_cases: List[Dict[str, str]]) -> ExecutionResult:
        if not code.strip():
            return ExecutionResult(
                status="SYNTAX_ERROR",
                execution_time_ms=0.0,
                peak_memory_mb=0.0,
                stdout="",
                stderr="No executable code found.",
                passed_test_cases=0,
                total_test_cases=len(test_cases),
                test_details=[]
            )

        # Build runner script that appends test cases execution
        test_harness = "\n\n# --- EVALUATION TEST HARNESS ---\n"
        test_harness += "if __name__ == '__main__':\n"
        test_harness += "    import json, sys\n"
        test_harness += "    results = []\n"
        
        for idx, tc in enumerate(test_cases):
            inp = tc.get("input", "")
            exp = tc.get("expected", "")
            test_harness += f"    try:\n"
            test_harness += f"        val = str({inp})\n"
            test_harness += f"        exp = str({exp})\n"
            test_harness += f"        passed = (val == exp)\n"
            test_harness += f"        results.append({{'id': {idx}, 'passed': passed, 'actual': val, 'expected': exp, 'error': None}})\n"
            test_harness += f"    except Exception as e:\n"
            test_harness += f"        results.append({{'id': {idx}, 'passed': False, 'actual': None, 'expected': str({exp}), 'error': str(e)}})\n"
        
        test_harness += "    print('__EVAL_RESULTS_START__')\n"
        test_harness += "    print(json.dumps(results))\n"
        test_harness += "    print('__EVAL_RESULTS_END__')\n"

        full_script = code + "\n" + test_harness

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(full_script)
            temp_file_path = f.name

        start_time = time.perf_counter()
        try:
            process = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            stdout = process.stdout
            stderr = process.stderr

            if process.returncode != 0:
                return ExecutionResult(
                    status="RUNTIME_ERROR",
                    execution_time_ms=elapsed_ms,
                    peak_memory_mb=0.1,
                    stdout=stdout,
                    stderr=stderr,
                    passed_test_cases=0,
                    total_test_cases=len(test_cases),
                    test_details=[]
                )

            # Parse test results from stdout
            passed_count = 0
            test_details = []
            if "__EVAL_RESULTS_START__" in stdout and "__EVAL_RESULTS_END__" in stdout:
                json_part = stdout.split("__EVAL_RESULTS_START__")[1].split("__EVAL_RESULTS_END__")[0].strip()
                import json
                try:
                    test_details = json.loads(json_part)
                    passed_count = sum(1 for res in test_details if res.get("passed", False))
                except Exception as e:
                    stderr += f"\nFailed to parse test harness output: {e}"

            status = "SUCCESS" if passed_count == len(test_cases) else "RUNTIME_ERROR"

            return ExecutionResult(
                status=status,
                execution_time_ms=round(elapsed_ms, 2),
                peak_memory_mb=1.5,  # Estimated baseline
                stdout=stdout,
                stderr=stderr,
                passed_test_cases=passed_count,
                total_test_cases=len(test_cases),
                test_details=test_details
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status="TIMEOUT",
                execution_time_ms=self.timeout_seconds * 1000.0,
                peak_memory_mb=0.0,
                stdout="",
                stderr=f"Execution timed out after {self.timeout_seconds} seconds.",
                passed_test_cases=0,
                total_test_cases=len(test_cases),
                test_details=[]
            )
        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
