# ZEUSS Setup Guide

## System requirements

- Python 3.10+
- pip or uv
- Access to API provider keys
- Internet connection for live search and provider calls

## 1. Clone the repository

```bash
git clone https://github.com/Artsy-i/Zuess.git
cd Zuess
```

## 2. Create a virtual environment

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file in the project root.

```bash
OPENROUTER_API_KEY=your_key_here
OPENROUTER_API_KEY_2=your_key_here
OPENROUTER_API_KEY_3=your_key_here
EXA_API_KEY=your_key_here
```

Optional keys:

```bash
GROQ_API_KEY=your_key_here
CEREBRAS_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
NVIDIA_API_KEY=your_key_here
OPENCODE_API_KEY=your_key_here
```

## 5. Run the project

### Standard run

```bash
python main.py --topic "AI Supply Chain 2026"
```

### Resume run

```bash
python main.py --topic "AI Supply Chain 2026" --resume
```

### Auto-approve mode

```bash
python main.py --topic "AI Supply Chain 2026" --auto-approve
```

## 6. Check outputs

The project saves data in the following directories:

```text
research_cache/
final_reports/
logs/
```

## Troubleshooting

### Missing API keys

If the project reports missing keys, update `.env` or the local `API KEYS` file and rerun.

### Failover activation

If a provider fails or rate-limits, the system will automatically rotate to the next provider and continue with checkpointed work.

### PDF generation fails

Ensure that:

- the environment is installed correctly
- the output directory exists or is writable
- reportlab dependencies loaded successfully

## Recommended workflow

1. Run the first report with a single focused topic
2. Review the generated chapter cache files
3. Inspect logs if QA blocked a chapter
4. Publish the final dossier once approved

## Security notes

- Do not commit `.env` files to public repositories
- Keep API tokens private
- Restrict access to sensitive generated outputs and logs

## Summary

The setup is intentionally lightweight: install dependencies, add environment keys, run the target topic, and let the pipeline handle chapter execution and publication stages.
