import json
from pathlib import Path

import pytest


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
