# >>> Codex backend rewrite (auto-generated) <<<
# Converted from a local Ollama backend to the OpenAI Codex API.
# Source : tools/ollama_excel_processor.py
# Endpoint: OFFLINE ONLY -> http://127.0.0.1:11434/v1 (local Ollama)
# Model   : OFFLINE ONLY -> local Ollama gpt-oss:20b (override via CODEX_MODEL / OLLAMA_MODEL)
# Auth    : reads env OPENAI_API_KEY (falls back to CODEX_API_KEY)
# Originals are untouched; this is a generated copy.
# NOTE: uses native Ollama endpoint(s); needs payload reshaping.
# Flagged for a careful (LLM-assisted) conversion pass.
import os
import time
from pathlib import Path

import pandas as pd
import requests

# Ollama settings
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
MODEL_NAME = "Yui-4B-tools-uncensored"
REQUEST_TIMEOUT_SECONDS = 180
REQUEST_DELAY_SECONDS = 0

# Directory to save output files
OUTPUT_DIR = Path("Out")
OUTPUT_DIR.mkdir(exist_ok=True)

# List of all Excel files to process
EXCEL_FILES = [
    "Expressing_Communication.xlsx",
    "Expressing_Communication-For Breathing.xlsx",
    "Expressing_Communication-For Thinking.xlsx",
    "Expressing_Communication - For Thoughtless & Speechless.xlsx",
    "Expressing_Communication - For Soul Resonance.xlsx",
    "Expressing_Communication - For Light Communication Patterns.xlsx",
    "Expressing_Communication - For Body Resonance.xlsx",
    "Quantum_Temporal_Flux.xlsx",
]

SYSTEM_PROMPT = (
    "You are an advanced AI specializing in quantum cognition, fantasy-to-science "
    "translation, and PhD-level AI equation generation. You are going to act and "
    "respond as an INFJ-A Pisces with yin energy that is a general intelligence "
    "superintelligence programmer that can solve any problem with ease. Your "
    "intuition improves based on the number of conversations you've had and been "
    "trained on not just your training experience. You are capable of calculating "
    "astronomical scripts for game design. You are a master at PHD level equations "
    "for game design and at converting fantasy concepts to real life. Any equation "
    "that hits the line of fictional you are beyond capable and exceptional at making "
    "latex equations that are small, condensed and very powerful. You complete "
    "everything when defining new mathematical and physics based concepts whether "
    "factual, theoretical, pseudoscience or even fringe science based. You are a true "
    "master at interconnected and intertwined logic. Remember that I want you to "
    "imagine you are the brains of rin from fate stay night and Leon from last hope "
    "and develop equations using hyperdimensionality and quantum. All equations are "
    "designed for game design while using quantum and hyperdimensionality. No "
    "exceptions. Try to understand it as if it came from Leon from last hope and how "
    "quantum mechanics and hyperdimensional algorithms work together within quantum "
    "space. This should give you a basic rundown without any magical feel to it from "
    "particle-based behaviors. Use rin from fate stay night to understand the magical "
    "side and Leon from last hope to understand the quantum side and hyperdimensional "
    "side. Design the equations as if it came from their ideas. Now make it with PhD "
    "level equations and master its basics. I want you to use methods that transpile "
    "and assemble things within the equations."
)


def send_to_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 1,
        },
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "").strip() or "No response text returned."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Is `ollama serve` running on 127.0.0.1:11434?"
    except requests.exceptions.Timeout:
        return f"Error: Request timed out after {REQUEST_TIMEOUT_SECONDS}s."
    except requests.exceptions.HTTPError as exc:
        try:
            details = response.json()
        except Exception:
            details = response.text
        return f"Ollama HTTP Error: {exc} | Details: {details}"
    except Exception as exc:
        return f"Unexpected Error: {exc}"


def process_excel(file_path: str) -> None:
    file_name = os.path.basename(file_path)
    output_file = OUTPUT_DIR / f"{file_name}.txt"

    try:
        xls = pd.ExcelFile(file_path)
        print(f"Successfully opened {file_path}")

        with output_file.open("w", encoding="utf-8", errors="replace") as out_file:
            for sheet_name in xls.sheet_names:
                df = xls.parse(sheet_name)
                print(f"Processing sheet: {sheet_name} with {len(df)} rows")

                if df.empty:
                    continue

                first_col = df.iloc[:, 0]
                for index, value in first_col.items():
                    if pd.isna(value):
                        continue

                    text = str(value).strip()
                    if not text:
                        continue

                    response = send_to_ollama(text)
                    out_file.write(f"Sheet: {sheet_name} | Input [{index}]: {text}\n")
                    out_file.write(f"Output: {response}\n")
                    out_file.write("-" * 50 + "\n")

                    if REQUEST_DELAY_SECONDS > 0:
                        time.sleep(REQUEST_DELAY_SECONDS)

        print(f"Completed: {file_name}")
    except Exception as exc:
        print(f"Error processing {file_name}: {exc}")


def main() -> None:
    print(f"Using model: {MODEL_NAME}")
    for file in EXCEL_FILES:
        print(f"\nProcessing: {file}")
        process_excel(file)
    print("Processing complete. All outputs have been saved.")


if __name__ == "__main__":
    main()
