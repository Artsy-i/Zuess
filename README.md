```
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                           ⚡ Z E U S S ⚡                                   ║
║                  AUTONOMOUS B2B INTELLIGENCE ENGINE                        ║
║                                                                            ║
║            Enterprise-Grade Research | Grounded Analysis | PDF Ready      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

<div align="center">
  <br>
  <img alt="ZEUSS" src="https://img.shields.io/badge/ZEUSS-Intelligence%20Pipeline-blue?style=for-the-badge&logoColor=white" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-2E8B57?style=for-the-badge" />
  <img alt="License" src="https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge" />
  <img alt="Status" src="https://img.shields.io/badge/Status-Production%20Ready-green?style=for-the-badge" />
  <br><br>
  <strong>Transform Raw Market Chaos Into Institutional Intelligence</strong>
  <br>
  <em>Zero synthetic estimations. 100% citation enforcement. Deterministic state machine.</em>
</div>

---

## 🎯 What is ZEUSS?

**ZEUSS** is a **proprietary autonomous research system** engineered to generate multi-chapter B2B industry intelligence reports with **institutional-grade verification standards**.

Unlike typical AI-powered analysis tools, ZEUSS enforces:

✅ **Grounded Authority** — Facts extracted only from whitelisted institutional sources (.gov, McKinsey, Bloomberg)  
✅ **Zero Estimations** — Missing data is flagged as "Data Unavailable" instead of guessed  
✅ **Adversarial QA** — DeepSeek-R1 fact-checks 100% of claims before approval  
✅ **Citation Enforcement** — Every numerical claim includes mandatory footnote URLs  
✅ **Resilient Failover** — Multi-provider waterfall with checkpoint-based resumption  
✅ **Publication Ready** — Formal institutional PDFs with cover pages, prefaces, and source ledgers  

---

## 💎 Premium Features

### 🔍 Intelligent Search Layer
- Live Exa.ai integration for real-time market data
- Domain whitelisting to eliminate open-web noise
- Structured fact extraction into verified JSON

### 🧠 Multi-Provider Intelligence Synthesis
- **Tier A (Search)**: OpenRouter NVIDIA models for fact grounding
- **Tier B (Synthesis)**: Llama 3.3 / Qwen rotating synthesis
- **Tier C (Reasoning)**: DeepSeek-R1 for adversarial QA
- **Automatic failover** with checkpointed resumption on rate limits

### 📊 Institutional Report Compilation
- **Formal Cover Page** with metadata grid and confidentiality notice
- **Executive Preface** with data verification charter
- **4-Chapter Core Analysis** with high-density institutional prose
- **Grand Source Ledger Appendix** with clickable citation URLs
- **Page Numbering & Running Headers** via two-pass canvas rendering

### 🎭 Commercial Council Verdict
After publication, 4 parallel advisor personas independently evaluate the report:
- 🛑 **The Contrarian** — "Why demand a refund?"
- 🔍 **The First Principles Thinker** — "Does this solve real problems?"
- 🚀 **The Expansionist** — "What's the hidden upside?"
- 🎯 **The Executor** — "Write the 3-sentence sales pitch"

Finally, **Chairman's Verdict** synthesizes all opinions and delivers a **PUBLISH / REVISE / SCRAP** decision with Gumroad monetization angle.

---

## 🏛️ Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER TOPIC INPUT                             │
│                 (e.g., "AI Supply Chain 2026")                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
      ┌────▼──┐       ┌────▼──┐      ┌────▼──┐
      │ CH 1  │       │ CH 2  │      │ CH 3  │      ┌─────────┐
      │Market │       │Capital│      │ Risk  │      │ CH 4    │
      │Drivers│       │Shifts │      │Reg'ry │      │Ledger   │
      └────┬──┘       └────┬──┘      └────┬──┘      └────┬────┘
           │               │               │              │
           └───────────────┼───────────────┴──────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
      ┌────▼────────────────────────────┐ │
      │   NODE A: GROUNDED SEARCH       │ │
      │   (Cohere / Exa.ai / OpenRouter)│ │
      └────┬─────────────────────────────┘ │
           │                               │
      ┌────▼─────────────────────────────┐ │
      │  NODE B: DEEP SYNTHESIS          │ │
      │  (Llama 3.3 / Qwen Rotation)     │ │
      └────┬──────────────────────────────┘ │
           │                               │
      ┌────▼──────────────────────────────┐│
      │  NODE C: QA AUDITOR               ││
      │  (DeepSeek-R1 Adversarial Gate)   ││
      └────┬───────────────────────────────┘│
           │                                │
      APPROVED?  ──NO──> REWRITE LOOP      │
           │YES                            │
           │◄───────────────────────────────┘
           │
      ┌────▼────────────────────────────┐
      │  NODE D: INSTITUTIONAL PUBLISHER │
      │  (PDF Compilation + Ledger)      │
      └────┬─────────────────────────────┘
           │
      ┌────▼──────────────────────────────┐
      │  NODE E: COMMERCIAL COUNCIL       │
      │  (4 Advisors + Chairman Verdict)  │
      └────┬───────────────────────────────┘
           │
      ┌────▼─────────────────────────────┐
      │  🎯 FINAL DOSSIER + STRATEGY     │
      └──────────────────────────────────┘
```

---

## ⚙️ Waterfall Failover System

**On Provider Failure (429/503/Timeout):**

1. 🔴 **Checkpoint** → Current accumulated text saved to `/research_cache/checkpoint_*.json`
2. 🔄 **Rotate** → Automatically shift to next provider in tier
3. 📝 **Inject** → Prompt includes resumption instruction to continue seamlessly
4. ✅ **Concatenate** → New output appended directly to checkpoint
5. 📊 **Log** → Failover event streamed to live Failover Log Panel

