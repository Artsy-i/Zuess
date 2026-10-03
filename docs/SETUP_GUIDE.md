# ZEUSS Setup Guide

<div align="center">

## Installation & Configuration

</div>

---

## System Requirements

<div align="center">

- Python 3.10+
- pip or uv
- Access to API provider keys
- Internet connection for live search and provider calls

</div>

---

## 1. Clone the Repository

<div align="center">

```bash
git clone https://github.com/Artsy-i/Zuess.git
cd Zuess
```

</div>

---

## 2. Create a Virtual Environment

### Linux/macOS

<div align="center">

```bash
python -m venv .venv
source .venv/bin/activate
```

</div>

### Windows PowerShell

<div align="center">

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

</div>

---

## 3. Install Dependencies

<div align="center">

```bash
pip install -r requirements.txt
```

</div>

---

## 4. Configure Environment Variables

<div align="center">

Create a `.env` file in the project root.

</div>

### Required Keys

<div align="center">

```bash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_API_KEY_2=your_key_here
OPENROUTER_API_KEY_3=your_key_here
EXA_API_KEY=your_key_here
```

</div>

### Optional Provider Keys

<div align="center">

```bash
GROQ_API_KEY=your_key_here
CEREBRAS_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
NVIDIA_API_KEY=your_key_here
OPENCODE_API_KEY=your_key_here
```

</div>

---

## 5. Run the Project

### Standard Run

<div align="center">

```bash
python main.py --topic "AI Supply Chain 2026"
```

</div>

### Resume from Checkpoint

<div align="center">

```bash
python main.py --topic "AI Supply Chain 2026" --resume
```

</div>

### Auto-Approve Mode (Unattended)

<div align="center">

```bash
python main.py --topic "AI Supply Chain 2026" --auto-approve
```

</div>

---

## 6. Check Outputs

<div align="center">

The project saves data in:

```
research_cache/     (Chapter states & checkpoints)
final_reports/      (Institutional PDFs)
logs/               (QA audit logs)
```

</div>

---

## Troubleshooting

### Missing API Keys

<div align="center">

**Issue:** Project reports missing keys  
**Solution:** Update `.env` or the local `API KEYS` file and rerun.

</div>

### Failover Activation

<div align="center">

**Issue:** Provider fails or rate-limits  
**Solution:** System automatically rotates to next provider and continues with checkpointed work.

</div>

### PDF Generation Fails

<div align="center">

**Issue:** PDF compilation error  
**Solution:** Ensure:
- Environment is installed correctly
- Output directory exists or is writable
- ReportLab dependencies loaded successfully

</div>

### All Providers Exhausted

<div align="center">

**Issue:** All failover tiers failed  
**Solution:** Check API key validity, network connectivity, and provider service status.

</div>

---

## Recommended Workflow

<div align="center">

1. Run the first report with a focused topic
2. Review generated chapter cache files
3. Inspect logs if QA blocked a chapter
4. Publish final dossier once approved
5. Review Commercial Council verdict

</div>

---

## Security Notes

<div align="center">

- ⚠️ Do not commit `.env` files to public repositories
- 🔐 Keep API tokens private
- 🔒 Restrict access to sensitive generated outputs and logs
- 📋 Treat generated dossiers as proprietary material

</div>

---

## Summary

<div align="center">

The setup is intentionally lightweight:

1. Install dependencies
2. Add environment keys
3. Run your target topic
4. Pipeline handles chapter execution and publication

</div>

---

<div align="center">

**Need help?** → [ARCHITECTURE.md](ARCHITECTURE.md) • [API_REFERENCE.md](API_REFERENCE.md) • [Issues](https://github.com/Artsy-i/Zuess/issues)

</div>
