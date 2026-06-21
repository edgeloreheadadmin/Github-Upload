# >>> Codex backend rewrite (auto-generated) <<<
# Converted from a local Ollama backend to the OpenAI Codex API.
# Source : tools/memory_cross_reference_binding.py
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


DEFAULT_PROMPT_TEMPLATE = """### MEMORY CROSS REFERENCE BINDING MODE (OPT-IN)
Bind cross-references between memories.
- Identify binding anchors and linkage signals.
- Provide concise binding outputs with confidence notes.
- Keep reasoning concise; avoid revealing chain-of-thought.

Focus: {focus}
Show steps: {show_steps}
Max bindings: {max_bindings}
"""

TOOL_PROMPT = (
    "Use `memory_cross_reference_binding` to bind cross-references between "
    "memories. Provide `prompt` or `messages`, and optionally set `focus`, "
    "`show_steps`, and `max_bindings`."
)


class CrossReferenceBindingMessage(BaseModel):
    role: str
    content: str


class CrossReferenceBindingArgs(BaseModel):
    prompt: str | None = Field(
        default=None, description="User prompt to solve."
    )
    messages: list[CrossReferenceBindingMessage] | None = Field(
        default=None, description="Optional chat messages."
    )
    system_prompt: str | None = Field(
        default=None, description="Optional system prompt prefix."
    )
    focus: str | None = Field(
        default=None, description="Focus label or domain."
    )
    show_steps: bool | None = Field(
        default=None, description="Whether to include a step outline."
    )
    max_bindings: int | None = Field(
        default=None, description="Maximum bindings in the outline."
    )
    llm_api_base: str | None = Field(
        default=None, description="OpenAI-compatible API base URL."
    )
    llm_model: str | None = Field(
        default=None, description="LLM model name."
    )
    llm_temperature: float = Field(
        default=0.2, description="LLM temperature."
    )
    llm_max_tokens: int = Field(
        default=900, description="LLM max tokens."
    )
    llm_stream: bool = Field(
        default=False, description="Stream LLM tokens."
    )


class CrossReferenceBindingResult(BaseModel):
    answer: str
    system_prompt: str
    messages: list[CrossReferenceBindingMessage]
    used_focus: str
    show_steps: bool
    max_bindings: int
    template_source: str
    warnings: list[str]
    errors: list[str]
    llm_model: str


class CrossReferenceBindingConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ASK
    llm_api_base: str = Field(
        default_factory=_codex_default_base,
        description="OpenAI-compatible API base URL.",
    )
    llm_model: str = Field(
        default_factory=_codex_default_model, description="Default LLM model name."
    )
    default_focus: str = Field(
        default="Memory cross reference binding.",
        description="Default focus label.",
    )
    default_show_steps: bool = Field(
        default=False, description="Default for show_steps."
    )
    default_max_bindings: int = Field(
        default=4, description="Default max bindings."
    )
    prompt_path: Path | None = Field(
        default=Path.home()
        / "codex"
        / "codex"
        / "core"
        / "prompts"
        / "memory_cross_reference_binding.md",
        description="Optional path to a prompt template.",
    )
    prompt_max_chars: int = Field(
        default=8000, description="Maximum template characters to load."
    )


class CrossReferenceBindingState(BaseToolState):
    pass


