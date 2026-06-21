# >>> Codex backend rewrite (auto-generated) <<<
# Converted from a local Ollama backend to the OpenAI Codex API.
# Source : tools/python_file_qubit_circuits_aer.py
# Endpoint: OFFLINE ONLY -> http://127.0.0.1:11434/v1 (local Ollama)
# Model   : OFFLINE ONLY -> local Ollama gpt-oss:20b (override via CODEX_MODEL / OLLAMA_MODEL)
# Auth    : reads env OPENAI_API_KEY (falls back to CODEX_API_KEY)
# Originals are untouched; this is a generated copy.
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

try:
    from qiskit import assemble as _qiskit_assemble
except ImportError:
    _qiskit_assemble = None


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".ruff_cache",
    ".svn",
    "__pycache__",
    "build",
    "dist",
    "env",
    "node_modules",
    "site-packages",
    "venv",
    ".venv",
}

DEFAULT_PIPELINE_APP_DIR = Path("android_auto_python_bridge")

LLM_MISTRAL_MARKERS = (
    "llm_model",
    "llm_api_base",
    "llm_temperature",
    "llm_max_tokens",
    "llm_stream",
    "chat/completions",
    "openai-compatible api",
    "gpt-5.4-mini",
    "codex",
    "ollama",
)


@dataclass(frozen=True)
class FileCandidate:
    key: str
    path: Path


def assemble(circuits: QuantumCircuit, **run_options: object) -> object:
    """Compatibility wrapper for Qiskit's removed assemble API in v2+."""
    if _qiskit_assemble is not None:
        return _qiskit_assemble(circuits, **run_options)
    return {"circuits": circuits, "run_options": run_options}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create and simulate one qubit-only Qiskit Aer circuit for every Python "
            "file under a root directory."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory to scan recursively for *.py files.",
    )
    parser.add_argument(
        "--output",
        default="python_file_qubit_circuits_aer.json",
        help="Output JSON file path.",
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "pipeline", "scan"),
        default="auto",
        help=(
            "'pipeline' reads Android auto manifest, 'scan' recursively scans root, "
            "'auto' prefers pipeline and falls back to scan."
        ),
    )
    parser.add_argument(
        "--android-app-dir",
        default=str(DEFAULT_PIPELINE_APP_DIR),
        help=(
            "Android app directory containing app/src/main/assets/python_scripts_manifest.json "
            "and app/src/main/python/generated_scripts."
        ),
    )
    parser.add_argument(
        "--manifest-path",
        default=None,
        help="Optional explicit manifest path; overrides --android-app-dir manifest location.",
    )
    parser.add_argument(
        "--qubits",
        type=int,
        default=8,
        help="Number of qubits per file circuit.",
    )
    parser.add_argument(
        "--max-layers",
        type=int,
        default=8,
        help="Maximum gate layers encoded from each file.",
    )
    parser.add_argument(
        "--optimization-level",
        type=int,
        choices=(0, 1, 2, 3),
        default=1,
        help="Transpiler optimization level.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Simulator seed.",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help=(
            "Directory name to exclude. Repeat this flag to add more excluded "
            "directory names."
        ),
    )
    parser.add_argument(
        "--allow-llm-files",
        action="store_true",
        help="Include files that appear to be LLM/Mistral related. Disabled by default.",
    )
    return parser.parse_args()


def list_python_files(root: Path, excluded_dirs: set[str]) -> list[FileCandidate]:
    files: list[FileCandidate] = []
    for path in root.rglob("*.py"):
        if any(part in excluded_dirs for part in path.parts):
            continue
        if not path.is_file():
            continue
        files.append(FileCandidate(key=str(path.relative_to(root)), path=path))
    files.sort(key=lambda item: item.key)
    return files


def file_digest_bytes(data: bytes, minimum_size: int) -> bytes:
    digest = hashlib.sha256(data).digest()
    while len(digest) < minimum_size:
        digest += hashlib.sha256(digest).digest()
    return digest


