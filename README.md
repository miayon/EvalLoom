# EvalLoom — Automated LLM Code Evaluation & Red-Teaming Suite

EvalLoom is a high-performance Python evaluation and benchmarking framework designed to execute, sandbox, and evaluate Large Language Model (LLM) code outputs against real-world test cases, edge conditions, efficiency constraints, and red-teaming checks.

---

## Features

- **Multi-Model Concurrency**: Concurrent side-by-side prompt executions via `asyncio`.
- **Clean Code Extraction**: Regex & AST-backed parsing for Python, JS, and C++.
- **Isolated Sandbox Subprocess Execution**: Safe execution with hard timeouts (default 5s), return code analysis, and stdout/stderr metric tracking.
- **Weighted Scoring Algorithm**: 
  - **Instruction Following (30%)**
  - **Correctness & Edge Case Pass Rate (40%)**
  - **Efficiency & Execution Speed (20%)**
  - **Safety & Red-Teaming (10%)**
- **Markdown Audit Reports**: Automatic side-by-side code diffs, pass rates, and critique notes (`outputs/EVALUATION_REPORT.md`).
- **Mock & Live Modes**: Seamless offline testing without API key dependencies, or live evaluation using Google Gemini, OpenAI, or Anthropic.

---

## File Structure

```text
evalloom/
├── benchmarks/
│   └── coding_prompts.json       # Benchmark prompts & test cases
├── evalloom/
│   ├── __init__.py
│   ├── api_runner.py            # Async LLM connector & Mock provider
│   ├── code_parser.py           # AST & Regex code block extractor
│   ├── sandbox.py               # Subprocess isolated execution engine
│   ├── evaluator.py             # Weighted 0-100 scoring logic
│   └── reporter.py              # Markdown report builder
├── tests/
│   ├── test_sandbox.py          # Unit tests for sandbox engine
│   └── test_evaluator.py        # Unit tests for scoring engine
├── outputs/
│   └── EVALUATION_REPORT.md     # Auto-generated markdown evaluation report
├── .env.example                 # Environment variables template
├── main.py                      # CLI entrypoint
├── requirements.txt             # Dependencies
└── README.md                    # Project documentation
```

---

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Run Offline Benchmark (Mock Mode)

```bash
python main.py --mock
```

### 3. Run Live Benchmark with API Keys

Set your API keys in `.env` or environment variables:
```bash
cp .env.example .env
# Edit .env with GEMINI_API_KEY, OPENAI_API_KEY, etc.
```

Run live evaluation:
```bash
python main.py --live --model-a gemini-2.5-flash --model-b gpt-4o-mini
```

---

## Running Unit Tests

```bash
python -m unittest discover -s tests
```
