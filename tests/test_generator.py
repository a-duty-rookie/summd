import json
from pathlib import Path

import pytest

from summd.generator import find_target_files, generate_markdown


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """
    テスト用の仮想的なプロジェクトディレクトリ構造を作成するpytestフィクスチャ。
    tmp_path: pytestが提供する一時ディレクトリのパス。
    """
    root = tmp_path / "test_project"
    root.mkdir()

    # 1. 収集されるべきファイル
    (root / "main.py").write_text("print('hello world')")
    (root / "README.md").write_text("# Project Title")
    (root / "src").mkdir()
    (root / "src" / "utils.js").write_text("const x = 1;")

    # 2. .gitignoreで無視されるべきファイル
    (root / ".gitignore").write_text("*.log\n/secrets/")
    (root / "app.log").write_text("log entry")
    (root / "secrets").mkdir()
    (root / "secrets" / "api.key").write_text("secret-key")

    # 3. デフォルトで無視されるべきディレクトリ
    (root / "node_modules").mkdir()
    (root / "node_modules" / "lib.js").write_text("var y = 2;")

    # 4. Jupyter Notebookファイル
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Analysis Header"],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["import pandas as pd"],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }
    (root / "notebooks").mkdir()
    (root / "notebooks" / "analysis.ipynb").write_text(json.dumps(notebook_content))
    return root


def test_find_target_files(project_root: Path):
    """
    find_target_filesが、.gitignoreやデフォルトの無視パターンを考慮し、
    正しくファイルを探索できることをテストする。
    """
    target_files = find_target_files(project_root, ignored_extensions=set())
    relative_paths = {str(p.relative_to(project_root)) for p in target_files}

    expected = {
        "main.py",
        "README.md",
        "src/utils.js",
        "notebooks/analysis.ipynb",
    }
    assert relative_paths == expected


def test_find_target_files_with_ignored_extensions(project_root: Path):
    """-i オプションで指定された拡張子が正しく無視されることをテストする。"""
    target_files = find_target_files(project_root, ignored_extensions={".md", ".js"})
    relative_paths = {str(p.relative_to(project_root)) for p in target_files}

    expected = {"main.py", "notebooks/analysis.ipynb"}
    assert relative_paths == expected


def test_generate_markdown_integration(project_root: Path, tmp_path: Path):
    """generate_markdownの統合テスト。ファイル生成と内容の検証を行う。"""
    output_path = tmp_path / "output.md"

    generate_markdown(project_root, output_path, ignored_extensions=[])

    assert output_path.is_file()
    content = output_path.read_text("utf-8")

    # 必須のファイルコンテンツが含まれているか
    assert "## ./main.py" in content
    assert "print('hello world')" in content
    assert "## ./notebooks/analysis.ipynb" in content
    assert "### Analysis Header" in content  # H1がH3に変換されているか

    # 無視されたファイルコンテンツが含まれていないか
    assert "app.log" not in content
    assert "secret-key" not in content
    assert "node_modules" not in content