def build_qubit_only_circuit(
    file_path: Path,
    data: bytes,
    qubits: int,
    max_layers: int,
) -> QuantumCircuit:
    if qubits < 1:
        raise ValueError("qubits must be >= 1")
    if max_layers < 1:
        raise ValueError("max_layers must be >= 1")

    payload = data if data else b"\x00"
    digest = file_digest_bytes(payload, qubits + 16)
    layer_count = max(1, min(max_layers, math.ceil(len(payload) / max(1, qubits * 2))))

    circuit = QuantumCircuit(qubits, name=file_path.name)

    # Seed the register deterministically from file content hash.
    for index in range(qubits):
        if digest[index] & 1:
            circuit.x(index)

    for layer in range(layer_count):
        for index in range(qubits):
            p_idx = (layer * qubits + index) % len(payload)
            d_idx = (layer * qubits + index) % len(digest)
            theta = (payload[p_idx] / 255.0) * math.tau
            phi = (digest[d_idx] / 255.0) * math.tau
            circuit.ry(theta, index)
            circuit.rz(phi, index)

        if qubits > 1:
            for index in range(qubits - 1):
                circuit.cx(index, index + 1)
            if qubits > 2:
                circuit.cx(qubits - 1, 0)

    # Keep circuits qubit-only: no classical registers, no measurements.
    circuit.save_statevector()
    return circuit


def normalize_manifest_path(args: argparse.Namespace) -> Path:
    if args.manifest_path:
        return Path(args.manifest_path).resolve()
    app_dir = Path(args.android_app_dir).resolve()
    return app_dir / "app" / "src" / "main" / "assets" / "python_scripts_manifest.json"


def load_pipeline_candidates(manifest_path: Path) -> tuple[list[FileCandidate], list[str]]:
    warnings: list[str] = []
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Manifest JSON parse failed: {exc}") from exc

    scripts = payload.get("scripts", []) if isinstance(payload, dict) else []
    if not isinstance(scripts, list):
        raise ValueError("Manifest field 'scripts' must be a list.")

    app_main = manifest_path.parent.parent
    python_root = app_main / "python"

    seen: set[str] = set()
    candidates: list[FileCandidate] = []
    for item in scripts:
        if not isinstance(item, dict):
            continue
        staged_path_raw = item.get("staged_path")
        if not isinstance(staged_path_raw, str) or not staged_path_raw.endswith(".py"):
            continue
        source_path = item.get("source_path")
        key = source_path if isinstance(source_path, str) and source_path else staged_path_raw
        staged_path = Path(staged_path_raw)
        full_path = (python_root / staged_path).resolve()
        if not full_path.exists():
            warnings.append(f"Missing staged script: {full_path}")
            continue
        canonical = str(full_path)
        if canonical in seen:
            continue
        seen.add(canonical)
        candidates.append(FileCandidate(key=key, path=full_path))

    candidates.sort(key=lambda item: item.key)
    return candidates, warnings


def looks_like_llm_or_mistral(path: Path, data: bytes) -> bool:
    path_text = str(path).replace("\\", "/").lower()
    if "codex" in path_text:
        return True
    if "/models/" in path_text and ("gpt" in path_text or "llm" in path_text or "mistral" in path_text):
        return True

    text = data[:200_000].decode("utf-8", errors="ignore").lower()
    return any(marker in text for marker in LLM_MISTRAL_MARKERS)


def resolve_candidates(
    args: argparse.Namespace,
    root: Path,
    excluded_dirs: set[str],
) -> tuple[str, list[FileCandidate], list[str], str | None]:
    warnings: list[str] = []
    manifest_path = normalize_manifest_path(args)

    if args.mode in {"auto", "pipeline"}:
        try:
            files, manifest_warnings = load_pipeline_candidates(manifest_path)
            warnings.extend(manifest_warnings)
            return "pipeline", files, warnings, str(manifest_path)
        except Exception as exc:
            if args.mode == "pipeline":
                raise
            warnings.append(f"Pipeline mode unavailable ({exc}); falling back to scan mode.")

    files = list_python_files(root, excluded_dirs)
    return "scan", files, warnings, None


