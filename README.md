# Naive Neuro-Symbolic

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███╗   ██╗ █████╗ ██╗██╗   ██╗███████╗                      ║
║   ████╗  ██║██╔══██╗██║██║   ██║██╔════╝                      ║
║   ██╔██╗ ██║███████║██║██║   ██║█████╗                        ║
║   ██║╚██╗██║██╔══██║██║╚██╗ ██╔╝██╔══╝                        ║
║   ██║ ╚████║██║  ██║██║ ╚████╔╝ ███████╗                      ║
║   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝                      ║
║                                                               ║
║        Neuro-Symbolic Reasoning: LLM + Prolog                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**A Proof of Concept - Minimal Toy Implementation**

---

## Overview

Naive Neuro-Symbolic is a minimal interactive command-line framework that demonstrates a hybrid neuro-symbolic workflow for solving logic problems. The system connects a Large Language Model (LLM) running locally via Ollama with SWI-Prolog using the janus-swi Python binding.

The workflow follows this pattern:

```
    ┌──────┐      ┌──────────┐      ┌────────┐      ┌─────────┐      ┌──────┐
    │ USER │─────>│   LLM    │─────>│ PROLOG │─────>│   LLM   │─────>│ USER │
    └──────┘      │ Translate│      │ Solve  │      │Translate│      └──────┘
     Natural      │  to      │      │ Logic  │      │  to     │      Natural
     Language     │ Prolog   │      │ Problem│      │ Language│      Language
                  └──────────┘      └────────┘      └─────────┘
```

## Why This Approach?

Research has shown that Logic Programming Machines (LPMs) like Prolog can outperform LLMs on structured reasoning tasks. Instead of asking an LLM to solve complex logic problems directly (which can lead to inconsistencies and errors), this framework uses the LLM to:
1. **Translate** natural language problem statements into formal Prolog code
2. **Execute** the Prolog program deterministically
3. **Translate** the Prolog results back into natural language

This hybrid approach leverages the strengths of both systems:
- **LLM**: Natural language understanding and generation
- **Prolog**: Deterministic constraint satisfaction and logical reasoning

## Architecture

The system implements a simple pipeline:

1. **User Input**: Natural language description of a logic problem
2. **LLM Translation (Step 1)**: Ollama (codellama:7b-instruct) converts the problem into Prolog code
3. **Prolog Execution**: SWI-Prolog solves the problem via janus-swi binding
4. **LLM Translation (Step 2)**: Ollama converts the Prolog output into human-readable text
5. **User Output**: Natural language solution

## Prerequisites

Before running this project, ensure you have:

```
┌────────────────────────────────────────────────────────┐
│  REQUIRED SOFTWARE                                     │
├────────────────────────────────────────────────────────┤
│  ✓ Python 3.8+                                         |
│  ✓ SWI-Prolog 9.0+         (system dependency)         |
│  ✓ Ollama                  (LLM runtime)               |
│  ✓ qwen2.5-coder:7b        (or compatible model)       |
└────────────────────────────────────────────────────────┘
```

**Detailed Requirements:**

