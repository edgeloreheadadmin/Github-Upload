# >>> Codex backend rewrite (auto-generated) <<<
# Converted from a local Ollama backend to the OpenAI Codex API.
# Source : tools/cybernetic_feedback_control.py
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


DEFAULT_PROMPT_TEMPLATE = """### CYBERNETIC FEEDBACK + STILLNESS MODE (OPT-IN)
Integrate cybernetic feedback across social, cognitive, sensory, and physiological layers.
- Model signals, feedback loops, control boundaries, and stability targets.
- Include teamwork/communication/charisma/morale/mood/body language dynamics.
- Include biorhythms, SCN responses, breathing patterns, balance, and stability.
- Address stillness states (speechless, thoughtless, silence, quiet, stillness, empty vs nothing).
- Distinguish conscious control vs guided/automatic/autopilot responses.
- Map sensory limits, calming of nerves, and steady breathing intervals.
- Map light/dark spectra (shades, shadows, darkness, illumination, luminescence) and natural vs artificial.
- Map act/move/do between control and automatic responses.
- Quantify timing: reaction/response time, wait/completion time, loops/cycles, completion ratios.
- Include stamina/vigilance/energy/endurance, patience via wait ratios, temperance via weight and temperature.
- Note origins of habits, behaviors, etiquette, mannerisms, reactions, and responses.
- Keep it conceptual; do not provide medical diagnosis or risky health directives.
- If the user asks for steps or show_steps is enabled, give a concise outline.

Focus: {focus}
Domains: {domains}
States: {states}
Control modes: {control_modes}
Physiology: {physiology}
Timing metrics: {timing_metrics}
Light/Dark frame: {light_dark}
Show steps: {show_steps}
Max steps: {max_steps}
"""

TOOL_PROMPT = (
    "Use `cybernetic_feedback_control` to integrate cybernetic feedback across "
    "social and physiological layers. Provide `prompt` or `messages`, and "
    "optionally set `focus`, `domains`, `states`, `control_modes`, "
    "`physiology`, `timing_metrics`, `light_dark`, `show_steps`, and `max_steps`."
)


@dataclass(frozen=True)
class _FeedbackSource:
    content: str
    label: str | None
    layer: str | None
    source_path: str | None


class CyberneticFeedbackMessage(BaseModel):
    role: str
    content: str


class CyberneticFeedbackContextItem(BaseModel):
    id: str | None = Field(default=None, description="Optional item id.")
    label: str | None = Field(default=None, description="Optional label.")
    layer: str | None = Field(
        default=None, description="Domain or layer label."
    )
    state: str | None = Field(
        default=None, description="State or mode (silence, autopilot, etc.)."
    )
    signal: str | None = Field(
        default=None, description="Observed signal or cue."
    )
    metric: str | None = Field(
        default=None, description="Timing or measurement detail."
    )
    constraint: str | None = Field(
        default=None, description="Boundary or constraint description."
    )
    physiology: str | None = Field(
        default=None, description="Breath, rhythm, SCN, or body detail."
    )
    light_dark: str | None = Field(
        default=None, description="Light/dark framing or contrast."
    )
    content: str | None = Field(
        default=None, description="Inline context content."
    )
    path: str | None = Field(
        default=None, description="Path to a context file."
    )
    tags: list[str] | None = Field(default=None, description="Optional tags.")


