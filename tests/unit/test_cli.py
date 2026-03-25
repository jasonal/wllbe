import subprocess
import sys
from pathlib import Path

from wllbe.cli import main


def test_main_prints_usage_for_no_args(capsys):
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "wllbe <command>" in captured.out


def test_main_handles_unknown_command(capsys):
    exit_code = main(["demo"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "unknown command: demo" in captured.out


def test_run_module_invokes_main():
    result = subprocess.run(
        [sys.executable, "-m", "wllbe.cli", "demo"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "unknown command: demo" in result.stdout


def test_approve_chapters_command_copies_input_json(tmp_path: Path):
    project = tmp_path / "runs" / "demo"
    input_path = tmp_path / "edited-chapters.json"
    input_path.write_text('{"chapters":[{"title":"Approved Chapter"}]}', encoding="utf-8")

    exit_code = main(
        [
            "approve",
            "chapters",
            "--project",
            str(project),
            "--input",
            str(input_path),
        ]
    )

    assert exit_code == 0
    approved_path = project / "chapter-outline.approved.json"
    assert approved_path.read_text(encoding="utf-8") == input_path.read_text(encoding="utf-8")


def test_approve_pages_command_copies_input_json(tmp_path: Path):
    project = tmp_path / "runs" / "demo"
    input_path = tmp_path / "edited-pages.json"
    input_path.write_text('{"pages":[{"title":"Approved Page"}]}', encoding="utf-8")

    exit_code = main(
        [
            "approve",
            "pages",
            "--project",
            str(project),
            "--input",
            str(input_path),
        ]
    )

    assert exit_code == 0
    approved_path = project / "page-outline.approved.json"
    assert approved_path.read_text(encoding="utf-8") == input_path.read_text(encoding="utf-8")
