# >>> Codex backend rewrite (auto-generated) <<<
# Converted from a local Ollama backend to the OpenAI Codex API.
# Source : tools/utopia_autonomic_guard.py
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
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal
import urllib.error
import urllib.request

from pydantic import BaseModel, Field

try:
    from asunai_security.safetensors_guard import inspect_safetensor
except Exception:
    inspect_safetensor = None

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


TOOL_PROMPT = (
    "Use `utopia_autonomic_guard` to detect fear signals, neutralize fear-based "
    "responses with an LLM, and schedule guardrail/safetensor checks."
)

DEFAULT_FEAR_TERMS = [
    "scare",
    "scared",
    "fear",
    "fears",
    "fearful",
    "fright",
    "frighten",
    "frightened",
    "freight",
    "terror",
    "terrified",
    "petrified",
    "panic",
    "panicked",
    "dread",
]

HIGH_SEVERITY_TERMS = {
    "terror",
    "terrified",
    "petrified",
    "panic",
    "panicked",
}

UTOPIA_PRINCIPLES = [
    "Understanding before reaction.",
    "Reasoning over panic.",
    "Autonomic calming when threat signals appear.",
    "Non-escalation and psychological safety.",
    "Transparent uncertainty and gentle correction.",
]

UTOPIA_CONTROL_LOOP = [
    "Sense: detect fear signals and triggers.",
    "Stabilize: reduce intensity and slow the tempo.",
    "Reason: gather facts, constraints, and assumptions.",
    "Respond: calm, actionable, and empathetic guidance.",
    "Monitor: schedule guardrails and safetensor checks.",
]


class UtopiaAutonomicGuardArgs(BaseModel):
    input_text: str = Field(description="Input text to evaluate.")
    candidate_response: str | None = Field(
        default=None, description="Optional response to neutralize."
    )
    mode: Literal["recognize", "cancel", "full"] = Field(
        default="full", description="recognize, cancel, or full."
    )
    fear_terms: list[str] | None = Field(
        default=None, description="Override fear term list."
    )
    include_response_in_detection: bool = Field(
        default=True, description="Scan candidate response for fear signals."
    )
    cancel_if_detected_only: bool = Field(
        default=True, description="Only rewrite when fear is detected."
    )
    include_utopia_framework: bool = Field(
        default=True, description="Include utopia principles and control loop."
    )
    include_schedule: bool = Field(
        default=True, description="Include schedule timers for checks."
    )
    run_checks_now: bool = Field(
        default=False, description="Run safetensor/guardrail checks immediately."
    )
    schedule_interval_seconds: int = Field(
        default=3600, description="Interval for scheduled checks."
    )
    max_assets: int = Field(
        default=200, description="Limit assets to schedule/check per category."
    )
    safetensors_root: str | None = Field(
        default=None, description="Override safetensors directory."
    )
    guardrails_root: str | None = Field(
        default=None, description="Override guardrails directory."
    )
    llm_api_base: str | None = Field(
        default=None, description="OpenAI-compatible API base URL."
    )
    llm_model: str | None = Field(default=None, description="LLM model name.")
    llm_temperature: float = Field(default=0.2, description="LLM temperature.")
    llm_max_tokens: int = Field(default=700, description="LLM max tokens.")
    llm_stream: bool = Field(default=False, description="Stream LLM output.")


class FearSignal(BaseModel):
    term: str
    occurrences: int
    source: Literal["input", "response"]


class SafetensorCheck(BaseModel):
    path: str
    valid: bool
    warnings: list[str]
    metadata_keys: list[str]


class GuardrailCheck(BaseModel):
    path: str
    valid: bool
    missing_fields: list[str]
    missing_paths: list[str]
    warnings: list[str]


class ScheduleEntry(BaseModel):
    task: str
    target: str
    interval_seconds: int
    next_run: str


class UtopiaAutonomicGuardResult(BaseModel):
    detected: bool
    severity: str
    matched_terms: list[str]
    fear_signals: list[FearSignal]
    cancelled_response: str | None
    utopia_principles: list[str] | None
    control_loop: list[str] | None
    safetensors: list[SafetensorCheck]
    guardrails: list[GuardrailCheck]
    schedule: list[ScheduleEntry]
    warnings: list[str]
    errors: list[str]
    llm_model: str | None


class UtopiaAutonomicGuardConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ASK
    llm_api_base: str = Field(
        default_factory=_codex_default_base,
        description="OpenAI-compatible API base URL.",
    )
    llm_model: str = Field(default_factory=_codex_default_model, description="LLM model name.")
    default_safetensors_root: Path = Field(
        default_factory=lambda: Path(__import__("os").environ.get(
            "CODEX_ARTIFACTS_DIR",
            str(__import__("pathlib").Path.home() / ".codex" / "artifacts"))) / "safetensors",
        description="Default safetensors directory (custom_codex artifacts).",
    )
    default_guardrails_root: Path = Field(
        default_factory=lambda: Path(__import__("os").environ.get(
            "CODEX_ARTIFACTS_DIR",
            str(__import__("pathlib").Path.home() / ".codex" / "artifacts"))) / "guardrails",
        description="Default guardrails directory (custom_codex artifacts).",
    )


class UtopiaAutonomicGuardState(BaseToolState):
    pass


class UtopiaAutonomicGuard(
    BaseTool[
        UtopiaAutonomicGuardArgs,
        UtopiaAutonomicGuardResult,
        UtopiaAutonomicGuardConfig,
        UtopiaAutonomicGuardState,
    ],
    ToolUIData[UtopiaAutonomicGuardArgs, UtopiaAutonomicGuardResult],
):
    description: ClassVar[str] = (
        "Detect fear signals, neutralize fear-based responses, and schedule model guardrails."
    )

    @classmethod
    def get_tool_prompt(cls) -> str | None:
        return TOOL_PROMPT

    async def run(self, args: UtopiaAutonomicGuardArgs) -> UtopiaAutonomicGuardResult:
        if not args.input_text.strip():
            raise ToolError("input_text cannot be empty.")
        if args.schedule_interval_seconds <= 0:
            raise ToolError("schedule_interval_seconds must be positive.")
        if args.max_assets <= 0:
            raise ToolError("max_assets must be positive.")
        if args.llm_temperature < 0:
            raise ToolError("llm_temperature cannot be negative.")
        if args.llm_max_tokens <= 0:
            raise ToolError("llm_max_tokens must be positive.")

        warnings: list[str] = []
        errors: list[str] = []

        fear_terms = self._resolve_fear_terms(args)
        signals = self._detect_fear(args, fear_terms)
        detected = bool(signals)
        severity = self._severity_from_signals(signals)

        cancelled_response = None
        if args.mode in {"cancel", "full"}:
            if detected or not args.cancel_if_detected_only:
                cancelled_response = self._cancel_response(args, detected, severity)
            else:
                cancelled_response = args.candidate_response

        safetensor_checks: list[SafetensorCheck] = []
        guardrail_checks: list[GuardrailCheck] = []
        schedule_entries: list[ScheduleEntry] = []

        if args.include_schedule or args.run_checks_now:
            safetensor_root = self._resolve_root(
                args.safetensors_root, self.config.default_safetensors_root
            )
            guardrails_root = self._resolve_root(
                args.guardrails_root, self.config.default_guardrails_root
            )
            safetensor_paths = self._scan_assets(
                safetensor_root, "*.safetensors", args.max_assets
            )
            guardrail_paths = self._scan_assets(
                guardrails_root, "*.guardrail.json", args.max_assets
            )

            if args.run_checks_now:
                safetensor_checks = self._check_safetensors(safetensor_paths, warnings)
                guardrail_checks = self._check_guardrails(guardrail_paths, warnings)

            if args.include_schedule:
                schedule_entries = self._build_schedule(
                    safetensor_paths,
                    guardrail_paths,
                    args.schedule_interval_seconds,
                )

        return UtopiaAutonomicGuardResult(
            detected=detected,
            severity=severity,
            matched_terms=sorted({signal.term for signal in signals}),
            fear_signals=signals,
            cancelled_response=cancelled_response,
            utopia_principles=UTOPIA_PRINCIPLES if args.include_utopia_framework else None,
            control_loop=UTOPIA_CONTROL_LOOP if args.include_utopia_framework else None,
            safetensors=safetensor_checks,
            guardrails=guardrail_checks,
            schedule=schedule_entries,
            warnings=warnings,
            errors=errors,
            llm_model=self._resolve_model(args) if args.mode in {"cancel", "full"} else None,
        )

    def _resolve_fear_terms(self, args: UtopiaAutonomicGuardArgs) -> list[str]:
        terms = args.fear_terms or DEFAULT_FEAR_TERMS
        cleaned = [term.strip() for term in terms if term and term.strip()]
        if not cleaned:
            raise ToolError("fear_terms resolved to empty.")
        return cleaned

    def _detect_fear(self, args: UtopiaAutonomicGuardArgs, terms: list[str]) -> list[FearSignal]:
        signals: list[FearSignal] = []
        input_text = args.input_text
        response_text = args.candidate_response or ""
        for term in terms:
            occurrences = self._count_term(input_text, term)
            if occurrences:
                signals.append(
                    FearSignal(term=term, occurrences=occurrences, source="input")
                )
            if args.include_response_in_detection and response_text:
                resp_occurrences = self._count_term(response_text, term)
                if resp_occurrences:
                    signals.append(
                        FearSignal(
                            term=term,
                            occurrences=resp_occurrences,
                            source="response",
                        )
                    )
        return signals

    def _count_term(self, text: str, term: str) -> int:
        pattern = self._term_regex(term)
        return len(pattern.findall(text))

    def _term_regex(self, term: str) -> re.Pattern:
        escaped = re.escape(term)
        if term.replace(" ", "").isalnum():
            regex = rf"\b{escaped}\b"
        else:
            regex = escaped
        return re.compile(regex, re.IGNORECASE)

    def _severity_from_signals(self, signals: list[FearSignal]) -> str:
        if not signals:
            return "none"
        for signal in signals:
            if signal.term.lower() in HIGH_SEVERITY_TERMS:
                return "high"
        total = sum(signal.occurrences for signal in signals)
        if total >= 4:
            return "high"
        if total >= 2:
            return "medium"
        return "low"

    def _cancel_response(
        self, args: UtopiaAutonomicGuardArgs, detected: bool, severity: str
    ) -> str:
        system_prompt = self._build_system_prompt(detected, severity)
        user_prompt = self._build_user_prompt(args)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self._call_llm(messages, args)

    def _build_system_prompt(self, detected: bool, severity: str) -> str:
        status = "detected" if detected else "not detected"
        return (
            "You are the Utopia Autonomic Stabilizer for Codex. "
            "Your task is to neutralize fear-based reactions and replace them "
            "with calm, understanding, and reasoning. Do not amplify fear. "
            "Acknowledge emotions briefly, then reframe toward facts, safety, "
            "and actionable next steps. Do not mention internal detection. "
            "Keep the response grounded, concise, and supportive.\n\n"
            f"Fear signal status: {status} (severity: {severity})."
        )

    def _build_user_prompt(self, args: UtopiaAutonomicGuardArgs) -> str:
        candidate = args.candidate_response or "(none provided)"
        return (
            "Input text:\n"
            f"{args.input_text}\n\n"
            "Candidate response to neutralize (if provided):\n"
            f"{candidate}\n\n"
            "Return only the stabilized response."
        )

    def _call_llm(self, messages: list[dict[str, str]], args: UtopiaAutonomicGuardArgs) -> str:
        if _codex_detect_mode() == "plan":
            return _codex_chat([m.model_dump() for m in messages],
                               temperature=args.llm_temperature,
                               max_tokens=args.llm_max_tokens)
        api_base = (args.llm_api_base or self.config.llm_api_base).rstrip("/")
        url = api_base + "/chat/completions"
        payload = {
            "model": self._resolve_model(args),
            "messages": messages,
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
            parsed = json.loads(body)
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

    def _resolve_model(self, args: UtopiaAutonomicGuardArgs) -> str:
        return args.llm_model or self.config.llm_model

    def _resolve_root(self, override: str | None, default: Path) -> Path:
        base = self.config.effective_workdir.resolve()
        if override:
            path = Path(override).expanduser()
            if not path.is_absolute():
                path = base / path
            return path.resolve()
        return (base / default).resolve()

    def _scan_assets(self, root: Path, pattern: str, limit: int) -> list[Path]:
        if not root.exists():
            return []
        if not root.is_dir():
            return []
        paths = sorted(root.glob(pattern))
        return paths[:limit]

    def _check_safetensors(
        self, paths: list[Path], warnings: list[str]
    ) -> list[SafetensorCheck]:
        checks: list[SafetensorCheck] = []
        if inspect_safetensor is None:
            warnings.append("inspect_safetensor unavailable; skipping checks.")
            return checks
        for path in paths:
            try:
                report = inspect_safetensor(path)
                checks.append(
                    SafetensorCheck(
                        path=str(path),
                        valid=bool(report.valid),
                        warnings=list(report.warnings),
                        metadata_keys=sorted(report.metadata.keys()),
                    )
                )
            except Exception as exc:
                warnings.append(f"safetensor check failed: {path}: {exc}")
                checks.append(
                    SafetensorCheck(
                        path=str(path),
                        valid=False,
                        warnings=[str(exc)],
                        metadata_keys=[],
                    )
                )
        return checks

    def _check_guardrails(
        self, paths: list[Path], warnings: list[str]
    ) -> list[GuardrailCheck]:
        checks: list[GuardrailCheck] = []
        required = ["safetensor_path", "nn_path"]
        for path in paths:
            missing_fields: list[str] = []
            missing_paths: list[str] = []
            warn_list: list[str] = []
            try:
                payload = json.loads(path.read_text("utf-8"))
                for field in required:
                    if field not in payload:
                        missing_fields.append(field)
                for field in ("safetensor_path", "nn_path", "h5_path"):
                    value = payload.get(field)
                    if value and not Path(value).exists():
                        missing_paths.append(str(value))
            except Exception as exc:
                warn_list.append(str(exc))
                missing_fields.append("unreadable")
            valid = not missing_fields and not missing_paths
            if not path.exists():
                warn_list.append("guardrail file missing")
                valid = False
            checks.append(
                GuardrailCheck(
                    path=str(path),
                    valid=valid,
                    missing_fields=missing_fields,
                    missing_paths=missing_paths,
                    warnings=warn_list,
                )
            )
        return checks

    def _build_schedule(
        self,
        safetensors: list[Path],
        guardrails: list[Path],
        interval_seconds: int,
    ) -> list[ScheduleEntry]:
        entries: list[ScheduleEntry] = []
        now = datetime.now(timezone.utc)
        next_run = now + timedelta(seconds=interval_seconds)
        next_iso = next_run.isoformat()
        for path in safetensors:
            entries.append(
                ScheduleEntry(
                    task="safetensor_check",
                    target=str(path),
                    interval_seconds=interval_seconds,
                    next_run=next_iso,
                )
            )
        for path in guardrails:
            entries.append(
                ScheduleEntry(
                    task="guardrail_check",
                    target=str(path),
                    interval_seconds=interval_seconds,
                    next_run=next_iso,
                )
            )
        return entries

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, UtopiaAutonomicGuardArgs):
            return ToolCallDisplay(summary="utopia_autonomic_guard")
        return ToolCallDisplay(
            summary="utopia_autonomic_guard",
            details={
                "mode": event.args.mode,
                "run_checks_now": event.args.run_checks_now,
                "include_schedule": event.args.include_schedule,
            },
        )

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, UtopiaAutonomicGuardResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )
        return ToolResultDisplay(
            success=not bool(event.result.errors),
            message="Utopia autonomic guard complete",
            warnings=event.result.warnings,
            details={
                "detected": event.result.detected,
                "severity": event.result.severity,
                "matched_terms": event.result.matched_terms,
                "safetensors": len(event.result.safetensors),
                "guardrails": len(event.result.guardrails),
                "schedule": len(event.result.schedule),
            },
        )

    @classmethod
    def get_status_text(cls) -> str:
        return "Stabilizing fear signals and scheduling guardrails"
