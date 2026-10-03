"""Universal LLM Router Module for B2B Industry Intelligence Pipeline.

Architecture: Universal Checkpointing Waterfall across all API tiers:
- Tier A (Search / Node A):
    Primary: Cohere SDK (model: "command-r-plus", connectors: [{"id": "web-search"}])
    Directive: "Extract metrics exclusively from .gov, mckinsey.com, and bloomberg.com domains."
- Tier B (Synthesis / Node B):
    Primary: NVIDIA NIM (base_url: "https://integrate.api.nvidia.com/v1", model: "meta/llama-3.1-70b-instruct")
    Failover 1: Groq (base_url: "https://api.groq.com/openai/v1", model: "qwen/qwen3.8-27b")
    Failover 2: Cerebras (base_url: "https://api.cerebras.ai/v1", model: "gpt-oss-120b")
- Tier C (Reasoning / Nodes C & E):
    Primary: NVIDIA NIM (base_url: "https://integrate.api.nvidia.com/v1", model: "deepseek-ai/deepseek-r1")
    Failover 1: Opencode Zen (base_url: "https://opencode.ai/zen/v1", model: "opencode/big-pickle")
    Failover 2: OpenRouter (base_url: "https://openrouter.ai/api/v1", model: "deepseek/deepseek-r1:free")

Failsafe Engine (execute_with_waterfall):
- Streams completions, appending chunks to a local string variable.
- Traps ANY API exception (429, 401/403, 402, 503, Timeouts, etc.).
- Saves current accumulated string to /research_cache/checkpoint_[node]_current.json.
- Rotates to next provider with prompt injection:
  "You are resuming an interrupted output. DO NOT start from the beginning. DO NOT introduce yourself. Continue seamlessly from this exact string: [load checkpoint]"
- Directly concatenates output to the checkpoint string.

JSON Repair Layer:
- Lightweight regex and structural repair for Node A and Node C cross-model concatenations.
"""

import json
import os
import re
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Thread-safe lock for handoff/checkpoint operations
_handoff_lock = threading.Lock()

# Base Workspace Paths
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(WORKSPACE_ROOT, "research_cache")
HANDOFF_FILE = os.path.join(CACHE_DIR, "handoff.json")

def load_skill(skill_name: str) -> str:
    """Loads a SKILL.md payload from the local skills directory."""
    skill_path = os.path.join(WORKSPACE_ROOT, "skills", skill_name, "SKILL.md")
    if os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Whitelisted authoritative domains for B2B research
WHITELISTED_DOMAINS = [
    ".gov",
    "mckinsey.com",
    "bloomberg.com"
]

# -----------------------------------------------------------------------------
# Tier A: Searcher / JSON Formatter (Node A)
# -----------------------------------------------------------------------------
TIER_A_SEARCHER = [
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "nvidia/nemotron-3.5-lightning:free",
        "env_var": "OPENROUTER_API_KEY",
        "headers": {
            "HTTP-Referer": "https://github.com/zeuss/b2b-intel",
            "X-Title": "B2B Industry Intelligence Pipeline",
        },
    },
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "cohere/north-mini-code:free",
        "env_var": "OPENROUTER_API_KEY_2",
        "headers": {
            "HTTP-Referer": "https://github.com/zeuss/b2b-intel",
            "X-Title": "B2B Industry Intelligence Pipeline",
        },
    },
]

# -----------------------------------------------------------------------------
# Tier B: Hardened Synthesis Array (Node B)
# -----------------------------------------------------------------------------
TIER_B_SYNTHESIS = [
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "env_var": "OPENROUTER_API_KEY_2",
        "headers": {
            "HTTP-Referer": "https://github.com/zeuss/b2b-intel",
            "X-Title": "B2B Industry Intelligence Pipeline",
        },
    },
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "env_var": "OPENROUTER_API_KEY_3",
        "headers": {
            "HTTP-Referer": "https://github.com/zeuss/b2b-intel",
            "X-Title": "B2B Industry Intelligence Pipeline",
        },
    },
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "qwen/qwen3.8-27b:free",
        "env_var": "OPENROUTER_API_KEY",
        "headers": {
            "HTTP-Referer": "https://github.com/zeuss/b2b-intel",
            "X-Title": "B2B Industry Intelligence Pipeline",
        },
    },
]

# -----------------------------------------------------------------------------
# Tier C: Hardened Reasoning Array (Nodes C & E)
# -----------------------------------------------------------------------------
TIER_C_REASONING = [
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "env_var": "OPENROUTER_API_KEY_3",
        "headers": {
            "HTTP-Referer": "https://github.com/zeuss/b2b-intel",
            "X-Title": "B2B Industry Intelligence Pipeline",
        },
    },
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "qwen/qwen3.8-27b:free",
        "env_var": "OPENROUTER_API_KEY",
        "headers": {
            "HTTP-Referer": "https://github.com/zeuss/b2b-intel",
            "X-Title": "B2B Industry Intelligence Pipeline",
        },
    },
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openrouter/free",
        "env_var": "OPENROUTER_API_KEY_2",
        "headers": {
            "HTTP-Referer": "https://github.com/zeuss/b2b-intel",
            "X-Title": "B2B Industry Intelligence Pipeline",
        },
    },
]

# Backwards-compatible aliases for existing main.py callers
TIER_A_SYNTHESIZER = TIER_B_SYNTHESIS
TIER_B_QA_AUDITOR = TIER_C_REASONING


