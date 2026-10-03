# ZEUSS Architecture

## Overview

ZEUSS is a multi-stage autonomous research engine for B2B industry intelligence. It takes a user topic, gathers grounded facts, synthesizes chapter-based analysis, audits the output, and publishes a structured institutional dossier.

The system is organized as a state-driven workflow with explicit progression between stages.

## High-level flow

```text
User Topic
   ↓
Search Stage (Node A)
   ↓
Synthesis Stage (Node B)
   ↓
QA Verification Stage (Node C)
   ↓
Publishing Stage (Node D)
   ↓
Commercial Council Stage (Node E)
```

## System responsibilities

### Node A — Searcher

Responsible for:

- Determining the topic and chapter scope
- Searching authoritative domains
- Collecting grounded evidence
- Formatting facts into structured JSON data

This stage uses knowledge sources and whitelists to minimize hallucination and noise.

### Node B — Synthesizer

Responsible for:

- Transforming fact data into long-form chapter content
- Writing dense institutional prose with structured headings
- Maintaining explicit citation and source discipline
- Avoiding speculative numbers and unsupported estimates

### Node C — QA Auditor

Responsible for:

- Cross-verifying each claim and metric against source facts
- Rejecting unsupported numerical statements
- Returning approval or rejection with a confidence score
- Driving loop rework if conclusions do not meet evidence standards

### Node D — Institutional Publisher

Responsible for:

- Compiling approved chapters into a single report
- Building cover pages, executive preface, and source ledger
- Generating an institutional PDF output for final use

### Node E — Commercial Council

Responsible for:

- Summarizing the final report
- Running parallel expert persona evaluations
- Delivering a final council verdict and recommendation

## Files and responsibilities

### main.py

This is the primary execution layer. It initializes the Rich terminal dashboard,
processes chapter states, runs publication logic, and triggers the final commercial review.

### llm_router.py

This file centralizes provider routing and failover. It includes retry logic,
checkpoint behavior, and JSON repair for responses that come back malformed or truncated.

### pdf_generator.py

This file assembles the formal report layout and writes the final PDF through ReportLab.

### orchestrator.py

This module offers a command-driven orchestration mode that can delegate tasks by issuing runtime commands to the research engine.

## State model

The system moves through similar lifecycle states such as:

- INITIAL
- SEARCH_COMPLETE
- SYNTHESIS_COMPLETE
- QA_REJECTED
- QA_APPROVED
- PUBLISHED
- COMMERCIAL_COUNCIL_COMPLETE

This state model ensures the system pauses only when evidence quality is acceptable.

## Fail-safe design

One of ZEUSS's core strengths is resilience. If a provider fails:

1. The current accumulation is checkpointed
2. The model attempts the next provider in the rotation
3. The prompt is adjusted to continue from the saved checkpoint
4. Execution resumes without restarting from the beginning

This pattern allows the pipeline to continue under temporary API or service instability.

## Data flow

```text
input topic
  -> chapter metadata
  -> fact extraction
  -> synthesis draft
  -> QA verification
  -> approved or rejected
  -> financial/institutional pdf output
  -> council evaluation and verdict
```

## Design principles

- Grounding over speculation
- Deterministic progression over ad hoc execution
- Explicit evidence handling over hidden assumptions
- Structured reporting over loose narrative output
- Failover continuity instead of brittle single-provider operation

## Future architecture considerations

Possible enhancements include:

- Web dashboard or UI layer
- More modular domain adapters
- Storage-backed report histories
- Better deployment packaging and environment control
- Additional model providers or orchestration strategies

## Summary

ZEUSS is designed to behave less like a freeform AI chat and more like a research operating system for institutional-grade analysis. Its architecture prioritizes evidence discipline, repeatability, and operational resilience.
