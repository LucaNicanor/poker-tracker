"""Regression tests for Astra capture ingestion and failure-safe persistence."""

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gpt_poker_analyst as analyst


def response():
    """Return a minimal valid structured response."""
    return {
        "players": [
            {
                "name": "Player",
                "platform": "ClubWPT Gold",
                "table_id": "A",
                "is_hero": False,
                "typical_stack_bb": 100,
                "archetype": "Unknown",
                "tendencies": [],
                "observed_actions": ["Raises to 3 BB"],
                "astra_exploit": "Use baseline ranges; evidence limited.",
            }
        ],
        "hero_analysis": "No Hero decision visible.",
        "limitations": [],
    }


class AnalystTests(unittest.TestCase):
    """Exercise validation, identity isolation, caching and bridge errors."""

    def test_invalid_response(self):
        """Reject malformed stacks and missing fields."""
        for stack in (True, -1, float("nan"), "100"):
            data = response()
            data["players"][0]["typical_stack_bb"] = stack
            with self.assertRaises(ValueError):
                analyst.validate_analysis(data)
        with self.assertRaises(ValueError):
            analyst.validate_analysis({})

    def test_merge(self):
        """Keep platform identities separate and repeated evidence unique."""
        profiles = {}
        players = response()["players"]
        analyst.merge_players(profiles, players, "capture")
        analyst.merge_players(profiles, players, "capture")
        self.assertEqual(len(profiles["Player"]["observed_actions"]), 1)
        self.assertEqual(profiles["Player"]["sources"], ["capture"])
        other = copy.deepcopy(players)
        other[0]["platform"] = "PokerNow"
        analyst.merge_players(profiles, other, "other")
        self.assertEqual(len(profiles), 2)

    def test_capture_batches(self):
        """Include every exported hand exactly once across bounded batches."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            capture = root / "hands.json"
            capture.write_text(json.dumps({"hands": list(range(43)), "gameId": "a"}))
            with patch.object(analyst, "RAW_DIR", root):
                units = list(analyst.capture_units([capture]))
            self.assertEqual(len(units), 3)
            self.assertEqual(
                [h for _, _, data in units for h in json.loads(data)["hands"]],
                list(range(43)),
            )

    def test_cache_and_failure(self):
        """Reuse successful extraction and preserve the report on bridge failure."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            capture = root / "table.png"
            capture.write_bytes(b"mock image")
            report = root / "report.md"
            with (
                patch.object(analyst, "RAW_DIR", root),
                patch.object(analyst, "PROCESSED_DIR", root),
                patch.object(analyst, "REPORT_MD", report),
                patch.object(analyst, "query_astra", return_value=response()) as query,
            ):
                telemetry = {
                    "captures": [capture],
                    "hero_profile": {},
                    "opponents_identified": {},
                }
                analyst.run_gpt_astra_analysis(telemetry)
                self.assertEqual(query.call_count, 2)
                analyst.run_gpt_astra_analysis(telemetry)
                self.assertEqual(query.call_count, 3)
                original = report.read_bytes()
                query.side_effect = RuntimeError("Unavailable")
                with self.assertRaises(RuntimeError):
                    analyst.run_gpt_astra_analysis(telemetry)
                self.assertEqual(report.read_bytes(), original)

    def test_bridge(self):
        """Pass images and exact model to Codex and reject unsuccessful processes."""

        def run(command, **kwargs):
            self.assertIn("gpt-6-astra", command)
            self.assertIn("--image", command)
            self.assertEqual(command[-1], "-")
            self.assertIn("input", kwargs)
            output = Path(command[command.index("--output-last-message") + 1])
            output.write_text(json.dumps(response()), encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, "", "")

        with (
            patch.object(analyst, "find_codex", return_value="codex.exe"),
            patch.object(analyst.subprocess, "run", side_effect=run),
        ):
            self.assertEqual(
                analyst.query_astra("test", [Path("table.png")]), response()
            )
        with (
            patch.object(analyst, "find_codex", return_value="codex.exe"),
            patch.object(
                analyst.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 1, "", "no access"),
            ),
            self.assertRaises(RuntimeError),
        ):
            analyst.query_astra("test", [])

    def test_corrupt_store(self):
        """Never replace a corrupt database with an empty default."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "opponents.json"
            path.write_text("{broken")
            with self.assertRaises(json.JSONDecodeError):
                analyst.read_json(path, {})
            self.assertEqual(path.read_text(), "{broken")


if __name__ == "__main__":
    unittest.main()
