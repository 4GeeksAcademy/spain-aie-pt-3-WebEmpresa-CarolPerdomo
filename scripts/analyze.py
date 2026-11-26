#!/usr/bin/env python3
"""Analyze Nexova support tickets without exposing individual records."""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from services.api.incident_analysis import CATEGORIES, FIELDS, ISSUES, STATUSES, analyze, metrics


def print_report(result):
    totals, issues, categories, statuses, scores = result
    print("=" * 60)
    print("  NEXOVA - ANALISIS DE INCIDENCIAS")
    print("=" * 60)
    for label, value in metrics(result)[:3]:
        print(f"{label:.<48} {value:>8}")

    print("\nREGISTROS INVALIDOS POR MOTIVO")
    for key, label in ISSUES.items():
        print(f"{label:.<48} {issues[key]:>8}")

    for title, names, counts in (
        ("CATEGORIAS (registros validos)", CATEGORIES, categories),
        ("ESTADOS (registros validos)", STATUSES, statuses),
    ):
        print(f"\n{title}")
        for name in names:
            percentage = counts[name] / totals["valid"] * 100 if totals["valid"] else 0
            print(f"{name:.<38} {counts[name]:>8}  ({percentage:>5.1f}%)")

    scored = sum(scores.values())
    average = sum(score * count for score, count in scores.items()) / scored if scored else None
    print("\nSATISFACCION (incidencias cerradas)")
    print(f"Con puntuacion: {scored} de {statuses['CLOSED']}")
    print(f"Puntuacion media: {average:.2f} / 5.00" if average is not None else "Puntuacion media: Sin datos")
    for score in range(1, 6):
        print(f"Puntuacion {score:.<37} {scores[score]:>8}")
    print("=" * 60)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analiza un CSV de incidencias de Nexova.")
    parser.add_argument("csv", type=Path, help="Ruta del CSV de incidencias")
    args = parser.parse_args(argv)
    try:
        result = analyze(args.csv)
    except (OSError, UnicodeError, csv.Error, ValueError):
        print("Error: no se pudo leer el CSV o su estructura es invalida.", file=sys.stderr)
        return 1

    print_report(result)
    while True:
        try:
            answer = input("¿Deseas exportar los resultados a CSV? [s / n] ").strip().lower()
        except EOFError:
            print("\nExportacion omitida.")
            return 0
        if answer == "n":
            return 0
        if answer == "s":
            try:
                destination = Path("results.csv")
                if destination.exists() and destination.samefile(args.csv):
                    print("Error: results.csv es el archivo de entrada; no se puede sobrescribir.", file=sys.stderr)
                    return 1
                with destination.open("w", encoding="utf-8", newline="") as output:
                    writer = csv.writer(output)
                    writer.writerow(("metrica", "valor"))
                    writer.writerows(metrics(result))
            except OSError:
                print("Error: no se pudo escribir results.csv.", file=sys.stderr)
                return 1
            print("Resultados exportados a results.csv.")
            return 0
        print("Responde s o n.")


if __name__ == "__main__":
    sys.exit(main())