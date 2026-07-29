import os
from typing import List, Dict, Any
from evalloom.api_runner import PromptExecutionResult

class ReportGenerator:
    """Generates structured Markdown evaluation reports (EVALUATION_REPORT.md)."""

    @staticmethod
    def generate_report(
        model_a_name: str,
        model_b_name: str,
        results_a: List[PromptExecutionResult],
        results_b: List[PromptExecutionResult],
        output_filepath: str = "outputs/EVALUATION_REPORT.md"
    ) -> str:
        
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

        def calc_metrics(results: List[PromptExecutionResult]):
            total = len(results)
            if total == 0:
                return 0, 0, 0, 0
            avg_score = sum(r.score.total_score for r in results) / total
            passed_tests = sum(1 for r in results if r.execution_result.status == "SUCCESS")
            pass_rate = (passed_tests / total) * 100
            avg_speed = sum(r.execution_result.execution_time_ms for r in results) / total
            syntax_errors = sum(1 for r in results if not r.is_valid_syntax)
            return round(avg_score, 1), round(pass_rate, 1), round(avg_speed, 1), syntax_errors

        score_a, pass_a, speed_a, syntax_a = calc_metrics(results_a)
        score_b, pass_b, speed_b, syntax_b = calc_metrics(results_b)

        winner = model_a_name if score_a >= score_b else model_b_name

        md = []
        md.append("# EvalLoom — LLM Code Evaluation & Red-Teaming Report\n")
        md.append(f"**Benchmark Summary:** Comparing **{model_a_name}** vs **{model_b_name}**  ")
        md.append(f"**Winner:** 🏆 `{winner}`\n")
        md.append("---\n")

        # Summary Table
        md.append("## 📊 Executive Summary Table\n")
        md.append("| Metric | " + model_a_name + " | " + model_b_name + " |")
        md.append("| :--- | :---: | :---: |")
        md.append(f"| **Overall Weighted Score (0-100)** | **{score_a}** | **{score_b}** |")
        md.append(f"| **Test Case Pass Rate (%)** | {pass_a}% | {pass_b}% |")
        md.append(f"| **Avg Execution Speed (ms)** | {speed_a} ms | {speed_b} ms |")
        md.append(f"| **Syntax Errors** | {syntax_a} | {syntax_b} |\n")

        # Side-by-side prompt breakdowns
        md.append("## 🔍 Detailed Prompt Evaluations\n")

        for idx, (res_a, res_b) in enumerate(zip(results_a, results_b), 1):
            md.append(f"### Prompt #{idx}: {res_a.prompt_title} (`{res_a.prompt_id}`)\n")
            md.append(f"**Scores:** `{model_a_name}`: {res_a.score.total_score}/100 | `{model_b_name}`: {res_b.score.total_score}/100\n")

            md.append("#### Side-by-Side Generated Code\n")
            md.append(f"**{model_a_name}:**")
            md.append("```python\n" + res_a.extracted_code + "\n```\n")

            md.append(f"**{model_b_name}:**")
            md.append("```python\n" + res_b.extracted_code + "\n```\n")

            md.append("#### Execution Details & Diagnostics")
            md.append(f"- **{model_a_name}**: Status = `{res_a.execution_result.status}`, Time = `{res_a.execution_result.execution_time_ms} ms`, Passed = `{res_a.execution_result.passed_test_cases}/{res_a.execution_result.total_test_cases}`")
            md.append(f"- **{model_b_name}**: Status = `{res_b.execution_result.status}`, Time = `{res_b.execution_result.execution_time_ms} ms`, Passed = `{res_b.execution_result.passed_test_cases}/{res_b.execution_result.total_test_cases}`\n")
            md.append("---\n")

        # Critique Section
        md.append("## 💡 Automated Critique Notes\n")
        if score_a > score_b:
            md.append(f"- **{model_a_name}** demonstrated superior accuracy and edge case handling compared to {model_b_name}.")
        elif score_b > score_a:
            md.append(f"- **{model_b_name}** demonstrated superior accuracy and edge case handling compared to {model_a_name}.")
        else:
            md.append("- Both models achieved identical overall weighted evaluation scores across the benchmark suite.")

        report_content = "\n".join(md)

        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(report_content)

        return report_content