class MemoryCrossReferenceBinding(
    BaseTool[
        CrossReferenceBindingArgs,
        CrossReferenceBindingResult,
        CrossReferenceBindingConfig,
        CrossReferenceBindingState,
    ],
    ToolUIData[CrossReferenceBindingArgs, CrossReferenceBindingResult],
):
    description: ClassVar[str] = "Bind cross-references between memories."

    @classmethod
    def get_tool_prompt(cls) -> str | None:
        return TOOL_PROMPT

    async def run(
        self, args: CrossReferenceBindingArgs
    ) -> CrossReferenceBindingResult:
        warnings: list[str] = []
        errors: list[str] = []

        focus = (args.focus or self.config.default_focus).strip()
        if not focus:
            focus = "memory cross reference binding"

        show_steps = (
            args.show_steps
            if args.show_steps is not None
            else self.config.default_show_steps
        )
        max_bindings = (
            args.max_bindings
            if args.max_bindings is not None
            else self.config.default_max_bindings
        )
        if max_bindings <= 0:
            raise ToolError("max_bindings must be positive.")

        self._validate_llm_settings(args)

        template, template_source = self._load_template(warnings)
        system_prompt = self._build_system_prompt(
            template, focus, show_steps, max_bindings, args.system_prompt
        )

        messages = self._normalize_messages(args, system_prompt)
        answer = self._call_llm(messages, args)

        return CrossReferenceBindingResult(
            answer=answer,
            system_prompt=system_prompt,
            messages=messages,
            used_focus=focus,
            show_steps=show_steps,
            max_bindings=max_bindings,
            template_source=template_source,
            warnings=warnings,
            errors=errors,
            llm_model=self._resolve_model(args),
        )

    def _validate_llm_settings(
        self, args: CrossReferenceBindingArgs
    ) -> None:
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

        template = text
        source = str(path)
        return self._truncate_template(template, warnings), source

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

    def _build_system_prompt(
        self,
        template: str,
        focus: str,
        show_steps: bool,
        max_bindings: int,
        prefix: str | None,
    ) -> str:
        show_steps_text = "yes" if show_steps else "no"
        rendered = self._render_template(
            template, focus, show_steps_text, max_bindings
        )
        if prefix and prefix.strip():
            return f"{prefix.strip()}\\n\\n{rendered}".strip()
        return rendered.strip()

    def _render_template(
        self,
        template: str,
        focus: str,
        show_steps_text: str,
        max_bindings: int,
    ) -> str:
        had_placeholders = (
            "{focus}" in template
            or "{show_steps}" in template
            or "{max_bindings}" in template
        )
        rendered = template
        if "{focus}" in template:
            rendered = rendered.replace("{focus}", focus)
        if "{show_steps}" in template:
            rendered = rendered.replace("{show_steps}", show_steps_text)
        if "{max_bindings}" in template:
            rendered = rendered.replace(
                "{max_bindings}", str(max_bindings)
            )

        if had_placeholders:
            return rendered

        extra = (
            f"Focus: {focus}\\n"
            f"Show steps: {show_steps_text}\\n"
            f"Max bindings: {max_bindings}"
        )
        return f"{rendered.rstrip()}\\n\\n{extra}"

    def _normalize_messages(
        self, args: CrossReferenceBindingArgs, system_prompt: str
    ) -> list[CrossReferenceBindingMessage]:
        messages: list[CrossReferenceBindingMessage] = []
        if args.messages:
            for msg in args.messages:
                role = (msg.role or "").strip()
                content = (msg.content or "").strip()
                if not content:
                    continue
                if not role:
                    role = "user"
                messages.append(
                    CrossReferenceBindingMessage(
                        role=role, content=content
                    )
                )
        elif args.prompt and args.prompt.strip():
            messages.append(
                CrossReferenceBindingMessage(
                    role="user", content=args.prompt.strip()
                )
            )
        else:
            raise ToolError("Provide prompt or messages.")

        if not messages:
            raise ToolError("No usable messages provided.")

        if system_prompt.strip():
            messages.insert(
                0,
                CrossReferenceBindingMessage(
                    role="system", content=system_prompt.strip()
                ),
            )
        return messages

    def _call_llm(
        self,
        messages: list[CrossReferenceBindingMessage],
        args: CrossReferenceBindingArgs,
    ) -> str:
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
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
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
            sys.stdout.write("\\n")
            sys.stdout.flush()
        return "".join(parts).strip()

    def _resolve_model(self, args: CrossReferenceBindingArgs) -> str:
        return args.llm_model or self.config.llm_model

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, CrossReferenceBindingArgs):
            return ToolCallDisplay(summary="memory_cross_reference_binding")
        return ToolCallDisplay(
            summary="memory_cross_reference_binding",
            details={
                "focus": event.args.focus,
                "show_steps": event.args.show_steps,
                "max_bindings": event.args.max_bindings,
            },
        )

    @classmethod
    def get_result_display(
        cls, event: ToolResultEvent
    ) -> ToolResultDisplay:
        if not isinstance(event.result, CrossReferenceBindingResult):
            return ToolResultDisplay(
                success=False,
                message=event.error or event.skip_reason or "No result",
            )
        message = "Memory cross reference binding complete"
        if event.result.errors:
            message = "Memory cross reference binding finished with errors"
        return ToolResultDisplay(
            success=not bool(event.result.errors),
            message=message,
            warnings=event.result.warnings,
            details={
                "answer": event.result.answer,
                "used_focus": event.result.used_focus,
                "show_steps": event.result.show_steps,
                "max_bindings": event.result.max_bindings,
                "template_source": event.result.template_source,
                "errors": event.result.errors,
            },
        )

    @classmethod
    def get_status_text(cls) -> str:
        return "Memory cross reference binding"