from wllbe.cli import main


def test_main_prints_usage_for_no_args(capsys):
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "wllbe <command>" in captured.out
