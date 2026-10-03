# Autonomous B2B Industry Intelligence Pipeline — Multi-Chapter High-Density Engine

A Python-based autonomous B2B Industry Intelligence pipeline built with a strict one-way State Machine architecture, multi-provider **Waterfall Failover with State Handoff**, live Google Search grounding, anti-hallucination QA verification, and publication-ready **Institutional Multi-Chapter PDF compilation**.

---

## 4 Core Institutional Deliverables

The engine executes independent search, synthesis, and auditing loops for 4 distinct chapters:

1. **Macro-Level Market Drivers**: The primary catalysts accelerating or disrupting the target sector over the next 24 months.
2. **Capital & Infrastructure Shifts**: Where enterprise capital is currently being deployed within the sector (Capex, hyperscalers, silicon, hardware).
3. **Risk & Regulatory Exposure**: Verified bottlenecks, supply chain vulnerabilities, export controls, and compliance hurdles.
4. **The Source Ledger**: Cross-chapter strategic outlook, synthesis of findings, and comprehensive primary citation mapping.

---

## Multi-Chapter Architecture

```
                    +---------------------------------------+
                    |       Input: CLI --topic              |
                    +---------------------------------------+
                                        |
       +--------------------------------+--------------------------------+
       |                                |                                |
       v                                v                                v
[CHAPTER 1: Drivers]        [CHAPTER 2: Capital]             [CHAPTER 3: Risk] ... [CHAPTER 4: Ledger]
  - Node A: Grounded Search   - Node A: Grounded Search        - Node A: Grounded Search
  - Node B: Deep Synthesis    - Node B: Deep Synthesis         - Node B: Deep Synthesis
  - Node C: QA Auditor        - Node C: QA Auditor             - Node C: QA Auditor
       |                                |                                |
       v                                v                                v
chapter_1_state.json        chapter_2_state.json             chapter_3_state.json
       +--------------------------------+--------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
| Node D: Institutional Publisher & Compiler                                        |
| - Waits until ALL 4 chapters pass the QA Gateway                                  |
| - Pauses for human terminal approval ('Y')                                        |
| - Compiles Formal Cover Page, Executive Preface, 4 Core Chapters, and Grand       |
|   Source Ledger Appendix in /final_reports/                                       |
+-----------------------------------------------------------------------------------+
```

---

## Waterfall Failover Tiers

### Tier A: The Synthesizer (Llama 3.3 Rotation)
1. **Primary**: **Groq** (`llama-3.3-70b-versatile` via `https://api.groq.com/openai/v1`)
2. **Failover 1**: **Cerebras** (`llama-3.3-70b` via `https://api.cerebras.ai/v1`)
3. **Failover 2**: **OpenRouter** (`meta-llama/llama-3.3-70b-instruct:free` via `https://openrouter.ai/api/v1`)

### Tier B: The QA Auditor (DeepSeek-R1 Rotation)
1. **Primary**: **DeepSeek Official** (`deepseek-reasoner` via `https://api.deepseek.com/v1`)
2. **Failover 1**: **OpenRouter** (`deepseek/deepseek-r1:free` via `https://openrouter.ai/api/v1`)

*On 429/503: State is saved to `research_cache/handoff.json`, a visible terminal warning is outputted, and the failover provider resumes generation seamlessly.*

---

## Execution Commands

### Standard Institutional Multi-Chapter Run
```powershell
python main.py --topic "AI Supply Chain 2026"
```

### Resume from Existing State
Skip already completed and QA-approved chapters from `/research_cache/`:
```powershell
python main.py --topic "AI Supply Chain 2026" --resume
```

### Unattended Automated Run
Bypass the human terminal confirmation gate:
```powershell
python main.py --topic "AI Supply Chain 2026" --auto-approve
```
