from pathlib import Path

import pytest

from summd.__main__ import main


def test_cli_success(project_root: Path, tmp_path: Path, capsys):
    """
    CLIが正常に実行され、ファイルが生成され、成功メッセージが表示されることをテストする。
    """
    output_file = tmp_path / "output.md"

    # sys.argvを模倣したリストを作成
    argv = ["code2md", str(project_root), str(output_file)]

    # main関数を呼び出し (スクリプト名argv[0]は渡さない)
    main(argv[1:])

    # 標準出力に成功メッセージが含まれているか確認
    captured = capsys.readouterr()
    assert "🎉 やったね！" in captured.out
    assert str(output_file.resolve()) in captured.out

    # ファイルが正しく生成されているか確認
    assert output_file.is_file()
    content = output_file.read_text("utf-8")
    assert "# test_project" in content
    assert "## ./main.py" in content


def test_cli_with_ignore_option(project_root: Path, tmp_path: Path):
    """
    -i/--ignore オプションが正しく機能することをテストする。
    """
    output_file = tmp_path / "output.md"
    argv = [
        "code2md",
        str(project_root),
        str(output_file),
        "--ignore",
        ".py",
        ".md",
    ]

    main(argv[1:])

    # 生成されたファイルの内容を確認
    content = output_file.read_text("utf-8")
    assert "## ./main.py" not in content
    assert "## ./README.md" not in content
    assert "## ./src/utils.js" in content  # これは無視されていない


def test_cli_missing_arguments(capsys):
    """
    引数が不足している場合に、argparseがエラーを出し、SystemExitが発生することをテストする。
    """
    with pytest.raises(SystemExit) as e:
        main([])  # 引数なしで呼び出し

    # argparseのエラーは終了コード2を返す
    assert e.value.code == 2

    # 標準エラー出力にヘルプメッセージが含まれているか確認
    captured = capsys.readouterr()
    assert "the following arguments are required" in captured.err
