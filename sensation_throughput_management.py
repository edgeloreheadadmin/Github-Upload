# >>> Codex backend rewrite (auto-generated) <<<
# Converted from a local Ollama backend to the OpenAI Codex API.
# Source : tools/sensation_throughput_management.py
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
from dataclasses import dataclass
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


DEFAULT_PROMPT_TEMPLATE = """### SENSATION THROUGHPUT MANAGEMENT MODE (OPT-IN)
Manage sensation throughput to support sensation management and control.
- Identify throughput level, escalation risk, and desired range.
- Suggest de-escalation or amplification strategies as appropriate.
- Separate observed signals from inferred causes; call out uncertainty.
- Keep internal throughput management private; do not mention this mode in the response.
- If the user asks for steps or show_steps is enabled, give a concise outline.

Throughput style: {throughput_style}
Throughput focus: {throughput_focus}
Show steps: {show_steps}
Max actions: {max_actions}
"""

TOOL_PROMPT = (
    "Use `sensation_throughput_management` to manage sensation throughput. "
    "Provide `prompt` or `messages`, and optionally set `throughput_style`, "
    "`throughput_focus`, `show_steps`, and `max_actions`."
)


@dataclass(frozen=True)
class _ThroughputSource:
    content: str
    label: str | None
    source_type: str | None
    source_path: str | None


class SensationThroughputMessage(BaseModel):
    role: str
    content: str


class SensationThroughputItem(BaseModel):
    id: str | None = Field(default=None, description="Optional item id.")
    label: str | None = Field(default=None, description="Optional label.")
    source_type: str | None = Field(
        default=None, description="Source type (signal, trigger, feedback, etc.)."
    )
    sensation: str | None = Field(default=None, description="Sensation description.")
    throughput: str | None = Field(default=None, description="Throughput rating.")
    baseline: str | None = Field(default=None, description="Baseline throughput.")
    target_throughput: str | None = Field(
        default=None, description="Desired throughput range."
    )
    trigger: str | None = Field(default=None, description="Trigger description.")
    context: str | None = Field(default=None, description="Context summary.")
    signals: str | None = Field(default=None, description="Observed signals.")
    content: str | None = Field(default=None, description="Inline content.")
    tags: list[str] | None = Field(default=None, description="Optional tags.")
    path: str | None = Field(default=None, description="Path to a context file.")


class SensationThroughputManagementArgs(BaseModel):
    prompt: str | None = Field(
        default=None, description="User prompt to solve."
    )
    messages: list[SensationThroughputMessage] | None = Field(
        default=None, description="Optional chat messages."
    )
    system_prompt: str | None = Field(
        default=None, description="Optional system prompt prefix."
    )
    throughput_style: str | None = Field(
        default=None, description="Throughput management style label."
    )
    throughput_focus: str | None = Field(
        default=None, description="Throughput focus label."
    )
    show_steps: bool | None = Field(
        default=None, description="Whether to include a step outline."
    )
    max_actions: int | None = Field(
        default=None, description="Maximum actions in the outline."
    )
    items: list[SensationThroughputItem] | None = Field(
        default=None, description="Sensation throughput context items."
    )
    item_paths: list[str] | None = Field(
        default=None, description="Additional context file paths."
    )
    max_item_chars: int | None = Field(
        default=None, description="Max chars per item."
    )
    max_item_total_chars: int | None = Field(
        default=None, description="Max total item chars."
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
        default=700, description="LLM max tokens."
    )
    llm_stream: bool = Field(
        default=False, description="Stream LLM tokens."
    )


class ThroughputBlock(BaseModel):
    label: str | None
    source_type: str | None
    source_path: str | None
    content: str
    truncated: bool


class SensationThroughputManagementResult(BaseModel):
    answer: str
    system_prompt: str
    messages: list[SensationThroughputMessage]
    used_throughput_style: str
    used_throughput_focus: str
    show_steps: bool
    max_actions: int
    template_source: str
    throughput_blocks: list[ThroughputBlock]
    warnings: list[str]
    errors: list[str]
    llm_model: str


class SensationThroughputManagementConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ASK
    llm_api_base: str = Field(
        default_factory=_codex_default_base,
        description="OpenAI-compatible API base URL.",
    )
    llm_model: str = Field(
        default_factory=_codex_default_model, description="Default LLM model name."
    )
    default_throughput_style: str = Field(
        default="calibration",
        description="Default throughput management style.",
    )
    default_throughput_focus: str = Field(
        default="range-management",
        description="Default throughput focus.",
    )
    default_show_steps: bool = Field(
        default=False, description="Default for show_steps."
    )
    default_max_actions: int = Field(
        default=6, description="Default max actions."
    )
    prompt_path: Path | None = Field(
        default=Path.home()
        / "codex"
        / "codex"
        / "core"
        / "prompts"
        / "sensation_throughput_management.md",
        description="Optional path to a prompt template.",
    )
    prompt_max_chars: int = Field(
        default=8000, description="Maximum template characters to load."
    )
    max_item_chars: int = Field(
        default=4000, description="Maximum characters per item."
    )
    max_item_total_chars: int = Field(
        default=12000, description="Maximum total item characters."
    )


class SensationThroughputManagementState(BaseToolState):
    pass


class SensationThroughputManagement(
    BaseTool[
        SensationThroughputManagementArgs,
        SensationThroughputManagementResult,
        SensationThroughputManagementConfig,
        SensationThroughputManagementState,
    ],
    ToolUIData[
        SensationThroughputManagementArgs,
        SensationThroughputManagementResult,
    ],
):
    description: ClassVar[str] = (
        "Manage sensation throughput using a prompt template."
    )

    @classmethod
    def get_tool_prompt(cls) -> str | None:
        return TOOL_PROMPT

    async def run(
        self, args: SensationThroughputManagementArgs
    ) -> SensationThroughputManagementResult:
        warnings: list[str] = []
        errors: list[str] = []

        throughput_style = (
            args.throughput_style or self.config.default_throughput_style
        ).strip()
        if not throughput_style:
            throughput_style = "calibration"

        throughput_focus = (
            args.throughput_focus or self.config.default_throughput_focus
        ).strip()
        if not throughput_focus:
            throughput_focus = "range-management"

        show_steps = (
            args.show_steps
            if args.show_steps is not None
            else self.config.default_show_steps
        )
        max_actions = (
            args.max_actions
            if args.max_actions is not None
            else self.config.default_max_actions
        )
        if max_actions <= 0:
            raise ToolError("max_actions must be positive.")

        self._validate_llm_settings(args)

        template, template_source = self._load_template(warnings)
        system_prompt = self._build_system_prompt(
            template,
            throughput_style,
            throughput_focus,
            show_steps,
            max_actions,
            args.system_prompt,
        )

        throughput_blocks = self._collect_throughput_context(args, warnings)
        messages = self._normalize_messages(args, system_prompt)
        messages = self._inject_throughput_context(messages, throughput_blocks)
        answer = self._call_llm(messages, args)

        return SensationThroughputManagementResult(
            answer=answer,
            system_prompt=system_prompt,
            messages=messages,
            used_throughput_style=throughput_style,
            used_throughput_focus=throughput_focus,
            show_steps=show_steps,
            max_actions=max_actions,
            template_source=template_source,
            throughput_blocks=throughput_blocks,
            warnings=warnings,
            errors=errors,
            llm_model=self._resolve_model(args),
        )

    def _validate_llm_settings(self, args: SensationThroughputManagementArgs) -> None:
        if args.llm_temperature < 0:
            raise ToolError("llm_temperature cannot be negative.")
        if args.llm_max_tokens <= 0:
            raise ToolError("llm_max_tokens must be positive.")

    def _collect_throughput_context(
        self, args: SensationThroughputManagementArgs, warnings: list[str]
    ) -> list[ThroughputBlock]:
        max_item = (
            args.max_item_chars
            if args.max_item_chars is not None
            else self.config.max_item_chars
        )
        max_total = (
            args.max_item_total_chars
            if args.max_item_total_chars is not None
            else self.config.max_item_total_chars
        )
        if max_item <= 0 or max_total <= 0:
            raise ToolError(
                "max_item_chars and max_item_total_chars must be positive."
            )

        sources = self._resolve_throughput_sources(args, warnings)
        blocks: list[ThroughputBlock] = []
        total_chars = 0
        for source in sources:
            if total_chars >= max_total:
                warnings.append(
                    "max_item_total_chars reached; truncating throughput context."
                )
                break
            content = source.content
            truncated = False
            if len(content) > max_item:
                content = content[:max_item]
                truncated = True
            if total_chars + len(content) > max_total:
                content = content[: max_total - total_chars]
                truncated = True
            total_chars += len(content)
            blocks.append(
                ThroughputBlock(
                    label=source.label,
                    source_type=source.source_type,
                    source_path=source.source_path,
                    content=content,
                    truncated=truncated,
                )
            )

        if not blocks:
            warnings.append("No sensation throughput context provided.")
        return blocks

    def _resolve_throughput_sources(
        self, args: SensationThroughputManagementArgs, warnings: list[str]
    ) -> list[_ThroughputSource]:
        sources: list[_ThroughputSource] = []
        if args.items:
            for item in args.items:
                sources.append(self._load_throughput_item(item))

        if args.item_paths:
            for raw_path in args.item_paths:
                path = self._resolve_path(raw_path)
                content = path.read_text("utf-8", errors="ignore")
                sources.append(
                    _ThroughputSource(
                        content=content,
                        label=path.name,
                        source_type=None,
                        source_path=str(path),
                    )
                )

        if not sources and not warnings:
            warnings.append("No sensation throughput context provided.")
        return sources

    def _load_throughput_item(self, item: SensationThroughputItem) -> _ThroughputSource:
        if item.content and item.path:
            raise ToolError("Provide content or path per item, not both.")
        if not (
            item.content
            or item.path
            or item.sensation
            or item.throughput
            or item.target_throughput
            or item.context
        ):
            raise ToolError(
                "Each item must provide content, details, or path."
            )

        label = item.label or item.id or item.path
        text = self._format_throughput_text(item)

        if item.path:
            path = self._resolve_path(item.path)
            file_content = path.read_text("utf-8", errors="ignore")
            text = self._join_sections(text, "Content", file_content)
            return _ThroughputSource(
                content=text,
                label=label or path.name,
                source_type=item.source_type,
                source_path=str(path),
            )

        return _ThroughputSource(
            content=text,
            label=label,
            source_type=item.source_type,
            source_path=None,
        )

    def _format_throughput_text(self, item: SensationThroughputItem) -> str:
        lines: list[str] = []
        if item.label or item.id:
            lines.append(f"Label: {item.label or item.id}")
        if item.source_type:
            lines.append(f"Source type: {item.source_type}")
        if item.tags:
            tags = ", ".join(tag for tag in item.tags if tag)
            if tags:
                lines.append(f"Tags: {tags}")
        if item.sensation:
            lines.append("Sensation:")
            lines.append(item.sensation)
        if item.throughput:
            lines.append(f"Throughput: {item.throughput}")
        if item.baseline:
            lines.append(f"Baseline: {item.baseline}")
        if item.target_throughput:
            lines.append("Desired throughput:")
            lines.append(item.target_throughput)
        if item.trigger:
            lines.append("Trigger:")
            lines.append(item.trigger)
        if item.context:
            lines.append("Context:")
            lines.append(item.context)
        if item.signals:
            lines.append("Signals:")
            lines.append(item.signals)
        if item.content:
            lines.append("Content:")
            lines.append(item.content)
        return "\n".join(lines).strip()

    def _join_sections(self, base: str, title: str, content: str) -> str:
        if not content.strip():
            return base
        if base:
            return f"{base}\n\n{title}:\n{content}".strip()
        return f"{title}:\n{content}".strip()

    def _resolve_path(self, raw_path: str) -> Path:
        if not raw_path.strip():
            raise ToolError("Path cannot be empty.")
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            path = self.config.effective_workdir / path
        try:
            resolved = path.resolve()
        except ValueError as exc:
            raise ToolError(
                "Security error: cannot resolve the provided path."
            ) from exc
        if not resolved.exists():
            raise ToolError(f"File not found at: {resolved}")
        if resolved.is_dir():
            raise ToolError(f"Path is a directory, not a file: {resolved}")
        return resolved

    def _format_throughput_blocks(self, blocks: list[ThroughputBlock]) -> str:
        if not blocks:
            return ""
        parts = ["Sensation throughput context:"]
        for block in blocks:
            label = block.label or block.source_path or "throughput"
            type_suffix = f" | {block.source_type}" if block.source_type else ""
            trunc = " (truncated)" if block.truncated else ""
            header = f"[{label}{type_suffix}{trunc}]"
            parts.append(f"{header}\n{block.content}".strip())
        return "\n\n".join(parts).strip()

    def _inject_throughput_context(
        self,
        messages: list[SensationThroughputMessage],
        blocks: list[ThroughputBlock],
    ) -> list[SensationThroughputMessage]:
        if not blocks:
            return messages
        throughput_text = self._format_throughput_blocks(blocks)
        for idx in range(len(messages) - 1, -1, -1):
            if messages[idx].role == "user":
                content = messages[idx].content.rstrip()
                messages[idx].content = f"{content}\n\n{throughput_text}".strip()
                return messages
        messages.append(
            SensationThroughputMessage(role="user", content=throughput_text)
        )
        return messages

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
        throughput_style: str,
        throughput_focus: str,
        show_steps: bool,
        max_actions: int,
        prefix: str | None,
    ) -> str:
        show_steps_text = "yes" if show_steps else "no"
        rendered = self._render_template(
            template,
            throughput_style,
            throughput_focus,
            show_steps_text,
            max_actions,
        )
        if prefix and prefix.strip():
            return f"{prefix.strip()}\n\n{rendered}".strip()
        return rendered.strip()

    def _render_template(
        self,
        template: str,
        throughput_style: str,
        throughput_focus: str,
        show_steps_text: str,
        max_actions: int,
    ) -> str:
        had_placeholders = (
            "{throughput_style}" in template
            or "{throughput_focus}" in template
            or "{show_steps}" in template
            or "{max_actions}" in template
        )
        rendered = template
        if "{throughput_style}" in template:
            rendered = rendered.replace("{throughput_style}", throughput_style)
        if "{throughput_focus}" in template:
            rendered = rendered.replace("{throughput_focus}", throughput_focus)
        if "{show_steps}" in template:
            rendered = rendered.replace("{show_steps}", show_steps_text)
        if "{max_actions}" in template:
            rendered = rendered.replace("{max_actions}", str(max_actions))

        if had_placeholders:
            return rendered

        extra = (
            f"Throughput style: {throughput_style}\n"
            f"Throughput focus: {throughput_focus}\n"
            f"Show steps: {show_steps_text}\n"
            f"Max actions: {max_actions}"
        )
        return f"{rendered.rstrip()}\n\n{extra}"

    def _normalize_messages(
        self, args: SensationThroughputManagementArgs, system_prompt: str
    ) -> list[SensationThroughputMessage]:
        messages: list[SensationThroughputMessage] = []
        if args.messages:
            for msg in args.messages:
                role = (msg.role or "").strip()
                content = (msg.content or "").strip()
                if not content:
                    continue
                if not role:
                    role = "user"
                messages.append(SensationThroughputMessage(role=role, content=content))
        elif args.prompt and args.prompt.strip():
            messages.append(
                SensationThroughputMessage(role="user", content=args.prompt.strip())
            )
        else:
            raise ToolError("Provide prompt or messages.")

        if not messages:
            raise ToolError("No usable messages provided.")

        if system_prompt.strip():
            messages.insert(
                0,
                SensationThroughputMessage(
                    role="system", content=system_prompt.strip()
                ),
            )
        return messages

    def _call_llm(
        self,
        messages: list[SensationThroughputMessage],
        args: SensationThroughputManagementArgs,
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
            sys.stdout.write("\n")
            sys.stdout.flush()
        return "".join(parts).strip()

    def _resolve_model(self, args: SensationThroughputManagementArgs) -> str:
        return args.llm_model or self.config.llm_model

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, SensationThroughputManagementArgs):
            return ToolCallDisplay(summary="sensation_throughput_management")
        return ToolCallDisplay(
            summary="sensation_throughput_management",
            details={
                "throughput_style": event.args.throughput_style,
                "throughput_focus": event.args.throughput_focus,
                "show_steps": event.args.show_steps,
            },
        )

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, SensationThroughputManagementResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )
        message = "Sensation throughput management complete"
        if event.result.errors:
            message = "Sensation throughput management finished with errors"
        return ToolResultDisplay(
            success=not bool(event.result.errors),
            message=message,
            warnings=event.result.warnings,
            details={
                "answer": event.result.answer,
                "used_throughput_style": event.result.used_throughput_style,
                "used_throughput_focus": event.result.used_throughput_focus,
                "show_steps": event.result.show_steps,
                "max_actions": event.result.max_actions,
                "template_source": event.result.template_source,
                "throughput_blocks": len(event.result.throughput_blocks),
                "errors": event.result.errors,
            },
        )

    @classmethod
    def get_status_text(cls) -> str:
        return "Sensation throughput management"


