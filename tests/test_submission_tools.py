from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class SubmissionToolingTests(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def create_scaffold(self, tmpdir: str, slug: str, summary: str) -> Path:
        create = self.run_cmd(
            "python3",
            "scripts/init_submission.py",
            "--base-dir",
            f"{tmpdir}/records",
            "--track",
            "track_non_record_16mb",
            "--slug",
            slug,
            "--author-name",
            "Facundo",
            "--github-id",
            "facundo",
            "--summary",
            summary,
        )
        self.assertEqual(create.returncode, 0, create.stderr)
        return Path(create.stdout.strip())

    def make_completed_submission(self, submission_dir: Path, *, val_loss: float, val_bpb: float) -> None:
        (submission_dir / "README.md").write_text(
            "# Completed submission\n\n## Summary\n\nPrueba seria\n\n## Motivation\n\nTexto final.\n\n## Reproduction\n\n```bash\npython train_gpt.py\n```\n\n## Notes\n\nSin placeholders.\n",
            encoding="utf-8",
        )
        (submission_dir / "train.log").write_text(
            f"step=1 val_loss={val_loss + 0.1:.2f}\nstep=2 val_loss={val_loss:.2f} val_bpb={val_bpb:.2f} artifact_size_bytes=12345678 num_runs=3\n",
            encoding="utf-8",
        )
        (submission_dir / "train_gpt.py").write_text("print('ok')\n", encoding="utf-8")

    def test_generated_scaffold_passes_draft_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            submission_dir = self.create_scaffold(tmpdir, "Primer intento", "Prueba inicial")

            validate = self.run_cmd(
                "python3",
                "scripts/validate_submission.py",
                str(submission_dir),
                "--mode",
                "draft",
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)
            self.assertIn("[PASS]", validate.stdout)
            self.assertIn("WARNING:", validate.stdout)

    def test_update_metrics_from_log_and_validate_submission(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            submission_dir = self.create_scaffold(tmpdir, "Intento serio", "Prueba seria")
            self.make_completed_submission(submission_dir, val_loss=1.23, val_bpb=0.98)

            update = self.run_cmd(
                "python3",
                "scripts/update_submission_metrics.py",
                str(submission_dir),
            )
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            self.assertIn("val_loss=1.23", update.stdout)
            self.assertIn("val_bpb=0.98", update.stdout)

            payload = json.loads((submission_dir / "submission.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["metrics"]["val_loss"], 1.23)
            self.assertEqual(payload["metrics"]["val_bpb"], 0.98)
            self.assertEqual(payload["metrics"]["artifact_size_bytes"], 12345678)
            self.assertEqual(payload["metrics"]["num_runs"], 3)

            validate = self.run_cmd(
                "python3",
                "scripts/validate_submission.py",
                str(submission_dir),
                "--mode",
                "submission",
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)
            self.assertIn("[PASS]", validate.stdout)
            self.assertNotIn("ERROR:", validate.stdout)

    def test_export_submission_to_upstream_records_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            submission_dir = self.create_scaffold(tmpdir, "Exportable", "Prueba exportable")
            self.make_completed_submission(submission_dir, val_loss=1.23, val_bpb=0.98)
            update = self.run_cmd(
                "python3",
                "scripts/update_submission_metrics.py",
                str(submission_dir),
            )
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)

            upstream_repo = Path(tmpdir) / "upstream"
            (upstream_repo / "records" / "track_non_record_16mb").mkdir(parents=True)

            export = self.run_cmd(
                "python3",
                "scripts/export_submission.py",
                str(submission_dir),
                str(upstream_repo),
            )
            self.assertEqual(export.returncode, 0, export.stdout + export.stderr)
            exported_dir = Path(export.stdout.strip())
            self.assertTrue(exported_dir.exists())
            self.assertTrue((exported_dir / "README.md").exists())
            self.assertTrue((exported_dir / "submission.json").exists())
            exported_payload = json.loads((exported_dir / "submission.json").read_text(encoding="utf-8"))
            self.assertEqual(exported_payload["metrics"]["num_runs"], 3)

    def test_report_submissions_sorts_rows_by_metric(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            first = self.create_scaffold(tmpdir, "Run A", "Primera")
            second = self.create_scaffold(tmpdir, "Run B", "Segunda")
            self.make_completed_submission(first, val_loss=1.30, val_bpb=1.05)
            self.make_completed_submission(second, val_loss=1.10, val_bpb=0.91)

            self.run_cmd("python3", "scripts/update_submission_metrics.py", str(first))
            self.run_cmd("python3", "scripts/update_submission_metrics.py", str(second))

            report = self.run_cmd(
                "python3",
                "scripts/report_submissions.py",
                "--base-dir",
                f"{tmpdir}/records",
                "--sort-by",
                "val_bpb",
                "--format",
                "json",
            )
            self.assertEqual(report.returncode, 0, report.stdout + report.stderr)
            rows = json.loads(report.stdout)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["val_bpb"], 0.91)
            self.assertEqual(rows[1]["val_bpb"], 1.05)

    def test_run_submission_creates_scaffold_and_captures_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            train_script = Path(tmpdir) / "train_gpt.py"
            train_script.write_text("print('training script')\n", encoding="utf-8")

            run = self.run_cmd(
                "python3",
                "scripts/run_submission.py",
                "--track",
                "track_non_record_16mb",
                "--slug",
                "Smoke Runner",
                "--author-name",
                "Facundo",
                "--github-id",
                "facundo",
                "--summary",
                "Smoke test runner",
                "--base-dir",
                f"{tmpdir}/records",
                "--train-script",
                str(train_script),
                "--",
                "python3",
                "-c",
                "from pathlib import Path; import os; Path(os.environ['SUBMISSION_DIR'], 'child_marker.txt').write_text('ok', encoding='utf-8'); print('val_loss=1.23 val_bpb=0.98 artifact_size_bytes=12345678 num_runs=1')",
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            submission_dir = Path(run.stdout.strip().splitlines()[-1])
            self.assertTrue((submission_dir / "train.log").exists())
            self.assertTrue((submission_dir / 'child_marker.txt').exists())
            self.assertIn("val_loss=1.23", (submission_dir / "train.log").read_text(encoding="utf-8"))
            payload = json.loads((submission_dir / "submission.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["metrics"]["val_bpb"], 0.98)
            self.assertIn("python3 -c", (submission_dir / "README.md").read_text(encoding="utf-8"))
            self.assertEqual((submission_dir / "train_gpt.py").read_text(encoding="utf-8"), "print('training script')\n")

    def test_run_campaign_uses_preset_and_upstream_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            upstream_repo = Path(tmpdir) / "upstream"
            upstream_repo.mkdir(parents=True)
            (upstream_repo / "train_gpt.py").write_text("print('fake train script')\n", encoding="utf-8")

            campaign = Path(tmpdir) / "campaign.env"
            campaign.write_text(
                "COMMAND=python3 -c \"print('val_loss=1.11 val_bpb=0.88 artifact_size_bytes=111 num_runs=1')\"\nRUN_ID=test_campaign\n",
                encoding="utf-8",
            )

            run = self.run_cmd(
                "python3",
                "scripts/run_campaign.py",
                "--campaign",
                str(campaign),
                "--upstream-repo",
                str(upstream_repo),
                "--slug",
                "campaign-smoke",
                "--author-name",
                "Facundo",
                "--github-id",
                "facundo",
                "--summary",
                "Campaign smoke",
                "--base-dir",
                f"{tmpdir}/records",
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            submission_dir = Path(run.stdout.strip().splitlines()[-1])
            payload = json.loads((submission_dir / "submission.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["metrics"]["val_bpb"], 0.88)
            self.assertEqual((submission_dir / "train_gpt.py").read_text(encoding="utf-8"), "print('fake train script')\n")
            self.assertIn("env RUN_ID=test_campaign", (submission_dir / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