class CyberneticFeedbackArgs(BaseModel):
    prompt: str | None = Field(
        default=None, description="User prompt to solve."
    )
    messages: list[CyberneticFeedbackMessage] | None = Field(
        default=None, description="Optional chat messages."
    )
    system_prompt: str | None = Field(
        default=None, description="Optional system prompt prefix."
    )
    focus: str | None = Field(
        default=None, description="Focus or scenario label."
    )
    domains: list[str] | None = Field(
        default=None, description="Domain layers to include."
    )
    states: list[str] | None = Field(
        default=None, description="Stillness or silence states to include."
    )
    control_modes: list[str] | None = Field(
        default=None, description="Control/auto modes to include."
    )
    physiology: list[str] | None = Field(
        default=None, description="Physiological rhythm layers."
    )
    timing_metrics: list[str] | None = Field(
        default=None, description="Timing and completion metrics."
    )
    light_dark: list[str] | None = Field(
        default=None, description="Light/dark frames to include."
    )
    show_steps: bool | None = Field(
        default=None, description="Whether to include a step outline."
    )
    max_steps: int | None = Field(
        default=None, description="Maximum steps in the outline."
    )
    feedback_inputs: list[CyberneticFeedbackContextItem] | None = Field(
        default=None, description="Context items for feedback synthesis."
    )
    feedback_paths: list[str] | None = Field(
        default=None, description="Additional context file paths."
    )
    max_feedback_chars: int | None = Field(
        default=None, description="Max chars per feedback item."
    )
    max_feedback_total_chars: int | None = Field(
        default=None, description="Max total feedback chars."
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


class FeedbackBlock(BaseModel):
    label: str | None
    layer: str | None
    source_path: str | None
    content: str
    truncated: bool


class CyberneticFeedbackResult(BaseModel):
    answer: str
    system_prompt: str
    messages: list[CyberneticFeedbackMessage]
    used_focus: str
    used_domains: list[str]
    used_states: list[str]
    used_control_modes: list[str]
    used_physiology: list[str]
    used_timing_metrics: list[str]
    used_light_dark: list[str]
    show_steps: bool
    max_steps: int
    template_source: str
    feedback_blocks: list[FeedbackBlock]
    warnings: list[str]
    errors: list[str]
    llm_model: str


class CyberneticFeedbackConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ASK
    llm_api_base: str = Field(
        default_factory=_codex_default_base,
        description="OpenAI-compatible API base URL.",
    )
    llm_model: str = Field(
        default_factory=_codex_default_model, description="Default LLM model name."
    )
    default_focus: str = Field(
        default=(
            "Cybernetic feedback across teamwork, communication, charisma, "
            "morale, moods, body language, biorhythms, SCN responses, "
            "breathing patterns, balance, and stability."
        ),
        description="Default focus label.",
    )
    default_domains: list[str] = Field(
        default_factory=lambda: [
            "teamwork",
            "communication",
            "charisma",
            "morale",
            "moods",
            "body language",
        ],
        description="Default domain layers.",
    )
    default_states: list[str] = Field(
        default_factory=lambda: [
            "speechless",
            "thoughtless",
            "silence",
            "quiet",
            "stillness",
            "complete nothing",
            "complete empty",
        ],
        description="Default stillness states.",
    )
    default_control_modes: list[str] = Field(
        default_factory=lambda: [
            "guided path",
            "automatic control",
            "autopilot",
            "conscious control",
            "nonconscious response",
            "subliminal to conscious shift",
            "limits and boundaries",
            "honing senses",
            "calming nerves",
        ],
        description="Default control modes.",
    )
    default_physiology: list[str] = Field(
        default_factory=lambda: [
            "biorhythms",
            "SCN responses",
            "breathing patterns",
            "balance",
            "stability",
            "muscle/reflex responses",
            "reaction time",
            "response time",
            "stamina",
            "vigilance",
            "energy",
            "endurance",
            "body temperature",
            "hormone cues",
        ],
        description="Default physiology layers.",
    )
    default_timing_metrics: list[str] = Field(
        default_factory=lambda: [
            "wait times",
            "completion times",
            "loops",
            "cycles",
            "completion ratios",
            "interaction speed (fast/slow)",
        ],
        description="Default timing metrics.",
    )
    default_light_dark: list[str] = Field(
        default_factory=lambda: [
            "shades",
            "shadows",
            "darkness",
            "illumination",
            "luminescence",
            "natural vs artificial light",
            "empty vs nothing",
        ],
        description="Default light/dark frames.",
    )
    default_show_steps: bool = Field(
        default=False, description="Default for show_steps."
    )
    default_max_steps: int = Field(
        default=7, description="Default max steps."
    )
    prompt_path: Path | None = Field(
        default=Path.home()
        / "codex"
        / "codex"
        / "core"
        / "prompts"
        / "cybernetic_feedback_control.md",
        description="Optional path to a prompt template.",
    )
    prompt_max_chars: int = Field(
        default=10000, description="Maximum template characters to load."
    )
    max_feedback_chars: int = Field(
        default=4000, description="Maximum characters per feedback item."
    )
    max_feedback_total_chars: int = Field(
        default=12000, description="Maximum total feedback characters."
    )


class CyberneticFeedbackState(BaseToolState):
    pass


class CyberneticFeedbackControl(
    BaseTool[
        CyberneticFeedbackArgs,
        CyberneticFeedbackResult,
        CyberneticFeedbackConfig,
        CyberneticFeedbackState,
    ],
    ToolUIData[CyberneticFeedbackArgs, CyberneticFeedbackResult],
):
    description: ClassVar[str] = (
        "Integrate cybernetic feedback across social and physiological layers."
    )

    @classmethod
    def get_tool_prompt(cls) -> str | None:
        return TOOL_PROMPT

    async def run(
        self, args: CyberneticFeedbackArgs
    ) -> CyberneticFeedbackResult:
        warnings: list[str] = []
        errors: list[str] = []

        focus = (args.focus or self.config.default_focus).strip()
        if not focus:
            focus = "cybernetic feedback integration"

        domains = self._normalize_list(
            args.domains, self.config.default_domains, "domains"
        )
        states = self._normalize_list(
            args.states, self.config.default_states, "states"
        )
        control_modes = self._normalize_list(
            args.control_modes,
            self.config.default_control_modes,
            "control_modes",
        )
        physiology = self._normalize_list(
            args.physiology, self.config.default_physiology, "physiology"
        )
        timing_metrics = self._normalize_list(
            args.timing_metrics,
            self.config.default_timing_metrics,
            "timing_metrics",
        )
        light_dark = self._normalize_list(
            args.light_dark, self.config.default_light_dark, "light_dark"
        )

        show_steps = (
            args.show_steps
            if args.show_steps is not None
            else self.config.default_show_steps
        )
        max_steps = (
            args.max_steps
            if args.max_steps is not None
            else self.config.default_max_steps
        )
        if max_steps <= 0:
            raise ToolError("max_steps must be positive.")

        self._validate_llm_settings(args)

        template, template_source = self._load_template(warnings)
        system_prompt = self._build_system_prompt(
            template,
            focus,
            domains,
            states,
            control_modes,
            physiology,
            timing_metrics,
            light_dark,
            show_steps,
            max_steps,
            args.system_prompt,
        )

        feedback_blocks = self._collect_feedback_inputs(args, warnings)
        messages = self._normalize_messages(args, system_prompt)
        messages = self._inject_feedback_context(messages, feedback_blocks)
        answer = self._call_llm(messages, args)

        return CyberneticFeedbackResult(
            answer=answer,
            system_prompt=system_prompt,
            messages=messages,
            used_focus=focus,
            used_domains=domains,
            used_states=states,
            used_control_modes=control_modes,
            used_physiology=physiology,
            used_timing_metrics=timing_metrics,
            used_light_dark=light_dark,
            show_steps=show_steps,
            max_steps=max_steps,
            template_source=template_source,
            feedback_blocks=feedback_blocks,
            warnings=warnings,
            errors=errors,
            llm_model=self._resolve_model(args),
        )

    def _normalize_list(
        self, values: list[str] | None, fallback: list[str], label: str
    ) -> list[str]:
        items = values if values is not None else list(fallback)
        normalized: list[str] = []
        seen: set[str] = set()
        for value in items:
            if not value or not value.strip():
                continue
            clean = value.strip()
            key = clean.lower()
            if key not in seen:
                normalized.append(clean)
                seen.add(key)
        if not normalized:
            raise ToolError(f"{label} must include at least one entry.")
        return normalized

    def _validate_llm_settings(self, args: CyberneticFeedbackArgs) -> None:
        if args.llm_temperature < 0:
            raise ToolError("llm_temperature cannot be negative.")
        if args.llm_max_tokens <= 0:
            raise ToolError("llm_max_tokens must be positive.")

    def _collect_feedback_inputs(
        self, args: CyberneticFeedbackArgs, warnings: list[str]
    ) -> list[FeedbackBlock]:
        max_item = (
            args.max_feedback_chars
            if args.max_feedback_chars is not None
            else self.config.max_feedback_chars
        )
        max_total = (
            args.max_feedback_total_chars
            if args.max_feedback_total_chars is not None
            else self.config.max_feedback_total_chars
        )
        if max_item <= 0 or max_total <= 0:
            raise ToolError(
                "max_feedback_chars and max_feedback_total_chars must be positive."
            )

        sources = self._resolve_feedback_sources(args, warnings)
        blocks: list[FeedbackBlock] = []
        total_chars = 0

        for source in sources:
            if total_chars >= max_total:
                warnings.append(
                    "max_feedback_total_chars reached; truncating feedback inputs."
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
                FeedbackBlock(
                    label=source.label,
                    layer=source.layer,
                    source_path=source.source_path,
                    content=content,
                    truncated=truncated,
                )
            )

        if not blocks:
            warnings.append("No feedback context provided.")
        return blocks

    def _resolve_feedback_sources(
        self, args: CyberneticFeedbackArgs, warnings: list[str]
    ) -> list[_FeedbackSource]:
        sources: list[_FeedbackSource] = []
        if args.feedback_inputs:
            for item in args.feedback_inputs:
                sources.append(self._load_feedback_item(item))

        if args.feedback_paths:
            for raw_path in args.feedback_paths:
                path = self._resolve_path(raw_path)
                content = path.read_text("utf-8", errors="ignore")
                sources.append(
                    _FeedbackSource(
                        content=content,
                        label=path.name,
                        layer=None,
                        source_path=str(path),
                    )
                )

        if not sources and not warnings:
            warnings.append("No feedback context provided.")
        return sources

    def _load_feedback_item(
        self, item: CyberneticFeedbackContextItem
    ) -> _FeedbackSource:
        if item.content and item.path:
            raise ToolError("Provide content or path per feedback item, not both.")
        if not (
            item.content
            or item.path
            or item.layer
            or item.state
            or item.signal
            or item.metric
            or item.constraint
            or item.physiology
            or item.light_dark
        ):
            raise ToolError(
                "Each feedback item must provide content, details, or path."
            )

        label = item.label or item.id or item.path
        content = self._format_feedback_text(item)

        if item.path:
            path = self._resolve_path(item.path)
            file_content = path.read_text("utf-8", errors="ignore")
            combined = self._join_sections(content, "Content", file_content)
            return _FeedbackSource(
                content=combined,
                label=label or path.name,
                layer=item.layer,
                source_path=str(path),
            )

        return _FeedbackSource(
            content=content,
            label=label,
            layer=item.layer,
            source_path=None,
        )

    def _format_feedback_text(self, item: CyberneticFeedbackContextItem) -> str:
        lines: list[str] = []
        if item.label or item.id:
            lines.append(f"Label: {item.label or item.id}")
        if item.layer:
            lines.append(f"Layer: {item.layer}")
        if item.state:
            lines.append(f"State: {item.state}")
        if item.signal:
            lines.append(f"Signal: {item.signal}")
        if item.metric:
            lines.append(f"Metric: {item.metric}")
        if item.constraint:
            lines.append(f"Constraint: {item.constraint}")
        if item.physiology:
            lines.append(f"Physiology: {item.physiology}")
        if item.light_dark:
            lines.append(f"Light/Dark: {item.light_dark}")
        if item.tags:
            tags = ", ".join(tag for tag in item.tags if tag)
            if tags:
                lines.append(f"Tags: {tags}")
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

    def _format_feedback_blocks(
        self, blocks: list[FeedbackBlock]
    ) -> str:
        if not blocks:
            return ""
        parts = ["Feedback context:"]
        for block in blocks:
            label = block.label or block.source_path or "feedback"
            layer_suffix = f" | {block.layer}" if block.layer else ""
            trunc = " (truncated)" if block.truncated else ""
            header = f"[{label}{layer_suffix}{trunc}]"
            parts.append(f"{header}\n{block.content}".strip())
        return "\n\n".join(parts).strip()

    def _inject_feedback_context(
        self,
        messages: list[CyberneticFeedbackMessage],
        blocks: list[FeedbackBlock],
    ) -> list[CyberneticFeedbackMessage]:
        if not blocks:
            return messages
        feedback_text = self._format_feedback_blocks(blocks)
        for idx in range(len(messages) - 1, -1, -1):
            if messages[idx].role == "user":
                content = messages[idx].content.rstrip()
                messages[idx].content = f"{content}\n\n{feedback_text}".strip()
                return messages
        messages.append(
            CyberneticFeedbackMessage(role="user", content=feedback_text)
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
        focus: str,
        domains: list[str],
        states: list[str],
        control_modes: list[str],
        physiology: list[str],
        timing_metrics: list[str],
        light_dark: list[str],
        show_steps: bool,
        max_steps: int,
        prefix: str | None,
    ) -> str:
        show_steps_text = "yes" if show_steps else "no"
        rendered = self._render_template(
            template,
            focus,
            ", ".join(domains),
            ", ".join(states),
            ", ".join(control_modes),
            ", ".join(physiology),
            ", ".join(timing_metrics),
            ", ".join(light_dark),
            show_steps_text,
            max_steps,
        )
        if prefix and prefix.strip():
            return f"{prefix.strip()}\n\n{rendered}".strip()
        return rendered.strip()

    def _render_template(
        self,
        template: str,
        focus: str,
        domains_text: str,
        states_text: str,
        control_modes_text: str,
        physiology_text: str,
        timing_metrics_text: str,
        light_dark_text: str,
        show_steps_text: str,
        max_steps: int,
    ) -> str:
        had_placeholders = (
            "{focus}" in template
            or "{domains}" in template
            or "{states}" in template
            or "{control_modes}" in template
            or "{physiology}" in template
            or "{timing_metrics}" in template
            or "{light_dark}" in template
            or "{show_steps}" in template
            or "{max_steps}" in template
        )
        rendered = template
        if "{focus}" in template:
            rendered = rendered.replace("{focus}", focus)
        if "{domains}" in template:
            rendered = rendered.replace("{domains}", domains_text)
        if "{states}" in template:
            rendered = rendered.replace("{states}", states_text)
        if "{control_modes}" in template:
            rendered = rendered.replace("{control_modes}", control_modes_text)
        if "{physiology}" in template:
            rendered = rendered.replace("{physiology}", physiology_text)
        if "{timing_metrics}" in template:
            rendered = rendered.replace("{timing_metrics}", timing_metrics_text)
        if "{light_dark}" in template:
            rendered = rendered.replace("{light_dark}", light_dark_text)
        if "{show_steps}" in template:
            rendered = rendered.replace("{show_steps}", show_steps_text)
        if "{max_steps}" in template:
            rendered = rendered.replace("{max_steps}", str(max_steps))

        if had_placeholders:
            return rendered

        extra = (
            f"Focus: {focus}\n"
            f"Domains: {domains_text}\n"
            f"States: {states_text}\n"
            f"Control modes: {control_modes_text}\n"
            f"Physiology: {physiology_text}\n"
            f"Timing metrics: {timing_metrics_text}\n"
            f"Light/Dark frame: {light_dark_text}\n"
            f"Show steps: {show_steps_text}\n"
            f"Max steps: {max_steps}"
        )
        return f"{rendered.rstrip()}\n\n{extra}"

    def _normalize_messages(
        self, args: CyberneticFeedbackArgs, system_prompt: str
    ) -> list[CyberneticFeedbackMessage]:
        messages: list[CyberneticFeedbackMessage] = []
        if args.messages:
            for msg in args.messages:
                role = (msg.role or "").strip()
                content = (msg.content or "").strip()
                if not content:
                    continue
                if not role:
                    role = "user"
                messages.append(
                    CyberneticFeedbackMessage(role=role, content=content)
                )
        elif args.prompt and args.prompt.strip():
            messages.append(
                CyberneticFeedbackMessage(
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
                CyberneticFeedbackMessage(
                    role="system", content=system_prompt.strip()
                ),
            )
        return messages

    def _call_llm(
        self,
        messages: list[CyberneticFeedbackMessage],
        args: CyberneticFeedbackArgs,
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

    def _resolve_model(self, args: CyberneticFeedbackArgs) -> str:
        return args.llm_model or self.config.llm_model

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, CyberneticFeedbackArgs):
            return ToolCallDisplay(summary="cybernetic_feedback_control")
        details = {
            "focus": event.args.focus,
            "domain_count": len(event.args.domains or []),
            "state_count": len(event.args.states or []),
            "show_steps": event.args.show_steps,
            "max_steps": event.args.max_steps,
        }
        return ToolCallDisplay(
            summary="cybernetic_feedback_control",
            details=details,
        )

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, CyberneticFeedbackResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )
        message = "Cybernetic feedback synthesis complete"
        if event.result.errors:
            message = "Cybernetic feedback synthesis finished with errors"
        return ToolResultDisplay(
            success=not bool(event.result.errors),
            message=message,
            warnings=event.result.warnings,
            details={
                "answer": event.result.answer,
                "used_focus": event.result.used_focus,
                "show_steps": event.result.show_steps,
                "max_steps": event.result.max_steps,
                "template_source": event.result.template_source,
                "errors": event.result.errors,
            },
        )

    @classmethod
    def get_status_text(cls) -> str:
        return "Cybernetic feedback synthesis"