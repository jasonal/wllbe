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
    project.mkdir(parents=True, exist_ok=True)
    (project / "chapter-outline.generated.json").write_text("{}", encoding="utf-8")
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
    project.mkdir(parents=True, exist_ok=True)
    (project / "page-outline.generated.json").write_text("{}", encoding="utf-8")
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


def test_approve_chapters_reports_missing_generated_artifact(tmp_path: Path, capsys) -> None:
    project = tmp_path / "runs" / "demo"
    project.mkdir(parents=True, exist_ok=True)
    input_path = tmp_path / "edited-chapters.json"
    input_path.write_text('{"chapters":[{"title":"Approved"}]}', encoding="utf-8")

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

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "generated artifact" in captured.err


def test_approve_chapters_reports_missing_project_without_creating_it(
    tmp_path: Path,
    capsys,
) -> None:
    project = tmp_path / "runs" / "demo"
    input_path = tmp_path / "edited-chapters.json"
    input_path.write_text('{"chapters":[{"title":"Approved"}]}', encoding="utf-8")

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

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "generated artifact" in captured.err
    assert not project.exists()


def test_approve_chapters_reports_missing_input(tmp_path: Path, capsys) -> None:
    project = tmp_path / "runs" / "demo"
    project.mkdir(parents=True, exist_ok=True)
    (project / "chapter-outline.generated.json").write_text("{}", encoding="utf-8")
    missing_input = tmp_path / "missing-input.json"

    exit_code = main(
        [
            "approve",
            "chapters",
            "--project",
            str(project),
            "--input",
            str(missing_input),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "missing-input" in captured.err


def test_approve_chapters_reports_directory_input(tmp_path: Path, capsys) -> None:
    project = tmp_path / "runs" / "demo"
    project.mkdir(parents=True, exist_ok=True)
    (project / "chapter-outline.generated.json").write_text("{}", encoding="utf-8")
    input_dir = tmp_path / "edited-dir"
    input_dir.mkdir()

    exit_code = main(
        [
            "approve",
            "chapters",
            "--project",
            str(project),
            "--input",
            str(input_dir),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "edited-dir" in captured.err


def test_approve_rejects_unknown_target(capsys) -> None:
    exit_code = main(["approve", "sections"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "unknown approve target: sections" in captured.out
