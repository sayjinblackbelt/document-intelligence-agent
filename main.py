"""Ponto de entrada do MVP."""

from pathlib import Path

from app.analyzer import analyze_directory
from app.report import save_report

ROOT = Path(__file__).resolve().parent
SAMPLE_DATA = ROOT / "sample_data"
OUTPUT = ROOT / "output" / "analysis_report.json"


def main() -> None:
    results = analyze_directory(SAMPLE_DATA)
    save_report(results, OUTPUT)

    print("DOCUMENT INTELLIGENCE AGENT")
    print(f"Documentos analisados: {len(results)}")
    print(f"Relatório: {OUTPUT}")


if __name__ == "__main__":
    main()
