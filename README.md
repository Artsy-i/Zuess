# ZEUSS — Autonomous B2B Intelligence Pipeline

<div align="center">

<img src="https://raw.githubusercontent.com/Artsy-i/Zuess/main/assets/zeuss-banner.png" alt="ZEUSS Banner" width="100%" />

</div>

> Autonomous B2B industry intelligence system engineered for grounded research, chapter-based synthesis, QA verification, and institutional report generation.

A Python-powered research and publishing engine that turns a topic into a multi-chapter, institutionally styled intelligence dossier using layered AI orchestration, source-grounded fact extraction, and failover-safe execution.

## Why ZEUSS

ZEUSS was built to solve a specific problem: producing professional-grade B2B market intelligence with stronger evidence discipline than typical AI-generated reports.

It does this by combining:

- Grounded fact collection from whitelisted research sources
- Multi-provider LLM failover with checkpoint handoff
- Structured synthesis into chapter-based reports
- Adversarial QA gating against the original fact set
- Institutional PDF publishing and commercial verdict generation

## Key capabilities

- Search and extract grounded facts from trusted domains (.gov, McKinsey, Bloomberg)
- Synthesize chapter-specific market intelligence
- Audit all claims before approval
- Generate publication-ready PDF dossiers
- Produce a commercial council decision after publication
- Resume work from saved chapter state when interrupted

## Repository at a glance

```text
ZEUSS/
├── main.py                  # Entry point, CLI, dashboard, pipeline orchestration
├── llm_router.py           # Failover routing, JSON repair, provider selection
├── orchestrator.py          # Orchestrator-mode command loop
├── pdf_generator.py         # Institutional PDF compiler
├── mcp.json                # MCP server config
├── requirements.txt        # Python dependencies
├── README.md               # Project overview and quick start
├── LICENSE.md              # Software license
├── LEGAL_NOTICE.md         # Copyright and usage notice
├── ARCHITECTURE.md         # Technical architecture
├── API_REFERENCE.md        # Public interfaces and responsibilities
├── SETUP_GUIDE.md          # Setup and environment instructions
├── research_cache/         # Cached chapter states and checkpoints
├── final_reports/          # Output PDF dossiers
├── logs/                  # QA and execution logs
└── skills/                # Prompt skill packs for synthesis and audit tasks
```

## Quick start

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment

Create a `.env` file:

```bash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_API_KEY_2=your_key_here
OPENROUTER_API_KEY_3=your_key_here
EXA_API_KEY=your_key_here
```

### 3) Run the pipeline

```bash
python main.py --topic "AI Supply Chain 2026"
```

Optional flags:

```bash
python main.py --topic "AI Supply Chain 2026" --resume
python main.py --topic "AI Supply Chain 2026" --auto-approve
```

## Execution model

```text
Topic input
   ↓
Chapter 1 → Node A → Node B → Node C
Chapter 2 → Node A → Node B → Node C
Chapter 3 → Node A → Node B → Node C
Chapter 4 → Node A → Node B → Node C
   ↓
Node D → Compile institutional PDF
   ↓
Node E → Commercial council verdict
```

## Primary files

### main.py
Main runtime for orchestration, dashboard UI, chapter execution, and publication flow.

### llm_router.py
Contains provider failover logic, prompt-based checkpoints, fallback rotations, and JSON repair routines used to keep generation resilient.

### pdf_generator.py
Generates formal multi-chapter PDF output with dedicated cover pages, section formatting, and source ledger tables.

### orchestrator.py
Alternative orchestrator loop for coordinating tasks and responding to LLM-issued runtime commands.

## Architecture notes

ZEUSS uses a layered architecture built around a deterministic state machine:

- Search stage gathers grounded facts
- Synthesis stage writes chapter narratives
- QA stage verifies claims against sourced evidence
- Publishing stage compiles the report
- Commercial review stage weighs the final business angle

The system is intentionally strict about source validation and avoids silent estimation. If evidence is missing, it is surfaced clearly instead of being guessed.

## Configuration and requirements

See:

- `SETUP_GUIDE.md`
- `API_REFERENCE.md`
- `ARCHITECTURE.md`

## Legal protection

This project includes copyright and legal notice documentation to help protect the code and project materials.

- `LICENSE.md`
- `LEGAL_NOTICE.md`

## License

This project is protected under copyright and is intended for proprietary use unless otherwise stated in the repository license file.

## Project status

This repository is a custom AI research and publishing system under active development. It is intended for internal or controlled deployment use, depending on the license terms in effect in your environment.

## Support

For repository issues, use the GitHub Issues tracker for this project.

---

Made for ZEUSS by Artsy-i.