```
Tier A (Search):
  Primary  → OpenRouter (nvidia/nemotron-3.5-lightning:free)
  Failover → OpenRouter (cohere/north-mini-code:free)

Tier B (Synthesis):
  Primary  → OpenRouter (nvidia/nemotron-3-ultra-550b:free)
  Failover1→ OpenRouter (nvidia/nemotron-3-super-120b:free)
  Failover2→ OpenRouter (qwen/qwen3.8-27b:free)

Tier C (Reasoning):
  Primary  → OpenRouter (nvidia/nemotron-3-nano-omni-30b:free)
  Failover1→ OpenRouter (qwen/qwen3.8-27b:free)
  Failover2→ OpenRouter (openrouter/free)
```

---

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/Artsy-i/Zuess.git && cd Zuess
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cat > .env << EOF
OPENROUTER_API_KEY=your_key_here
OPENROUTER_API_KEY_2=your_key_here
OPENROUTER_API_KEY_3=your_key_here
EXA_API_KEY=your_key_here
EOF
```

### 3. Run

```bash
# Standard execution
python main.py --topic "AI Supply Chain 2026"

# Resume from checkpoint
python main.py --topic "AI Supply Chain 2026" --resume

# Auto-approve (unattended)
python main.py --topic "AI Supply Chain 2026" --auto-approve
```

### 4. Outputs

```
✅ final_reports/
   └─ ai_supply_chain_2026_institutional_dossier_YYYYMMDD_HHMMSS.pdf

📊 research_cache/
   ├─ chapter_1_state.json
   ├─ chapter_2_state.json
   ├─ chapter_3_state.json
   ├─ chapter_4_state.json
   └─ commercial_council_state.json

📋 logs/
   ├─ qa_audit_ch1_*.json
   ├─ qa_audit_ch2_*.json
   ├─ qa_audit_ch3_*.json
   └─ commercial_council_*.json
```

---

## 📚 Documentation

Complete documentation is organized in the `/docs` folder:

| Document | Purpose |
|----------|----------|
| [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | System design, data flows, state machine |
| [**API_REFERENCE.md**](docs/API_REFERENCE.md) | Module exports, class methods, signatures |
| [**SETUP_GUIDE.md**](docs/SETUP_GUIDE.md) | Installation, environment, troubleshooting |
| [**LICENSE.md**](docs/LICENSE.md) | Software licensing terms |
| [**LEGAL_NOTICE.md**](docs/LEGAL_NOTICE.md) | Copyright & IP protection notice |

---

## 🔐 Legal & Intellectual Property

**© 2026 Artsy-i. All rights reserved.**

This project is **proprietary software**. Unauthorized reproduction, distribution, modification, or commercial use is strictly prohibited. See [LICENSE.md](docs/LICENSE.md) and [LEGAL_NOTICE.md](docs/LEGAL_NOTICE.md) for complete terms.

---

## 📊 Use Cases

### Supply Chain Intelligence
```bash
python main.py --topic "Semiconductor Supply Chain Resilience 2026"
```
→ Capital flows, geopolitical risks, manufacturing bottlenecks, vendor dependencies

### Enterprise AI Adoption
```bash
python main.py --topic "Generative AI Deployment in Financial Services"
```
→ Market drivers, regulatory exposure, competitive positioning, integration risks

### Infrastructure Investment
```bash
python main.py --topic "EV Charging Network Expansion 2026-2028"
```
→ Capex allocations, site selection, compliance hurdles, competitive dynamics

---

## 🎯 Core Principles

| Principle | Implementation |
|-----------|----------------|
| **Grounding Over Speculation** | Whitelisted sources only (.gov, McKinsey, Bloomberg) |
| **Evidence Discipline** | Missing data explicitly marked "Data Unavailable" |
| **Deterministic Progression** | State machine ensures strict stage progression |
| **Resilient Operation** | Waterfall failover with checkpoint handoff |
| **Transparency** | 100% citation enforcement with footnote URLs |
| **Institutional Grade** | Formal PDF dossiers with executive preface & ledger |

---

## 🌟 Technical Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.10+ |
| **LLM Integration** | OpenAI SDK (multi-provider via OpenRouter) |
| **Search** | Exa.ai API |
| **PDF Generation** | ReportLab |
| **Terminal UI** | Rich |
| **Async/Concurrency** | concurrent.futures |
| **Configuration** | python-dotenv |

---

## 📞 Support & Feedback

- 🐛 **Report Issues**: [GitHub Issues](https://github.com/Artsy-i/Zuess/issues)
- 📖 **Read Docs**: [/docs](docs/)
- 📧 **Contact**: @Artsy-i on GitHub

---

## 🚀 Roadmap

- [ ] Web dashboard (Streamlit/FastAPI)
- [ ] Multi-language report generation
- [ ] Real-time data feed integrations
- [ ] Custom sector taxonomies
- [ ] Enterprise deployment templates
- [ ] Report distribution & archival

---

<div align="center">
  <br>
  <strong>⚡ Built with institutional rigor. Powered by AI orchestration. ⚡</strong>
  <br><br>
  <img src="https://img.shields.io/badge/Made%20with-Python-blue?style=flat-square" alt="Made with Python" />
  <img src="https://img.shields.io/badge/Enterprise-Grade-green?style=flat-square" alt="Enterprise Grade" />
  <img src="https://img.shields.io/badge/100%25-Grounded-brightgreen?style=flat-square" alt="100% Grounded" />
  <br><br>
  <code>© 2026 Artsy-i • Proprietary Intelligence Research System</code>
  <br>
  <a href="https://github.com/Artsy-i/Zuess">Repository</a> •
  <a href="docs/">Documentation</a> •
  <a href="docs/LICENSE.md">License</a>
</div>