- **Python 3.8+** installed
- **SWI-Prolog 9.0+** installed ([Download here](https://www.swi-prolog.org/))
  - Must be in system PATH
  - Required for `pyswip` to function
- **Ollama** installed and running ([Download here](https://ollama.com/))
  - Service must be active
- **LLM Model** pulled in Ollama (see recommended models below)

### Install SWI-Prolog

**Windows:**
```bash
# Download installer from https://www.swi-prolog.org/download/stable
# Run the installer and ensure SWI-Prolog is added to PATH
```

**macOS:**
```bash
brew install swi-prolog
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-add-repository ppa:swi-prolog/stable
sudo apt-get update
sudo apt-get install swi-prolog
```

### Install Ollama and Model

1. Install Ollama from [https://ollama.com/](https://ollama.com/)
2. Pull a recommended model:
```bash
# Recommended models (in order of quality for Prolog generation):
ollama pull qwen2.5-coder:7b          # Best for code generation
ollama pull deepseek-coder-v2:16b     # Excellent but larger
ollama pull llama3.1:8b-instruct      # Good balance
ollama pull codellama:7b-instruct     # Minimum (may struggle with complex logic)
```
3. Verify Ollama is running:
```bash
ollama list
```

**Note**: For best results with Prolog generation, use `qwen2.5-coder:7b` or larger models. Smaller models like `codellama:7b-instruct` may generate syntactically incorrect code for complex logic problems.

## Installation

### 1. Clone or Navigate to the Project Directory

```bash
cd Naive-Neuro-Symbolic
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows users**: If you encounter build errors, ensure SWI-Prolog is installed and in your system PATH before installing Python dependencies.

#### Python Dependencies

The project requires the following Python packages:

| Package | Purpose | Notes |
|---------|---------|-------|
| `ollama` | LLM client for interacting with Ollama | Handles HTTP communication with local Ollama instance |
| `pyswip` | Python-Prolog bridge for SWI-Prolog | Enables Python to execute Prolog code directly |

**Sub-dependencies** (automatically installed):
- `httpx>=0.27` - HTTP client for Ollama API calls
- `pydantic>=2.9` - Data validation for Ollama responses
- `certifi` - SSL certificate verification
- `idna` - Internationalized domain names support

**System Requirements:**
- Python 3.8 or higher
- SWI-Prolog 9.0 or higher (must be installed separately and in PATH)
- Ollama running locally

## Usage

### Starting the Interactive Chat

With your virtual environment activated:

```bash
python naive_neurosym.py
```

### Interacting with the System

1. The system will prompt you to enter a logic problem
2. Type your problem in natural language
3. The system will:
   - Convert your problem to Prolog
   - Save the Prolog code to `prolog_programs/`
   - Execute the Prolog program
   - Translate the result back to natural language
   - Display the solution
4. Type `exit`, `quit`, or press `Ctrl+C` to quit

### Example Session

```
======================================
  Naive Neuro-Symbolic System
  User > LLM > Prolog > LLM > User
======================================

Enter a logic problem (or 'exit' to quit):
> Three people (Alice, Bob, Carol) each have a different pet (cat, dog, bird) and live in different colored houses (red, blue, green). Alice does not have a cat. Bob lives in the red house. The person with the dog lives in the blue house. Carol does not live in the green house. Who has which pet and lives in which house?

[Converting problem to Prolog...]
[Prolog code saved to: prolog_programs/problem_20250104_143022.pl]
[Executing Prolog program...]
[Translating results to natural language...]

Solution:
Alice has the bird and lives in the green house.
Bob has the cat and lives in the red house.
Carol has the dog and lives in the blue house.

Enter a logic problem (or 'exit' to quit):
> exit

Goodbye!
```

## How It Works

### 1. Problem to Prolog Translation

The system sends your problem to the LLM with a carefully crafted prompt that instructs it to generate **only** valid Prolog code with inline comments. No explanations outside the code are allowed. This ensures clean, executable Prolog output.

### 2. Prolog Code Storage

Each generated Prolog program is saved to the `prolog_programs/` directory with a timestamp. This allows you to:
- Review the generated code
- Debug issues
- Reuse or modify solutions

### 3. Prolog Execution

The system uses `pyswip`, a Python-Prolog bridge that allows direct interaction with SWI-Prolog from Python. The Prolog program is executed, and results are captured.

### 4. Result Translation

The raw Prolog output is sent back to the LLM with the original problem context. The LLM translates the formal Prolog solution into natural, human-readable language.

### 5. Error Handling

If any step fails (LLM unavailable, invalid Prolog code, execution error), the system provides clear error messages and continues running.

## Project Structure

```
LLM-prolog-binding/
├── README.md              # This file - complete documentation
├── requirements.txt       # Python dependencies (minimal)
├── naive_neurosym.py      # Main script (heavily commented)
└── prolog_programs/       # Generated Prolog files (created automatically)
    └── problem_*.pl       # Timestamped Prolog programs
```

### Dependencies Tree

```
naive_neurosym.py
├── ollama (Python package)
│   ├── httpx>=0.27
│   │   ├── httpcore==1.*
│   │   │   └── h11>=0.16
│   │   ├── certifi
│   │   ├── idna
│   │   └── anyio
│   │       └── sniffio>=1.1
│   └── pydantic>=2.9
│       ├── pydantic-core==2.41.4
│       ├── typing-extensions>=4.14.1
│       ├── typing-inspection>=0.4.2
│       └── annotated-types>=0.6.0
│
└── pyswip (Python package)
    └── SWI-Prolog 9.0+ (system dependency)
```

## Implementation Notes

This is a **Proof of Concept (PoC)** - emphasis on minimalism:
- No over-engineering
- Every line is commented
- Simple, readable code
- Minimal dependencies
- Direct, straightforward workflow

## Testing

You can test the system with the classic "Tea Party Puzzle" from the research paper:

```
Three guests (Ada, Babbage, Turing) each brought different tea (Earl Grey, Darjeeling, Chamomile), 
wore different colored hats (red, blue, green), and sat in different chairs (left, middle, right).

Clues:
1. The person in the middle seat wore the blue hat
2. Ada sat to the left of the person who brought Darjeeling
3. The guest in the red hat brought Chamomile
4. Babbage did not sit on the left
5. Turing wore the green hat
6. The person who brought Earl Grey sat immediately next to the person who wore the red hat

Who sat where with what tea and hat?
```

## Model Performance Testing

```
╔═══════════════════════════════════════════════════════════════╗
║                    LLM MODEL TEST RESULTS                     ║
╚═══════════════════════════════════════════════════════════════╝
```

During development, various models were tested for Prolog code generation:

| Model | Status | Notes |
|-------|--------|-------|
| **qwen2.5-coder:7b** | ✅ **SUCCESS** | Best performer - generates valid, efficient Prolog for simple problems |
| codellama:7b-instruct | ❌ Failed | Generates syntactically incorrect code |
| DeepSeek-Coder 6.7B | ❌ Failed | Poor Prolog syntax understanding |
| Phi-2 | ❌ Failed | Cannot generate valid Prolog |
| StarCoderBase 7B | ❌ Failed | Struggles with logic programming paradigm |
| TinyLlama | ❌ Failed | Too small for complex code generation |

### Key Findings

1. **Prompt Engineering is Critical**: The quality of generated Prolog code is highly dependent on precise, well-structured prompts with:
   - Explicit examples showing correct patterns
   - Clear warnings about common pitfalls (e.g., infinite loops with undefined domains)
   - Step-by-step structure guidance
   - Concrete syntax rules

2. **Model Size Matters**: Smaller models (<7B parameters) consistently fail to generate valid Prolog, even with excellent prompts.

3. **Code-Specialized Models Excel**: Models trained specifically for code generation (like qwen2.5-coder) significantly outperform general instruction models.

## Generated Files Naming Convention

```
    ┌─────────────────────────────────────────────┐
    │  prolog_programs/problem_YYYYMMDD_HHMMSS.pl │
    └─────────────────────────────────────────────┘
              │           │        │
              │           │        └─► Time (24h format)
              │           └─────────► Date
              └─────────────────────► Prefix
```

All generated Prolog programs are automatically saved in the `prolog_programs/` directory with a timestamp-based naming scheme:

- **Format**: `problem_YYYYMMDD_HHMMSS.pl`
- **Example**: `problem_20251104_143022.pl`
  - Generated on: November 4, 2025
  - At: 14:30:22 (2:30:22 PM)

**Benefits of this approach:**
- Chronological ordering (easy to find recent attempts)
- No filename conflicts (each file is unique)
- Debugging friendly (can compare different generations)
- Historical record of LLM performance

## Limitations

As a minimal PoC, this system has intentional limitations:

```
    ⚠ This is a TOY IMPLEMENTATION - Basic Proof of Concept ⚠
```

**Current Limitations:**
- Works best with **simple, well-defined logic puzzles**
- Dependent on the quality of the LLM's Prolog generation
- No conversation memory between problems
- Single-shot generation (no iterative refinement)
- Basic error handling
- No automatic code validation before execution

**Potential Improvements** (not implemented - requires research):
- Multi-shot generation with validation feedback loop
- Automatic syntax checking and correction
- Support for more complex Prolog features (CLP, DCGs)
- Integration with constraint solvers (CLP(FD), CLP(R))
- Interactive debugging when Prolog execution fails
- Performance optimization for large search spaces
- Support for probabilistic logic programming

## References

This project is inspired by research on hybrid neuro-symbolic approaches:

- [When Prolog Beats the LLM That Created It](https://www.embedded-commerce.com/prolog_vs_llm_logic_paper.html)
- [LLM and Prolog: The Logical Alternative to Chain-of-Thought Reasoning](https://medium.com/gft-engineering/llm-and-prolog-the-logical-alternative-to-chain-of-thought-reasoning-cdf3f4805153)
- [Ollama - codellama:7b-instruct](https://ollama.com/library/codellama:7b-instruct)
- [SWI-Prolog](https://www.swi-prolog.org/)
- [pyswip on PyPI](https://pypi.org/project/pyswip/)
- [pyswip on GitHub](https://github.com/yuce/pyswip)

---

**License**: MIT  
**Status**: Proof of Concept  
**Contributions**: Welcome