class LLMRouter:
    """Manages multi-provider execution with Universal Checkpointing Waterfall and JSON Repair."""

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        cerebras_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        deepseek_api_key: Optional[str] = None,
        xai_api_key: Optional[str] = None,
        cohere_api_key: Optional[str] = None,
        opencode_api_key: Optional[str] = None,
        nvidia_api_key: Optional[str] = None,
    ):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
        self.cerebras_api_key = cerebras_api_key or os.getenv("CEREBRAS_API_KEY", "")
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.deepseek_api_key = deepseek_api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.xai_api_key = xai_api_key or os.getenv("XAI_API_KEY", "")
        self.cohere_api_key = cohere_api_key or os.getenv("COHERE_API_KEY", "")
        self.opencode_api_key = opencode_api_key or os.getenv("OPENCODE_API_KEY", "")
        self.nvidia_api_key = nvidia_api_key or os.getenv("NVIDIA_API_KEY", "")
        self.log_callback = None
        self.ui_state = None
        self.ui_callback = None

        self._cohere_client = None

    def _safe_log(self, msg: str, ui_state: Optional[Any] = None, style: Optional[str] = None):
        """Safely prints to console through Live if active to avoid corrupting layout grid."""
        state = ui_state or self.ui_state
        if state:
            if hasattr(state, "safe_print"):
                try:
                    state.safe_print(msg, style=style)
                    return
                except Exception:
                    pass
            live_obj = getattr(state, "live", None)
            if live_obj and getattr(live_obj, "console", None):
                try:
                    live_obj.console.print(msg, style=style)
                    return
                except Exception:
                    pass
        print(msg)

    def _dispatch_ui_model(self, provider_name: str, model_slug: str, ui_state: Any = None, ui_callback: Any = None):
        """Updates Active Task Panel model state across ui_state and ui_callback."""
        state = ui_state or self.ui_state
        callback = ui_callback or self.ui_callback
        active_str = f"Active Model: {provider_name} - {model_slug}"

        if state and hasattr(state, "set_active_model"):
            try:
                state.set_active_model(provider_name, model_slug)
            except Exception:
                pass

        if callback and callable(callback):
            if hasattr(state, "set_active_model") and callback == getattr(state, "set_active_model"):
                return
            try:
                callback("MODEL_CHANGE", {"provider": provider_name, "model": model_slug, "active_model_str": active_str})
            except Exception:
                try:
                    callback(active_str)
                except Exception:
                    pass

    def _dispatch_failover_log(self, message: str, event_type: str = "FAILOVER_LOG", data: Optional[Dict[str, Any]] = None, ui_state: Any = None, ui_callback: Any = None):
        """Pushes failover and rate limit events to Failover Log Panel across ui_state and ui_callback."""
        state = ui_state or self.ui_state
        callback = ui_callback or self.ui_callback or self.log_callback

        if state and hasattr(state, "add_failover_log"):
            try:
                state.add_failover_log(message)
            except Exception:
                pass

        if callback and callable(callback):
            if hasattr(state, "add_failover_log") and callback == getattr(state, "add_failover_log"):
                return
            payload = data or {"message": message}
            try:
                callback(event_type, payload)
            except Exception:
                try:
                    callback(message)
                except Exception:
                    pass

    def _resolve_api_key(self, env_var_name: str) -> str:
        """Resolves an API key from instance attributes, environment variables, or local API KEYS file."""
        mapping = {
            "GROQ_API_KEY": self.groq_api_key,
            "CEREBRAS_API_KEY": self.cerebras_api_key,
            "OPENROUTER_API_KEY": self.openrouter_api_key,
            "DEEPSEEK_API_KEY": self.deepseek_api_key,
            "XAI_API_KEY": self.xai_api_key,
            "COHERE_API_KEY": self.cohere_api_key,
            "OPENCODE_API_KEY": self.opencode_api_key,
            "NVIDIA_API_KEY": self.nvidia_api_key,
        }
        val = mapping.get(env_var_name, "").strip()
        if val and not val.startswith("your_"):
            return val

        env_val = os.getenv(env_var_name, "").strip()
        if env_val and not env_val.startswith("your_"):
            return env_val

        api_keys_file = os.path.join(WORKSPACE_ROOT, "API KEYS")
        if os.path.exists(api_keys_file):
            try:
                with open(api_keys_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or ":" not in line:
                            continue
                        prefix, key_candidate = line.split(":", 1)
                        prefix = prefix.strip().lower()
                        key_candidate = key_candidate.strip()
                        if not key_candidate:
                            continue

                        if env_var_name == "GROQ_API_KEY" and ("groq" in prefix or "grok" in prefix or key_candidate.startswith("gsk_")):
                            return key_candidate
                        elif env_var_name == "CEREBRAS_API_KEY" and ("cerebras" in prefix or key_candidate.startswith("csk-")):
                            return key_candidate
                        elif env_var_name == "OPENROUTER_API_KEY" and ("openrouter" in prefix or key_candidate.startswith("sk-or-v1-")):
                            return key_candidate
                        elif env_var_name == "DEEPSEEK_API_KEY" and ("deepseek" in prefix and not key_candidate.startswith("sk-or-")):
                            return key_candidate
                        elif env_var_name == "XAI_API_KEY" and ("xai" in prefix or key_candidate.startswith("xai-")):
                            return key_candidate
                        elif env_var_name == "COHERE_API_KEY" and "cohere" in prefix:
                            return key_candidate
                        elif env_var_name == "OPENCODE_API_KEY" and "opencode" in prefix:
                            return key_candidate
                        elif env_var_name == "NVIDIA_API_KEY" and ("nvidia" in prefix or key_candidate.startswith("nvapi-")):
                            return key_candidate
            except Exception:
                pass

        return ""

    def _get_cohere_client(self):
        """Lazy initialization of native Cohere client (Node A: The Searcher)."""
        if not self._cohere_client:
            import cohere
            key = self._resolve_api_key("COHERE_API_KEY")
            if not key or key.startswith("your_"):
                raise ValueError(
                    "COHERE_API_KEY is not configured in .env or API KEYS. "
                    "Please set your Cohere API key to enable Node A (Searcher)."
                )
            self._cohere_client = cohere.Client(api_key=key)
        return self._cohere_client

    # -------------------------------------------------------------------------
    # Step 3: JSON Repair Layer
    # -------------------------------------------------------------------------
    def repair_json_string(self, raw: str) -> str:
        """Pre-processes text to clean common LLM formatting issues."""
        if not raw:
            return ""
        text = raw.strip()

        # Strip markdown code blocks
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        elif text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        # Remove trailing commas before closing braces/brackets
        text = re.sub(r",\s*([\]}])", r"\1", text)
        return text.strip()

    def _balance_json_delimiters(self, text: str) -> str:
        """Balances unclosed quotes, brackets, and braces using a delimiter stack."""
        candidate = text.strip()
        stack = []
        in_str = False
        escape = False

        for ch in candidate:
            if escape:
                escape = False
                continue
            if ch == '\\':
                escape = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if not in_str:
                if ch in ('{', '['):
                    stack.append(ch)
                elif ch == '}' and stack and stack[-1] == '{':
                    stack.pop()
                elif ch == ']' and stack and stack[-1] == '[':
                    stack.pop()

        if in_str:
            candidate += '"'

        # Remove trailing comma before appending closing delimiters
        candidate = re.sub(r",\s*$", "", candidate)

        # Close in reverse order of nesting
        for opener in reversed(stack):
            if opener == '{':
                candidate += '}'
            elif opener == '[':
                candidate += ']'

        return re.sub(r",\s*([\]}])", r"\1", candidate)

    def parse_and_repair_json_array(self, raw: str) -> List[Dict[str, Any]]:
        """Repairs and extracts a JSON array of dicts even from truncated cross-model output."""
        if not raw:
            return []
        cleaned = self.repair_json_string(raw)

        # 1. Direct parse attempt
        try:
            data = json.loads(cleaned)
            if isinstance(data, list):
                return [d for d in data if isinstance(d, dict)]
            elif isinstance(data, dict):
                return [data]
        except Exception:
            pass

        # 2. Extract outermost [ ... ]
        m = re.search(r"(\[[\s\S]*\])", cleaned)
        if m:
            try:
                cand = re.sub(r",\s*([\]}])", r"\1", m.group(1))
                data = json.loads(cand)
                if isinstance(data, list):
                    return [d for d in data if isinstance(d, dict)]
            except Exception:
                pass

        # 3. Stack-based delimiter balancing
        if "[" in cleaned:
            start_pos = cleaned.find("[")
            candidate = cleaned[start_pos:]
            balanced = self._balance_json_delimiters(candidate)
            try:
                data = json.loads(balanced)
                if isinstance(data, list):
                    return [d for d in data if isinstance(d, dict)]
            except Exception:
                pass

        # 4. Regex object extractor: pull all individual valid JSON objects {...}
        results: List[Dict[str, Any]] = []
        obj_matches = re.finditer(r"\{[^{}]*\}", cleaned)
        for m in obj_matches:
            chunk = m.group(0)
            chunk = re.sub(r",\s*\}", "}", chunk)
            try:
                parsed = json.loads(chunk)
                if isinstance(parsed, dict):
                    results.append(parsed)
            except Exception:
                pass

        if results:
            return results

        # 5. Regex field parser fallback for Node A fact structures
        fact_pattern = re.findall(
            r'"fact"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"(?:[^{}]*?"numeric_data"\s*:\s*([^,}\n]+))?(?:[^{}]*?"source_url"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)")?',
            cleaned,
            re.DOTALL,
        )
        for match in fact_pattern:
            f_text = match[0].replace('\\"', '"')
            n_data = match[1].strip().strip('"') if match[1] else None
            if n_data in ("null", "None", ""):
                n_data = None
            s_url = match[2].strip() if match[2] else "https://www.mckinsey.com"
            results.append({
                "fact": f_text,
                "numeric_data": n_data,
                "source_url": s_url,
                "source_domain": "mckinsey.com",
                "topic_area": "Market Dynamics"
            })

        return results

    def parse_and_repair_json_object(self, raw: str) -> Dict[str, Any]:
        """Repairs and extracts a JSON object even from interrupted cross-model output."""
        if not raw:
            return {}
        cleaned = self.repair_json_string(raw)

        # 1. Direct parse attempt
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

        # 2. Extract outermost { ... }
        m = re.search(r"(\{[\s\S]*\})", cleaned)
        if m:
            try:
                candidate = re.sub(r",\s*([\]}])", r"\1", m.group(1))
                data = json.loads(candidate)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass

        # 3. Stack-based delimiter balancing
        if "{" in cleaned:
            start_pos = cleaned.find("{")
            candidate = cleaned[start_pos:]
            balanced = self._balance_json_delimiters(candidate)
            try:
                data = json.loads(balanced)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass

        # 4. Regex key extractor fallback for Node C
        result: Dict[str, Any] = {}
        app_match = re.search(r'"approved"\s*:\s*(true|false)', cleaned, re.IGNORECASE)
        if app_match:
            result["approved"] = app_match.group(1).lower() == "true"
        conf_match = re.search(r'"confidence_score"\s*:\s*(\d+)', cleaned)
        if conf_match:
            result["confidence_score"] = int(conf_match.group(1))
        sum_match = re.search(r'"summary"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
        if sum_match:
            result["summary"] = sum_match.group(1)
        crit_match = re.search(r'"critique"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', cleaned)
        if crit_match:
            result["critique"] = crit_match.group(1)

        claims_match = re.search(r'"audited_claims"\s*:\s*(\[[^\]]*\])', cleaned)
        if claims_match:
            try:
                claims_str = re.sub(r",\s*\]", "]", claims_match.group(1))
                result["audited_claims"] = json.loads(claims_str)
            except Exception:
                result["audited_claims"] = []
        else:
            result.setdefault("audited_claims", [])

        return result

    # Backwards-compatible aliases for JSON extraction
    _extract_json_array = parse_and_repair_json_array
    _extract_json_object = parse_and_repair_json_object

    # -------------------------------------------------------------------------
    # Step 1: The Failsafe Engine (execute_with_waterfall)
    # -------------------------------------------------------------------------
    def execute_with_waterfall(
        self,
        task_prompt: str,
        node_id: str = "UniversalNode",
        provider_configs: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        ui_callback: Optional[Any] = None,
        ui_state: Optional[Any] = None,
        **kwargs,
    ) -> str:
        """Universal failsafe waterfall engine across prioritized provider configurations.

        - Execution: Streams completion, continuously appending chunks to local string.
        - Trap: Catches RateLimitError 429, AuthenticationError 401/403, InsufficientBalance 402,
          ServiceUnavailable 503, APITimeoutError, and any network/API exception.
        - Checkpoint: Saves current accumulated string to /research_cache/checkpoint_[node]_current.json.
        - Rotate & Resume: Shifts to next provider with prompt injection:
          "You are resuming an interrupted output. DO NOT start from the beginning.
           DO NOT introduce yourself. Continue seamlessly from this exact string: [load checkpoint]"
        - Concatenation: Directly appends new output to checkpoint string.
        - UI Telemetry: Updates Active Task Panel (Active Model: [Provider] - [Model]) and Failover Log Panel.
        """
        from openai import (
            OpenAI,
            RateLimitError,
            AuthenticationError,
            PermissionDeniedError,
            APITimeoutError,
            APIConnectionError,
            InternalServerError,
            APIStatusError,
            BadRequestError,
        )

        # Normalize arguments if passed via kwargs or alternate order
        if kwargs.get("node_name"):
            node_id = kwargs["node_name"]
        if kwargs.get("rotation"):
            provider_configs = kwargs["rotation"]
        if kwargs.get("user_content"):
            task_prompt = kwargs["user_content"]
        if kwargs.get("system_prompt"):
            system_prompt = kwargs["system_prompt"]

        # Support alternative positional invocation: (node_id, provider_configs, task_prompt)
        if isinstance(node_id, list) and isinstance(provider_configs, (str, type(None))):
            actual_node = task_prompt
            actual_configs = node_id
            actual_prompt = provider_configs or kwargs.get("user_content", "")
            node_id = actual_node
            provider_configs = actual_configs
            task_prompt = actual_prompt

        if not provider_configs:
            provider_configs = TIER_B_SYNTHESIS

        # Resolve UI hooks
        active_ui_state = kwargs.get("ui_state") or ui_state or getattr(self, "ui_state", None)
        active_ui_callback = kwargs.get("ui_callback") or ui_callback or getattr(self, "ui_callback", None) or getattr(self, "log_callback", None)

        safe_node = re.sub(r"[^\w-]", "_", str(node_id).strip().lower())
        checkpoint_file = os.path.join(CACHE_DIR, f"checkpoint_{safe_node}_current.json")
        node_handoff_file = os.path.join(CACHE_DIR, f"handoff_{safe_node}.json")

        # Clean prior stale checkpoints before starting fresh execution
        if os.path.exists(checkpoint_file):
            try:
                os.remove(checkpoint_file)
            except Exception:
                pass
        if os.path.exists(node_handoff_file):
            try:
                os.remove(node_handoff_file)
            except Exception:
                pass
        with _handoff_lock:
            if os.path.exists(HANDOFF_FILE):
                try:
                    os.remove(HANDOFF_FILE)
                except Exception:
                    pass

        accumulated_string = ""
        last_error = None
        total_providers = len(provider_configs)

        for idx, provider_cfg in enumerate(provider_configs):
            provider_name = provider_cfg.get("name", "UnknownProvider")
            base_url = provider_cfg.get("base_url", "")
            model = provider_cfg.get("model", "")
            env_var = provider_cfg.get("env_var", "")
            headers = provider_cfg.get("headers")

            api_key = self._resolve_api_key(env_var) if env_var else ""
            if not api_key:
                self._safe_log(f"[WATERFALL] Skipping {provider_name}: {env_var} not configured or empty.", ui_state=active_ui_state)
                continue

            # Step 2: On normal execution: Update Active Task Panel to show current provider
            self._dispatch_ui_model(provider_name, model, ui_state=active_ui_state, ui_callback=active_ui_callback)

            self._safe_log(f"[WATERFALL] [{node_id}] Connecting to {provider_name} ({base_url}) | Model: {model}", ui_state=active_ui_state)

            client = OpenAI(
                base_url=base_url,
                api_key=api_key,
                default_headers=headers or None,
            )

            # Rotate & Resume Prompt Adjustment
            if accumulated_string:
                resumption_prompt = (
                    "You are resuming an interrupted output. DO NOT start from the beginning. "
                    f"DO NOT introduce yourself. Continue seamlessly from this exact string: {accumulated_string}"
                )
                current_sys_prompt = f"{system_prompt}\n\n{resumption_prompt}" if system_prompt else resumption_prompt
                self._safe_log(f"[WATERFALL RESUME] Injected resumption prompt with checkpoint ({len(accumulated_string)} chars)", ui_state=active_ui_state)
            else:
                current_sys_prompt = system_prompt or "You are an expert AI assistant."

            messages = [
                {"role": "system", "content": current_sys_prompt},
                {"role": "user", "content": task_prompt},
            ]

            # Groq OTPM safety cap to prevent 429 on free tier
            call_max_tokens = min(max_tokens, 1000) if "groq" in base_url.lower() else max_tokens

            checkpoint_before_call = accumulated_string
            provider_stream = ""

            try:
                # Execution: Attempt to stream the completion
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=call_max_tokens,
                    stream=True,
                )

                # Continuously append chunks to local string variable
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        delta_text = chunk.choices[0].delta.content
                        provider_stream += delta_text
                        accumulated_string = (
                            provider_stream if provider_stream.startswith(checkpoint_before_call)
                            else (checkpoint_before_call + provider_stream)
                        )

                # Clean up checkpoint files upon successful node completion
                if os.path.exists(checkpoint_file):
                    try:
                        os.remove(checkpoint_file)
                    except Exception:
                        pass
                if os.path.exists(node_handoff_file):
                    try:
                        os.remove(node_handoff_file)
                    except Exception:
                        pass
                with _handoff_lock:
                    if os.path.exists(HANDOFF_FILE):
                        try:
                            os.remove(HANDOFF_FILE)
                        except Exception:
                            pass

                self._safe_log(f"[WATERFALL SUCCESS] [{node_id}] {provider_name} completed generation ({len(accumulated_string.split())} words).", ui_state=active_ui_state)
                return accumulated_string

            except (
                RateLimitError,
                AuthenticationError,
                PermissionDeniedError,
                APITimeoutError,
                APIConnectionError,
                InternalServerError,
                APIStatusError,
                BadRequestError,
                Exception,
            ) as e:
                last_error = e
                status_code = getattr(e, "status_code", None)
                
                # Safer error message extraction
                err_str = ""
                if hasattr(e, "response") and hasattr(e.response, "json"):
                    try:
                        err_str = e.response.json().get("error", {}).get("message", "")
                    except Exception:
                        pass
                if not err_str and hasattr(e, "message"):
                    err_str = str(e.message)
                if not err_str:
                    err_str = str(e)
                    
                self._safe_log(f"[WATERFALL ERROR] [{node_id}] {provider_name} ({model}): {err_str}", ui_state=active_ui_state)

                # Checkpoint: Save current accumulated string immediately
                os.makedirs(CACHE_DIR, exist_ok=True)
                checkpoint_payload = {
                    "node_id": str(node_id),
                    "checkpoint": accumulated_string,
                    "partial_text": accumulated_string,
                    "accumulated_string": accumulated_string,
                    "failed_provider": provider_name,
                    "failed_base_url": base_url,
                    "failed_model": model,
                    "status_code": status_code or 503,
                    "error": err_str,
                    "timestamp": datetime.now().isoformat(),
                }
                try:
                    with open(checkpoint_file, "w", encoding="utf-8") as f:
                        json.dump(checkpoint_payload, f, indent=2, ensure_ascii=False)
                    with open(node_handoff_file, "w", encoding="utf-8") as f:
                        json.dump(checkpoint_payload, f, indent=2, ensure_ascii=False)
                    with _handoff_lock:
                        with open(HANDOFF_FILE, "w", encoding="utf-8") as f:
                            json.dump(checkpoint_payload, f, indent=2, ensure_ascii=False)
                except Exception as save_err:
                    self._safe_log(f"[WATERFALL] Warning: could not write checkpoint: {save_err}", ui_state=active_ui_state)

                # Step 2: On exception (Rate Limit/Error):
                # 1. Push a formatted warning string to the Failover Log Panel:
                #    `[RATE LIMIT REACHED] {Failed Provider} failed. Checkpoint saved.`
                rate_limit_msg = f"[bold red][RATE LIMIT REACHED][/bold red] {provider_name} failed. Checkpoint saved."
                self._dispatch_failover_log(
                    message=rate_limit_msg,
                    event_type="FAILOVER_ERROR",
                    data={"provider": provider_name, "message": rate_limit_msg},
                    ui_state=active_ui_state,
                    ui_callback=active_ui_callback,
                )

                # Rotate & Resume: Automatically shift to the next provider
                if idx + 1 < total_providers:
                    next_cfg = provider_configs[idx + 1]
                    next_provider_name = next_cfg.get("name", "NextProvider")
                    next_model = next_cfg.get("model", "")

                    # 2. Push the transition string:
                    #    `[HANDOFF] Transitioning chunk to {Next Provider}...`
                    handoff_msg = f"[bold yellow][HANDOFF][/bold yellow] Transitioning chunk to {next_provider_name}..."
                    self._dispatch_failover_log(
                        message=handoff_msg,
                        event_type="FAILOVER_HANDOFF",
                        data={"next_provider": next_provider_name, "message": handoff_msg},
                        ui_state=active_ui_state,
                        ui_callback=active_ui_callback,
                    )

                    # 3. Instantly update the Active Task Panel to reflect the new model taking over (e.g., "Active Model: Groq - qwen3.8-27b")
                    self._dispatch_ui_model(
                        provider_name=next_provider_name,
                        model_slug=next_model,
                        ui_state=active_ui_state,
                        ui_callback=active_ui_callback,
                    )

                    banner = (
                        "\n" + "!" * 75 + "\n"
                        f"  [WARNING] Failover triggered: Routing to {next_provider_name}\n"
                        f"  Reason: {provider_name} encountered error ({type(e).__name__}: {status_code or 'Unknown'})\n"
                        f"  Checkpoint: Saved {len(accumulated_string)} chars to {checkpoint_file}\n"
                        + "!" * 75 + "\n"
                    )
                    self._safe_log(banner, ui_state=active_ui_state)
                else:
                    exhausted_msg = f"[bold red][EXHAUSTED][/bold red] All providers in tier {node_id} exhausted."
                    self._dispatch_failover_log(
                        message=exhausted_msg,
                        event_type="EXHAUSTED",
                        data={"node_id": node_id, "message": exhausted_msg},
                        ui_state=active_ui_state,
                        ui_callback=active_ui_callback,
                    )
                    self._safe_log(f"\n[WATERFALL] Final provider {provider_name} in tier {node_id} exhausted.", ui_state=active_ui_state)

                continue

        # Emergency Fallback Tier Cascade (Groq -> Cerebras)
        emergency_rotation = [
            {
                "name": "Groq",
                "base_url": "https://api.groq.com/openai/v1",
                "model": "qwen/qwen3.8-27b",
                "env_var": "GROQ_API_KEY",
                "headers": None,
            },
            {
                "name": "Cerebras",
                "base_url": "https://api.cerebras.ai/v1",
                "model": "gpt-oss-120b",
                "env_var": "CEREBRAS_API_KEY",
                "headers": None,
            },
        ]
        if provider_configs != emergency_rotation:
            handoff_emergency = "[bold yellow][HANDOFF][/bold yellow] Transitioning chunk to Groq (Emergency Fallback)..."
            self._dispatch_failover_log(
                message=handoff_emergency,
                event_type="FAILOVER_HANDOFF",
                data={"next_provider": "Groq", "message": handoff_emergency},
                ui_state=active_ui_state,
                ui_callback=active_ui_callback,
            )
            self._dispatch_ui_model(
                provider_name="Groq",
                model_slug="qwen/qwen3.8-27b",
                ui_state=active_ui_state,
                ui_callback=active_ui_callback,
            )

            self._safe_log(f"\n[WATERFALL] Attempting failover to emergency fallback tier for {node_id}...", ui_state=active_ui_state)
            return self.execute_with_waterfall(
                task_prompt=task_prompt,
                node_id=f"{node_id}_EmergencyFallback",
                provider_configs=emergency_rotation,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                ui_state=active_ui_state,
                ui_callback=active_ui_callback,
            )

        raise RuntimeError(
            f"All providers in the {node_id} waterfall failed. Last error: {last_error}"
        )


    # Backwards-compatible alias for existing internal calls
    _execute_waterfall_completion = execute_with_waterfall

    # -------------------------------------------------------------------------
    # Tier A (Search / Node A): Cohere SDK with Web Grounding & Directive
    # -------------------------------------------------------------------------
    def search_authoritative_facts(
        self,
        topic: str,
        whitelist_domains: Optional[List[str]] = None,
        max_facts: int = 6,
        chapter_title: Optional[str] = None,
        chapter_focus: Optional[str] = None,
        ui_state: Optional[Any] = None,
        ui_callback: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """Tier A: Executes Node A JSON Formatter directly on OpenRouter models."""
        
        active_ui_state = ui_state or getattr(self, "ui_state", None)
        active_ui_callback = ui_callback or getattr(self, "ui_callback", None) or getattr(self, "log_callback", None)

        domains = whitelist_domains or WHITELISTED_DOMAINS
        
        system_prompt = load_skill("fact-density-extraction") + "\n\n" + load_skill("json-schema-contract") + "\n\n" + f"""You are an elite B2B Industry Intelligence Research Agent.
You must synthesize high-quality, empirical facts from the provided REAL-TIME SEARCH CONTEXT regarding the requested topic.
OUTPUT REQUIREMENT (AGGRESSIVE ENFORCEMENT):
You must format these facts into a valid, raw JSON array of fact objects. Do not include introductory text. Return ONLY valid JSON:
[
  {{
    "fact": "A concise description of the finding",
    "numeric_data": "The exact number or null",
    "source_url": "The full direct URL extracted from the search context",
    "source_domain": "The domain name extracted from the URL",
    "topic_area": "{chapter_title or 'Market Dynamics'}"
  }}
]
"""
        # Fetch real-time context using Exa.ai
        search_context = ""
        try:
            import requests
            query = f"{topic} {chapter_title or ''} {chapter_focus or ''}".strip()
            self._safe_log(f"[Node A] Executing Exa.ai search for: '{query}'", ui_state=active_ui_state)
            
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "x-api-key": os.getenv("EXA_API_KEY", "1491d01b-6c00-4842-b312-fd7ab1797e66")
            }
            payload = {
                "query": query,
                "useAutoprompt": True,
                "numResults": 5,
                "contents": {"text": True}
            }
            res = requests.post("https://api.exa.ai/search", json=payload, headers=headers)
            res.raise_for_status()
            exa_data = res.json()
            results = exa_data.get("results", [])
            
            if results:
                search_context = "REAL-TIME SEARCH CONTEXT (Exa.ai):\n"
                for i, r in enumerate(results):
                    search_context += f"--- Result {i+1} ---\nTitle: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('text', '')[:2000]}\n\n"
            else:
                search_context = "REAL-TIME SEARCH CONTEXT: No live data returned."
        except Exception as e:
            search_context = f"REAL-TIME SEARCH CONTEXT ERROR: {e}"
            self._safe_log(f"[Node A] Exa search error: {e}", ui_state=active_ui_state)

        user_content = f"Topic: {topic}\nChapter: {chapter_title or ''}\nFocus: {chapter_focus or ''}\nTarget Domains to emulate: {', '.join(domains)}\n\n{search_context}"

        try:
            raw_json_text = self.execute_with_waterfall(
                task_prompt=user_content,
                node_id="Node_A_Searcher",
                provider_configs=TIER_A_SEARCHER,
                system_prompt=system_prompt,
                temperature=0.1,
                ui_state=active_ui_state,
                ui_callback=active_ui_callback,
            )
            facts = self.parse_and_repair_json_array(raw_json_text)
        except Exception as e:
            self._safe_log(f"[ERROR] Node A Waterfall failed: {e}", ui_state=active_ui_state)
            facts = []

        if not facts:
            facts = [{
                "fact": f"Institutional sector intelligence for {topic}: {chapter_title or 'Market Dynamics'}",
                "numeric_data": None,
                "source_url": f"https://www.{domains[0].lstrip('.')}",
                "source_domain": domains[0].lstrip("."),
                "topic_area": chapter_title or "Market Dynamics",
            }]

        return facts

    # -------------------------------------------------------------------------
    # Tier B (Synthesis / Node B): NVIDIA NIM -> Groq -> Cerebras
    # -------------------------------------------------------------------------
    def synthesize_report_section(
        self,
        topic: str,
        facts_data: List[Dict[str, Any]],
        chapter_title: Optional[str] = None,
        chapter_focus: Optional[str] = None,
        qa_critique: Optional[str] = None,
        ui_state: Optional[Any] = None,
        ui_callback: Optional[Any] = None,
    ) -> str:
        """Synthesizes high-density institutional analysis using Tier B rotation:
        - Primary: NVIDIA NIM (meta/llama-3.1-70b-instruct)
        - Failover 1: Groq (qwen/qwen3.8-27b)
        - Failover 2: Cerebras (gpt-oss-120b)
        """
        ch_name = chapter_title or "Executive Intelligence Briefing"
        ch_scope = chapter_focus or "Empirical market dynamics, regulatory trends, and capital deployments."

        system_prompt = load_skill("minto-pyramid-synthesis") + "\n\n" + (
            f"You are an elite Institutional B2B Industry Intelligence Analyst authoring: '{ch_name}'.\n"
            f"TARGET SECTOR: {topic}\n"
            f"CHAPTER OBJECTIVE & FOCUS: {ch_scope}\n\n"
            "MANDATE: Focus your entire context window on generating high-density, exhaustive, long-form institutional analysis strictly dedicated to this chapter.\n\n"
            "CRITICAL SYSTEM CONSTRAINTS (ZERO-TOLERANCE):\n"
            "1. CITE EVERY NUMERICAL CLAIM: Every single number, percentage, dollar valuation, CAGR, or timeframe "
            "must be immediately followed by a footnote citation linking directly to its source URL from the provided facts data "
            "(e.g., 'The market reached $45B[^1]' where [^1]: https://...).\n"
            "2. MISSING DATA RULE: If specific quantitative data or projections for any metric within this chapter are not present in the facts provided, "
            "you MUST output the EXACT literal phrase: 'Data Unavailable at time of publication'. Do NOT attempt to infer, estimate, or fill the gap.\n"
            "3. FORBIDDEN FROM ESTIMATING: You are strictly forbidden from estimating numbers, rounding unverified figures, or generating projections.\n"
            f"4. HIGH-DENSITY INSTITUTIONAL STRUCTURE: Structure '{ch_name}' with multiple formal subheadings (## and ###), "
            "empirical market breakdowns, Capex / operational dynamics, risk sensitivities for institutional buyers and strategists, "
            "and a dedicated Chapter Footnote Reference list.\n"
        )

        user_content = (
            f"TARGET NICHE: {topic}\n"
            f"CHAPTER TITLE: {ch_name}\n"
            f"CHAPTER SCOPE: {ch_scope}\n\n"
            f"VERIFIED RESEARCH FACTS (Source of Truth):\n{json.dumps(facts_data, indent=2)}\n\n"
        )

        if qa_critique:
            user_content += (
                "PREVIOUS DRAFT REJECTED BY QA GATEWAY:\n"
                f"{qa_critique}\n\n"
                "INSTRUCTION: You must strictly address the above critique. Remove any ungrounded assertions or numbers, "
                "substitute missing metrics with the exact phrase 'Data Unavailable at time of publication', "
                "and ensure all numerical statements carry valid footnote URLs.\n"
            )

        return self.execute_with_waterfall(
            task_prompt=user_content,
            node_id="Node_B_Synthesis",
            provider_configs=TIER_B_SYNTHESIS,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=4000,
            ui_state=ui_state or getattr(self, "ui_state", None),
            ui_callback=ui_callback or getattr(self, "ui_callback", None),
        )

    # -------------------------------------------------------------------------
    # Tier C (Reasoning / Node C): QA Auditor
    # -------------------------------------------------------------------------
    def qa_verify_report(
        self,
        topic: str,
        draft_text: str,
        facts_data: List[Dict[str, Any]],
        chapter_title: Optional[str] = None,
        ui_state: Optional[Any] = None,
        ui_callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Audits synthesized report against original facts using Tier C:
        - Primary: NVIDIA NIM (deepseek-ai/deepseek-r1)
        - Failover 1: Opencode Zen (opencode/big-pickle)
        - Failover 2: OpenRouter (deepseek/deepseek-r1:free)

        Passes raw output through Step 3 JSON Repair Layer.
        """
        ch_name = chapter_title or "General Report"
        system_prompt = load_skill("adversarial-audit") + "\n\n" + load_skill("json-schema-contract") + "\n\n" + (
            "You are an uncompromising Chief QA & Fact-Checking Officer for institutional investment intelligence.\n"
            f"You are auditing Chapter: '{ch_name}'.\n"
            "Your sole objective is to prevent hallucinations and ungrounded claims in B2B intelligence reports.\n\n"
            "RULES OF ENGAGEMENT:\n"
            "1. Cross-reference every numerical figure, statistic, percentage, dollar value, and factual claim in the DRAFT TEXT "
            "against the provided SOURCE FACTS JSON.\n"
            "2. If a numerical claim in the draft is NOT explicitly corroborated by the SOURCE FACTS, or lacks a source citation, "
            "it is a REJECTION.\n"
            "3. If the author attempted to estimate or interpolate any number rather than stating 'Data Unavailable at time of publication', "
            "it is a REJECTION.\n"
            "4. Only approve ('approved': true) if 100% of numerical and material claims are grounded in the source facts.\n"
            "5. You must output your evaluation in strictly valid JSON format with the exact keys specified.\n"
        )

        user_content = f"""TOPIC: {topic}
AUDITED CHAPTER: {ch_name}

SOURCE FACTS JSON (Ground Truth):
{json.dumps(facts_data, indent=2)}

SYNTHESIZED DRAFT TEXT TO AUDIT:
{draft_text}

OUTPUT FORMAT (Respond ONLY with valid JSON):
{{
  "approved": true | false,
  "confidence_score": 0-100,
  "summary": "Concise 1-page Fact-Check Summary detailing audited metrics, verification status, and audit conclusion",
  "critique": "If rejected, detailed list of unverified numbers, hallucinated claims, or missing citations that must be fixed",
  "audited_claims": [
    {{
      "claim": "The specific statement or number checked",
      "source_found": true | false,
      "source_url": "matching url or 'None'",
      "verdict": "VERIFIED" | "UNVERIFIED" | "DATA_UNAVAILABLE_OK"
    }}
  ]
}}
"""

        raw_response = self.execute_with_waterfall(
            task_prompt=user_content,
            node_id="Node_C_QA_Auditor",
            provider_configs=TIER_C_REASONING,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=4000,
            ui_state=ui_state or getattr(self, "ui_state", None),
            ui_callback=ui_callback or getattr(self, "ui_callback", None),
        )

        # Step 3: JSON Repair Layer for Node C
        qa_result = self.parse_and_repair_json_object(raw_response)

        # Fallback defaults if LLM output format needs structuring
        if "approved" not in qa_result:
            qa_result["approved"] = False
            qa_result["summary"] = raw_response[:500] if raw_response else "Audit format parsing fallback."
            qa_result["critique"] = "QA model output format error. Verification required."
            qa_result["confidence_score"] = 0
            qa_result["audited_claims"] = []

        return qa_result

    # -------------------------------------------------------------------------
    # Tier C (Reasoning / Node E): Commercial Council & Chairman
    # -------------------------------------------------------------------------
    def evaluate_council_persona(
        self,
        topic: str,
        summary_text: str,
        persona_name: str,
        persona_system_prompt: str,
        ui_state: Optional[Any] = None,
        ui_callback: Optional[Any] = None,
    ) -> str:
        """Executes a Commercial Council advisor persona evaluation using Tier C Reasoning rotation."""
        user_content = (
            f"TARGET SECTOR / REPORT TOPIC: {topic}\n\n"
            f"COMPILED REPORT EXECUTIVE SUMMARY & PRIMARY BULLET POINTS:\n"
            f"{summary_text}\n\n"
            "ADVISOR MANDATE:\n"
            "Review the above report executive summary and bullet points. "
            "Deliver your sharp, unfiltered, direct assessment strictly adhering to your assigned persona."
        )

        return self.execute_with_waterfall(
            task_prompt=user_content,
            node_id=f"Council_{persona_name.replace(' ', '_')}",
            provider_configs=TIER_C_REASONING,
            system_prompt=load_skill("adversarial-audit") + "\n\n" + load_skill("json-schema-contract") + "\n\n" + persona_system_prompt,
            temperature=0.3,
            max_tokens=1500,
            ui_state=ui_state or getattr(self, "ui_state", None),
            ui_callback=ui_callback or getattr(self, "ui_callback", None),
        )

    def evaluate_chairman_verdict(
        self,
        topic: str,
        summary_text: str,
        council_opinions: Dict[str, str],
        ui_state: Optional[Any] = None,
        ui_callback: Optional[Any] = None,
    ) -> str:
        """Executes Chairman's final verdict using Tier C Reasoning rotation."""
        system_prompt = load_skill("adversarial-audit") + "\n\n" + load_skill("json-schema-contract") + "\n\n" + (
            "You are the Chairman of a B2B publishing firm. "
            "Read the following 4 advisor opinions on our newly generated report. "
            "Write ONE final verdict. Open with PUBLISH, REVISE, or SCRAP. "
            "Follow with a 2-sentence justification, and finally, the best sales angle to use on Gumroad."
        )

        opinions_block = []
        for persona_name, text in council_opinions.items():
            opinions_block.append(f"--- ADVISOR OPINION: {persona_name.upper()} ---\n{text.strip()}\n")

        user_content = (
            f"REPORT TARGET SECTOR: {topic}\n\n"
            f"REPORT EXECUTIVE SUMMARY & PRIMARY BULLET POINTS:\n{summary_text}\n\n"
            "COMMERCIAL COUNCIL ADVISOR DELIBERATIONS:\n\n"
            + "\n".join(opinions_block)
            + "\nNow provide your final Chairman's Verdict following your exact system prompt rules."
        )

        return self.execute_with_waterfall(
            task_prompt=user_content,
            node_id="Council_Chairman",
            provider_configs=TIER_C_REASONING,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=1500,
            ui_state=ui_state or getattr(self, "ui_state", None),
            ui_callback=ui_callback or getattr(self, "ui_callback", None),
        )


# Module-level convenience function for execute_with_waterfall
def execute_with_waterfall(
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
) -> str:
    """Module-level universal waterfall function."""
    r = router or LLMRouter()
    return r.execute_with_waterfall(
        task_prompt=task_prompt,
        node_id=node_id,
        provider_configs=provider_configs,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        ui_callback=ui_callback,
        ui_state=ui_state,
        **kwargs,
    )
