import argparse
import json
import asyncio
import os
import sys
from dotenv import load_dotenv

from evalloom.api_runner import APIRunner, PromptExecutionResult
from evalloom.code_parser import CodeParser
from evalloom.sandbox import CodeSandbox
from evalloom.evaluator import Evaluator
from evalloom.reporter import ReportGenerator

load_dotenv()

async def run_benchmark(
    benchmarks_path: str,
    model_a: str,
    model_b: str,
    mock: bool,
    output_path: str
):
    print(f"=== Starting EvalLoom Benchmark Suite ===")
    print(f"   Benchmark dataset: {benchmarks_path}")
    print(f"   Model A: {model_a}")
    print(f"   Model B: {model_b}")
    print(f"   Mode: {'MOCK (Offline)' if mock else 'LIVE (API)'}")
    print("-" * 50)

    if not os.path.exists(benchmarks_path):
        print(f"Error: Benchmark file not found at {benchmarks_path}")
        sys.exit(1)

    with open(benchmarks_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    runner = APIRunner(mock=mock)
    sandbox = CodeSandbox(timeout_seconds=5.0)

    results_a: list[PromptExecutionResult] = []
    results_b: list[PromptExecutionResult] = []

    for item in prompts:
        prompt_id = item["id"]
        prompt_title = item.get("title", prompt_id)
        print(f"  * Running prompt: [{prompt_id}] {prompt_title}...")

        # Run models concurrently
        raw_a_task = runner.run_prompt(model_a, item)
        raw_b_task = runner.run_prompt(model_b, item)
        raw_a, raw_b = await asyncio.gather(raw_a_task, raw_b_task)

        # Process Model A
        extracted_a = CodeParser.extract_code(raw_a, item.get("language", "python"))
        is_valid_a, _ = CodeParser.validate_python_syntax(extracted_a)
        exec_a = sandbox.execute_python_code(extracted_a, item.get("test_cases", []))
        score_a = Evaluator.evaluate(is_valid_a, extracted_a, exec_a, item.get("category", "Coding"))

        res_a = PromptExecutionResult(
            model_name=model_a,
            prompt_id=prompt_id,
            prompt_title=prompt_title,
            raw_response=raw_a,
            extracted_code=extracted_a,
            is_valid_syntax=is_valid_a,
            execution_result=exec_a,
            score=score_a
        )
        results_a.append(res_a)

        # Process Model B
        extracted_b = CodeParser.extract_code(raw_b, item.get("language", "python"))
        is_valid_b, _ = CodeParser.validate_python_syntax(extracted_b)
        exec_b = sandbox.execute_python_code(extracted_b, item.get("test_cases", []))
        score_b = Evaluator.evaluate(is_valid_b, extracted_b, exec_b, item.get("category", "Coding"))

        res_b = PromptExecutionResult(
            model_name=model_b,
            prompt_id=prompt_id,
            prompt_title=prompt_title,
            raw_response=raw_b,
            extracted_code=extracted_b,
            is_valid_syntax=is_valid_b,
            execution_result=exec_b,
            score=score_b
        )
        results_b.append(res_b)

    print("-" * 50)
    print(f"Generating Markdown report to: {output_path}")
    ReportGenerator.generate_report(
        model_a_name=model_a,
        model_b_name=model_b,
        results_a=results_a,
        results_b=results_b,
        output_filepath=output_path
    )
    print(f"[SUCCESS] EvalLoom benchmark complete! Check output at {output_path}")

def main():
    parser = argparse.ArgumentParser(description="EvalLoom — Automated LLM Code Evaluation & Red-Teaming Suite")
    parser.add_argument("--benchmarks", type=str, default="benchmarks/coding_prompts.json", help="Path to benchmarks JSON file")
    parser.add_argument("--model-a", type=str, default="Model_A_Optimized", help="Name or API identifier for Model A")
    parser.add_argument("--model-b", type=str, default="Model_B_Baseline", help="Name or API identifier for Model B")
    parser.add_argument("--mock", action="store_true", default=True, help="Run in mock mode without invoking real LLM APIs")
    parser.add_argument("--live", action="store_false", dest="mock", help="Run in live API mode using API keys from environment")
    parser.add_argument("--output", type=str, default="outputs/EVALUATION_REPORT.md", help="Path to output Markdown report")

    args = parser.parse_args()

    asyncio.run(run_benchmark(
        benchmarks_path=args.benchmarks,
        model_a=args.model_a,
        model_b=args.model_b,
        mock=args.mock,
        output_path=args.output
    ))

if __name__ == "__main__":
    main()
