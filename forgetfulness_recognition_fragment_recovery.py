# >>> Codex backend rewrite (auto-generated) <<<
# Converted from a local Ollama backend to the OpenAI Codex API.
# Source : tools/forgetfulness_recognition_fragment_recovery.py
# Endpoint: OFFLINE ONLY -> http://127.0.0.1:11434/v1 (local Ollama)
# Model   : OFFLINE ONLY -> local Ollama gpt-oss:20b (override via CODEX_MODEL / OLLAMA_MODEL)
# Auth    : reads env OPENAI_API_KEY (falls back to CODEX_API_KEY)
# Originals are untouched; this is a generated copy.
from __future__ import annotations

# --- Codex tier bootstrap (auto-generated) -----------------------------------
try:
    import sys as _cdx_sys
    import pathlib as _cdx_path
    for _cdx_par in _cdx_path.Path(__file__).resolve().parents:
        if (_cdx_par / "_shared" / "codex_backend.py").exists():
            if str(_cdx_par / "_shared") not in _cdx_sys.path:
                _cdx_sys.path.insert(0, str(_cdx_par / "_shared"))
            break
    from codex_backend import (
        default_chat_base as _codex_default_base,
        default_chat_model as _codex_default_model,
        codex_chat as _codex_chat,
        detect_mode as _codex_detect_mode,
    )
except Exception:  # fallback keeps the file runnable even without the helper
    def _codex_default_base():
        return __import__("os").environ.get("OPENAI_BASE_URL", "http://127.0.0.1:11434/v1")

    def _codex_default_model():
        return __import__("os").environ.get("CODEX_MODEL", "gpt-oss:20b")

    def _codex_detect_mode():
        return "offline"

    def _codex_chat(*_a, **_k):
        raise RuntimeError("codex_backend helper unavailable for plan tier")
# -----------------------------------------------------------------------------

try:
    from asunai_security import bootstrap as _asunai_bootstrap
    _asunai_bootstrap.install()
except Exception:
    pass

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, Field

from codex.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    ToolError,
    ToolPermission,
)
from codex.core.tools.ui import ToolCallDisplay, ToolResultDisplay, ToolUIData

if TYPE_CHECKING:
    from codex.core.types import ToolCallEvent, ToolResultEvent


DEFAULT_PROMPT_TEMPLATE = """### MEMORY FRAGMENT / FORGETFULNESS MODE (OPT-IN)
Work with forgetfulness detection and fragment-based recovery.
- Identify gaps, recall cues, and reconstruction steps.
- Provide concise guidance with confidence notes.
- Keep reasoning concise; avoid revealing chain-of-thought.

Focus: {focus}
Show steps: {show_steps}
Max results: {max_results}
"""

TOOL_PROMPT = (
    "Use forgetfulness_recognition_fragment_recovery to recognize forgetfulness or recover memory fragments. "
    "Provide prompt or messages, and optionally set focus, show_steps, and max_results."
)


class MemoryFragmentMessage(BaseModel):
    role: str
    content: str


class MemoryFragmentArgs(BaseModel):
    prompt: str | None = Field(default=None, description="User prompt to solve.")
    messages: list[MemoryFragmentMessage] | None = Field(
        default=None, description="Optional chat messages."
    )
    system_prompt: str | None = Field(default=None, description="Optional system prompt prefix.")
    focus: str | None = Field(default=None, description="Focus label or domain.")
    show_steps: bool | None = Field(default=None, description="Whether to include a step outline.")
    max_results: int | None = Field(default=None, description="Maximum results in the outline.")
    llm_api_base: str | None = Field(default=None, description="OpenAI-compatible API base URL.")
    llm_model: str | None = Field(default=None, description="LLM model name.")
    llm_temperature: float = Field(default=0.2, description="LLM temperature.")
    llm_max_tokens: int = Field(default=900, description="LLM max tokens.")
    llm_stream: bool = Field(default=False, description="Stream LLM tokens.")


class MemoryFragmentResult(BaseModel):
    answer: str
    system_prompt: str
    messages: list[MemoryFragmentMessage]
    used_focus: str
    show_steps: bool
    max_results: int
    template_source: str
    warnings: list[str]
    errors: list[str]
    llm_model: str


class MemoryFragmentConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ASK
    llm_api_base: str = Field(default="http://127.0.0.1:11434/v1", description="OpenAI-compatible API base URL.")
    llm_model: str = Field(default_factory=_codex_default_model, description="Default LLM model name.")
    default_focus: str = Field(
        default="Recover forgotten memory via short-term and long-term fragments.",
        description="Default focus label.",
    )
    default_show_steps: bool = Field(default=False, description="Default for show_steps.")
    default_max_results: int = Field(default=4, description="Default max results.")
    prompt_path: Path | None = Field(
        default=Path.home()
        / "codex"
        / "codex"
        / "core"
        / "prompts"
        / "forgetfulness_recognition_fragment_recovery.md",
        description="Optional path to a prompt template.",
    )
    prompt_max_chars: int = Field(default=8000, description="Maximum template characters to load.")


class MemoryFragmentState(BaseToolState):
    pass


class ForgetfulnessRecognitionFragmentRecovery(
    BaseTool[
        MemoryFragmentArgs,
        MemoryFragmentResult,
        MemoryFragmentConfig,
        MemoryFragmentState,
    ],
    ToolUIData[MemoryFragmentArgs, MemoryFragmentResult],
):
    description: ClassVar[str] = "Detect forgotten instances and recover memory via fragments across short/long-term memory."

    @classmethod
    def get_tool_prompt(cls) -> str | None:
        return TOOL_PROMPT

    async def run(self, args: MemoryFragmentArgs) -> MemoryFragmentResult:
        warnings: list[str] = []
        errors: list[str] = []

        focus = (args.focus or self.config.default_focus).strip() or "memory fragments"
        show_steps = args.show_steps if args.show_steps is not None else self.config.default_show_steps
        max_results = args.max_results if args.max_results is not None else self.config.default_max_results
        if max_results <= 0:
            raise ToolError("max_results must be positive.")

        self._validate_llm_settings(args)
        template, template_source = self._load_template(warnings)
        system_prompt = self._build_system_prompt(template, focus, show_steps, max_results, args.system_prompt)
        messages = self._normalize_messages(args, system_prompt)
        answer = self._call_llm(messages, args)

        return MemoryFragmentResult(
            answer=answer,
            system_prompt=system_prompt,
            messages=messages,
            used_focus=focus,
            show_steps=show_steps,
            max_results=max_results,
            template_source=template_source,
            warnings=warnings,
            errors=errors,
            llm_model=self._resolve_model(args),
        )

    def _validate_llm_settings(self, args: MemoryFragmentArgs) -> None:
        if args.llm_temperature < 0:
            raise ToolError("llm_temperature cannot be negative.")
        if args.llm_max_tokens <= 0:
            raise ToolError("llm_max_tokens must be positive.")

    def _load_template(self, warnings: list[str]) -> tuple[str, str]:
        template = DEFAULT_PROMPT_TEMPLATE
        source = "embedded"
        if not self.config.prompt_path:
            return self._truncate_template(template, warnings), source
        path = self._resolve_prompt_path(self.config.prompt_path)
        if not path.exists():
            warnings.append(f"Prompt template not found: {path}")
            return self._truncate_template(template, warnings), source
        if path.is_dir():
            warnings.append(f"Prompt template is a directory: {path}")
            return self._truncate_template(template, warnings), source
        try:
            text = path.read_text("utf-8", errors="ignore").strip()
        except OSError as exc:
            warnings.append(f"Failed to read prompt template: {exc}")
            return self._truncate_template(template, warnings), source
        if not text:
            warnings.append(f"Prompt template empty: {path}")
            return self._truncate_template(template, warnings), source
        return self._truncate_template(text, warnings), str(path)

    def _resolve_prompt_path(self, raw_path: Path | str) -> Path:
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            path = self.config.effective_workdir / path
        return path.resolve()

    def _truncate_template(self, template: str, warnings: list[str]) -> str:
        max_chars = self.config.prompt_max_chars
        if max_chars > 0 and len(template) > max_chars:
            warnings.append("Prompt template truncated to prompt_max_chars.")
            return template[:max_chars].rstrip()
        return template

    def _build_system_prompt(self, template: str, focus: str, show_steps: bool, max_results: int, prefix: str | None) -> str:
        show_steps_text = "yes" if show_steps else "no"
        rendered = self._render_template(template, focus, show_steps_text, max_results)
        if prefix and prefix.strip():
            return f"{prefix.strip()}\n\n{rendered}".strip()
        return rendered.strip()

    def _render_template(self, template: str, focus: str, show_steps_text: str, max_results: int) -> str:
        had_placeholders = any(token in template for token in ("{focus}", "{show_steps}", "{max_results}"))
        rendered = template.replace("{focus}", focus)
        rendered = rendered.replace("{show_steps}", show_steps_text)
        rendered = rendered.replace("{max_results}", str(max_results))
        if had_placeholders:
            return rendered
        extra = f"Focus: {focus}\nShow steps: {show_steps_text}\nMax results: {max_results}"
        return f"{rendered.rstrip()}\n\n{extra}"

    def _normalize_messages(self, args: MemoryFragmentArgs, system_prompt: str) -> list[MemoryFragmentMessage]:
        messages: list[MemoryFragmentMessage] = []
        if args.messages:
            for msg in args.messages:
                role = (msg.role or "").strip() or "user"
                content = (msg.content or "").strip()
                if content:
                    messages.append(MemoryFragmentMessage(role=role, content=content))
        elif args.prompt and args.prompt.strip():
            messages.append(MemoryFragmentMessage(role="user", content=args.prompt.strip()))
        else:
            raise ToolError("Provide prompt or messages.")
        if not messages:
            raise ToolError("No usable messages provided.")
        if system_prompt.strip():
            messages.insert(0, MemoryFragmentMessage(role="system", content=system_prompt.strip()))
        return messages

    def _call_llm(self, messages: list[MemoryFragmentMessage], args: MemoryFragmentArgs) -> str:
        if _codex_detect_mode() == "plan":
            return _codex_chat([m.model_dump() for m in messages],
                               temperature=args.llm_temperature,
                               max_tokens=args.llm_max_tokens)
        api_base = (args.llm_api_base or self.config.llm_api_base).rstrip("/")
        url = api_base + "/chat/completions"
        payload = {
            "model": self._resolve_model(args),
            "messages": [msg.model_dump() for msg in messages],
            "temperature": args.llm_temperature,
            "max_tokens": args.llm_max_tokens,
            "stream": bool(args.llm_stream),
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            resp = urllib.request.urlopen(req, timeout=600)
        except urllib.error.URLError as exc:
            raise ToolError(f"LLM request failed: {exc}") from exc
        if not args.llm_stream:
            body = resp.read().decode("utf-8")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError as exc:
                raise ToolError(f"LLM response parse failed: {exc}") from exc
            return parsed["choices"][0]["message"].get("content", "").strip()
        return self._read_streaming_response(resp)

    def _read_streaming_response(self, resp) -> str:
        parts: list[str] = []
        for raw in resp:
            line = raw.decode("utf-8").strip()
            if not line:
                continue
            if line.startswith("data:"):
                line = line[len("data:") :].strip()
            if line == "[DONE]":
                break
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            choice = chunk.get("choices", [{}])[0]
            delta = choice.get("delta") or choice.get("message") or {}
            content = delta.get("content")
            if content:
                parts.append(content)
                sys.stdout.write(content)
                sys.stdout.flush()
        if parts:
            sys.stdout.write("\n")
            sys.stdout.flush()
        return "".join(parts).strip()

    def _resolve_model(self, args: MemoryFragmentArgs) -> str:
        return args.llm_model or self.config.llm_model

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, MemoryFragmentArgs):
            return ToolCallDisplay(summary="forgetfulness_recognition_fragment_recovery")
        return ToolCallDisplay(
            summary="forgetfulness_recognition_fragment_recovery",
            details={
                "focus": event.args.focus,
                "show_steps": event.args.show_steps,
                "max_results": event.args.max_results,
            },
        )

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, MemoryFragmentResult):
            return ToolResultDisplay(success=False, message=event.error or event.skip_reason or "No result")
        message = "Memory fragment/forgetfulness processing complete"
        if event.result.errors:
            message = "Memory fragment/forgetfulness processing finished with errors"
        return ToolResultDisplay(
            success=not bool(event.result.errors),
            message=message,
            warnings=event.result.warnings,
            details={
                "answer": event.result.answer,
                "used_focus": event.result.used_focus,
                "show_steps": event.result.show_steps,
                "max_results": event.result.max_results,
                "template_source": event.result.template_source,
                "errors": event.result.errors,
            },
        )

    @classmethod
    def get_status_text(cls) -> str:
        return "Memory fragment/forgetfulness processing complete"