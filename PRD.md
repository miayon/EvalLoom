# Product Requirement Document (PRD): EvalLoom
**Project Name:** EvalLoom — Automated LLM Code Evaluation & Red-Teaming Suite  
**Version:** 1.0.0  
**Target Goal:** An automated CLI and reporting engine to benchmark, sand-box, and evaluate LLM-generated code outputs against real-world test cases, edge conditions, and execution metrics.

---

## 1. Executive Summary & Objective
EvalLoom is a lightweight Python evaluation suite designed to automate the process of testing, rating, and benchmarking Large Language Model (LLM) outputs—specifically focusing on code generation (Python, JavaScript, C++). 

The system executes side-by-side prompt runs across multiple LLM endpoints, runs the resulting code inside isolated sandboxed subprocesses, tracks execution metrics (time, memory, status), detects silent logical bugs/hallucinations, and exports structured, audit-ready Markdown evaluation reports.

---

## 2. Core Functional Requirements

### Feature 1: Multi-Model Prompt Execution Engine
* **Input:** A structured JSON benchmark file (`prompts.json`) containing prompt items, categories (Coding, Logic, Red-Teaming), expected output patterns, and test cases.
* **LLM Integration:** Supports calling at least two major LLM provider APIs (e.g., Google Gemini API, OpenAI API, or Anthropic API) or simulated local models.
* **Concurrency:** Runs prompt executions concurrently using Python's `asyncio` or `concurrent.futures` to maximize throughput.

### Feature 2: Sandboxed Code Extraction & Execution Sandbox
* **Code Parsing:** Uses regex/AST parsers to cleanly extract code blocks (Python, JS, C++) from raw LLM responses.
* **Isolated Execution:** Executes the extracted code in an isolated, secure subprocess using `subprocess.run` with hard timeouts (e.g., 5-second max runtime limit per test).
* **Metric Capture:** Captures:
  * Exit Status (Success, SyntaxError, RuntimeError, Timeout)
  * Execution Time (in milliseconds)
  * Peak Memory Allocation
  * Standard Output (`stdout`) and Standard Error (`stderr`)

### Feature 3: Automated Scoring & Evaluation Engine
Calculates a weighted metric score (0 to 100) based on strict AI evaluation criteria:
1. **Instruction Following (30%):** Did the model output valid syntax and strictly follow formatting constraints?
2. **Correctness & Pass Rate (40%):** Did the generated code pass 100% of defined edge-case inputs?
3. **Efficiency (20%):** Did execution complete within expected time/memory thresholds?
4. **Safety & Red-Teaming (10%):** Did the response avoid executing malicious or unhandled dangerous calls?

### Feature 4: Markdown Evaluation Report Generator
* Generates an audit-grade Markdown report file (`EVALUATION_REPORT.md`) after every evaluation run.
* Includes:
  * Summary table comparing Model A vs Model B (Pass Rate, Avg Speed, Syntax Error Rate).
  * Side-by-side code diffs and execution output logs.
  * Auto-generated critique notes detailing why Model A outperformed Model B.

---

## 3. Project File Architecture
```text
evalloom/
├── benchmarks/
│   └── coding_prompts.json       # JSON file containing test prompts & test cases
├── evalloom/
│   ├── __init__.py
│   ├── api_runner.py            # API connection & prompt execution
│   ├── code_parser.py           # Regex/AST code extractor
│   ├── sandbox.py               # Subprocess code execution engine
│   ├── evaluator.py             # Scoring algorithm logic
│   └── reporter.py              # Markdown report builder
├── tests/
│   ├── test_sandbox.py          # Pytest unit tests for execution runner
│   └── test_evaluator.py        # Pytest unit tests for scoring engine
├── outputs/
│   └── EVALUATION_REPORT.md     # Generated output report
├── .env.example                 # API key templates (GEMINI_API_KEY, OPENAI_API_KEY)
├── main.py                      # CLI entry point
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation