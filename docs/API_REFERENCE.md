# API Reference

## Module overview

This repository exposes several core Python modules and runtime entry points used by the pipeline.

## main.py

### `main()`

Runs the CLI entry point.

Arguments:

- `--topic`: research topic to analyze
- `--resume`: resume from cached chapter states
- `--max-retries`: QA retry limit per chapter
- `--auto-approve`: skip the publication approval prompt

Behavior:

- validates API key availability
- displays the welcome UI
- asks the user for a topic if none is supplied
- chooses between classic engine mode and orchestrator mode
- executes the pipeline

### `MultiChapterPipelineEngine`

Main engine class used for multi-chapter processing.

#### Constructor

```python
MultiChapterPipelineEngine(topic: str, resume: bool = False, max_retries: int = 3, auto_approve: bool = False)
```

#### Responsibilities

- manages chapter state
- runs Node A/B/C for chapters
- caches chapter results
- publishes institutional PDF output
- executes final commercial council evaluation

#### Core methods

- `get_chapter_cache_paths(chapter_id: int) -> List[str]`
- `load_chapter_cache(chapter_id: int) -> Optional[Dict[str, Any]]`
- `save_chapter_cache(chapter_id: int, chapter_state: Dict[str, Any]) -> None`
- `process_chapter(ch_meta: Dict[str, Any], dashboard: PipelineDashboard) -> Dict[str, Any]`
- `run_node_d_institutional_publisher(console: Console) -> bool`
- `run_node_e_commercial_council(console: Console) -> str`
- `execute() -> None`

## llm_router.py

### `LLMRouter`

The core provider rotation and failover class.

#### Constructor

```python
LLMRouter(
    groq_api_key: Optional[str] = None,
    cerebras_api_key: Optional[str] = None,
    openrouter_api_key: Optional[str] = None,
    deepseek_api_key: Optional[str] = None,
    xai_api_key: Optional[str] = None,
    cohere_api_key: Optional[str] = None,
    opencode_api_key: Optional[str] = None,
    nvidia_api_key: Optional[str] = None,
)
```

#### Core methods

- `_resolve_api_key(env_var_name: str) -> str`
- `repair_json_string(raw: str) -> str`
- `parse_and_repair_json_array(raw: str) -> List[Dict[str, Any]]`
- `parse_and_repair_json_object(raw: str) -> Dict[str, Any]`
- `execute_with_waterfall(...) -> str`
- `search_authoritative_facts(...) -> List[Dict[str, Any]]`
- `synthesize_report_section(...) -> str`
- `qa_verify_report(...) -> Dict[str, Any]`
- `evaluate_council_persona(...) -> str`
- `evaluate_chairman_verdict(...) -> str`

### `execute_with_waterfall(...)`

This is the public helper function for triggering the major failover mechanism.

```python
execute_with_waterfall(
    task_prompt: str,
    node_id: str = "UniversalNode",
    provider_configs: Optional[List[Dict[str, Any]]] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 4000,
    router: Optional[LLMRouter] = None,
    ui_callback: Optional[Any] = None,
    ui_state: Optional[Any] = None,
    **kwargs,
) -> str
```

## pdf_generator.py

### `ReportLabPDFGenerator`

Generates the final multi-chapter institutional dossier.

#### Constructor

```python
ReportLabPDFGenerator()
```

#### Core method

```python
generate_institutional_pdf(
    output_filepath: str,
    topic: str,
    chapters_data: List[Dict[str, Any]],
    overall_summary: Optional[str] = None,
) -> str
```

This method compiles the final report with:

- cover page
- executive preface
- chapter content
- QA badge blocks
- source ledger appendix
- automated page numbering

## orchestrator.py

### `ZeussOrchestrator`

Alternative command-driven orchestrator that manages a mission loop.

#### Constructor

```python
ZeussOrchestrator(topic: str)
```

#### Core method

- `execute_mission() -> None`

This loop issues commands like:

- `RUN_NODE_A(1)`
- `RUN_NODE_B(1, Rewrite the growth numbers)`
- `RUN_NODE_C(1)`
- `RUN_NODE_D()`
- `RUN_NODE_E()`
- `FINISH(summary)`

## Supporting constants

### `CHAPTERS`

Defines the four primary report chapters:

1. Macro-Level Market Drivers
2. Capital & Infrastructure Shifts
3. Risk & Regulatory Exposure
4. The Source Ledger

### `WHITELISTED_DOMAINS`

Authoritative source domains used by the search layer, such as:

- `.gov`
- `mckinsey.com`
- `bloomberg.com`

## Notes

The public interface is intentionally designed for runtime orchestration and document generation rather than library-style reuse. The project is best understood as an operational AI research pipeline, not a conventional SDK.