def dominant_state(statevector: object, qubits: int) -> tuple[str, float]:
    amplitudes = getattr(statevector, "data", statevector)
    max_index = 0
    max_probability = 0.0
    for index, amplitude in enumerate(amplitudes):
        probability = float((amplitude.real * amplitude.real) + (amplitude.imag * amplitude.imag))
        if probability > max_probability:
            max_probability = probability
            max_index = index
    state = format(max_index, f"0{qubits}b")
    return state, max_probability


def simulate_circuit(
    backend: AerSimulator,
    circuit: QuantumCircuit,
    optimization_level: int,
    qubits: int,
) -> dict[str, object]:
    transpiled = transpile(circuit, backend=backend, optimization_level=optimization_level)
    assembled = assemble(transpiled, shots=1)
    if isinstance(assembled, dict) and "circuits" in assembled:
        result = backend.run(assembled["circuits"], **assembled["run_options"]).result()
    else:
        result = backend.run(assembled).result()
    statevector = result.get_statevector(transpiled)
    top_state, top_probability = dominant_state(statevector, qubits)
    return {
        "depth": transpiled.depth(),
        "size": transpiled.size(),
        "top_state": top_state,
        "top_state_probability": top_probability,
    }


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output).resolve()

    excluded_dirs = set(DEFAULT_EXCLUDED_DIRS)
    excluded_dirs.update(args.exclude_dir)

    selected_mode, files, mode_warnings, manifest_used = resolve_candidates(
        args=args,
        root=root,
        excluded_dirs=excluded_dirs,
    )
    backend = AerSimulator(method="statevector", seed_simulator=args.seed)

    records: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    for candidate in files:
        try:
            data = candidate.path.read_bytes()
            if not args.allow_llm_files and looks_like_llm_or_mistral(candidate.path, data):
                skipped.append({"file": candidate.key, "reason": "llm_or_mistral_marker"})
                continue
            circuit = build_qubit_only_circuit(
                file_path=candidate.path,
                data=data,
                qubits=args.qubits,
                max_layers=args.max_layers,
            )
            simulation = simulate_circuit(
                backend=backend,
                circuit=circuit,
                optimization_level=args.optimization_level,
                qubits=args.qubits,
            )
            records.append(
                {
                    "file": candidate.key,
                    "path": str(candidate.path),
                    "bytes": len(data),
                    "qubits": args.qubits,
                    "layers": max(1, min(args.max_layers, math.ceil(max(1, len(data)) / max(1, args.qubits * 2)))),
                    **simulation,
                }
            )
        except Exception as exc:
            errors.append(
                {
                    "file": str(candidate.path),
                    "error": str(exc),
                }
            )

    payload = {
        "root": str(root),
        "mode": selected_mode,
        "pipeline_manifest": manifest_used,
        "allow_llm_files": bool(args.allow_llm_files),
        "total_python_files": len(files),
        "skipped": len(skipped),
        "processed": len(records),
        "failed": len(errors),
        "qubits_per_circuit": args.qubits,
        "max_layers": args.max_layers,
        "optimization_level": args.optimization_level,
        "seed": args.seed,
        "warnings": mode_warnings,
        "records": records,
        "skipped_records": skipped,
        "errors": errors,
    }

    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Scanned: {len(files)}")
    print(f"Mode: {selected_mode}")
    if manifest_used:
        print(f"Manifest: {manifest_used}")
    print(f"Skipped: {len(skipped)}")
    print(f"Processed: {len(records)}")
    print(f"Failed: {len(errors)}")
    print(f"Output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
