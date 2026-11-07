import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import analyze


class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "incidents.csv"

    def write_rows(self, rows):
        with self.path.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=analyze.FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def make_row(self, number, category="TECHNICAL", status="OPEN", score=""):
        return {
            "ticket_id": f"NXV-{number:06d}", "date": "2025-01-01",
            "client_company": "Empresa ficticia", "category": category,
            "description": "Incidencia ficticia", "agent_id": "AGT-01",
            "status": status, "customer_email": "fictional@example.invalid",
            "satisfaction_score": score,
        }

    def test_briefing_distribution_and_export(self):
        categories = [category for category, count in zip(analyze.CATEGORIES, (28, 18, 21, 17, 12)) for _ in range(count)]
        statuses = ["OPEN"] * 27 + ["CLOSED"] * 56 + ["DISCARDED"] * 13
        scores = [str(score) for score, count in enumerate((0, 2, 5, 10, 22, 17)) for _ in range(count)]
        rows = []
        for number, (category, status) in enumerate(zip(categories, statuses), 1):
            score = scores.pop(0) if status == "CLOSED" else ""
            rows.append(self.make_row(number, category, status, score))
        for number, field, value in (
            (97, "client_company", ""), (98, "category", "INVALID"),
            (99, "customer_email", "private-address-without-at"),
            (100, "satisfaction_score", ""),
        ):
            row = self.make_row(number, status="CLOSED", score="5")
            row[field] = value
            rows.append(row)
        self.write_rows(rows)

        result = analyze.analyze(self.path)
        totals, issues, categories, statuses, scores = result
        self.assertEqual((totals["total"], totals["valid"], totals["invalid"]), (100, 96, 4))
        self.assertEqual([categories[key] for key in analyze.CATEGORIES], [28, 18, 21, 17, 12])
        self.assertEqual([statuses[key] for key in analyze.STATUSES], [27, 56, 13])
        self.assertEqual([scores[key] for key in range(1, 6)], [2, 5, 10, 22, 17])
        self.assertEqual(sum(issues.values()), 4)
        self.assertEqual(dict(analyze.metrics(result))["Satisfaccion media"], "3.84")

        process = subprocess.run(
            [sys.executable, str(Path(analyze.__file__)), str(self.path)],
            input="s\n", text=True, capture_output=True, cwd=self.directory.name, check=True,
        )
        output = (Path(self.directory.name) / "results.csv").read_text(encoding="utf-8")
        self.assertIn("3.84", process.stdout)
        self.assertIn("Satisfaccion media,3.84", output)
        for private_value in ("fictional@example.invalid", "private-address-without-at"):
            self.assertNotIn(private_value, process.stdout + process.stderr + output)

    def test_multiple_issues_schema_and_empty_results(self):
        row = self.make_row(1, category="BAD", status="CLOSED", score="6")
        row["client_company"] = ""
        row["customer_email"] = "invalid"
        self.write_rows([row])
        totals, issues, categories, statuses, scores = analyze.analyze(self.path)
        self.assertEqual(totals["invalid"], 1)
        for issue in ("category", "client_company", "customer_email", "invalid_score"):
            self.assertEqual(issues[issue], 1)
        self.assertEqual(dict(analyze.metrics((totals, issues, categories, statuses, scores)))["Satisfaccion media"], "Sin datos")

    def test_duplicate_ids_and_malformed_rows(self):
        row = self.make_row(1)
        self.write_rows([row, row])
        with self.path.open("a", encoding="utf-8") as output:
            output.write("too,few,columns\n")
        totals, issues, *_ = analyze.analyze(self.path)
        self.assertEqual((totals["valid"], totals["invalid"]), (1, 2))
        self.assertEqual((issues["ticket_id"], issues["columns"]), (1, 1))

    def test_missing_header_fails_without_exposing_content(self):
        self.path.write_text("secret@example.invalid\n", encoding="utf-8")
        process = subprocess.run(
            [sys.executable, str(Path(analyze.__file__)), str(self.path)],
            text=True, capture_output=True, cwd=self.directory.name,
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertNotIn("secret@example.invalid", process.stdout + process.stderr)

    def test_export_does_not_overwrite_input(self):
        self.path = Path(self.directory.name) / "results.csv"
        self.write_rows([self.make_row(1)])
        original = self.path.read_bytes()
        process = subprocess.run(
            [sys.executable, str(Path(analyze.__file__)), str(self.path)],
            input="s\n", text=True, capture_output=True, cwd=self.directory.name,
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(self.path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()