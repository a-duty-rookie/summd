# code2md

## ./README.md

```markdown

```

## ./pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "code2md"
version = "0.1.0"
authors = [{ name = "a-duty-rookie", email = "yutaro1127@gmail.com" }]
description = "A CLI tool to bundle coding files into a single Markdown file."
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
# 👇 依存関係を追加！
dependencies = [
    "nbformat",
    "pathspec", # .gitignoreを解釈するために追加！
]

[project.scripts]
code2md = "code2md.__main__:main"

```

## ./src/code2md/__init__.py

```python

```

## ./src/code2md/__main__.py

```python
import argparse

from code2md.generator import generate_markdown


def main():
    parser = argparse.ArgumentParser(
        description="指定したディレクトリのコーディングファイルを1つのMarkdownファイルにまとめます。"
    )
    parser.add_argument("root_path", help="ファイル収集の起点となるディレクトリのパス")
    parser.add_argument(
        "output_path", help="出力するMarkdownファイルのパス (例: output/summary.md)"
    )
    # 👇 除外オプションを追加！
    parser.add_argument(
        "-i",
        "--ignore",
        nargs="+",  # 複数の値をリストとして受け取る
        default=[],
        help="無視するファイルの拡張子をスペース区切りで指定 (例: .log .tmp)",
    )

    args = parser.parse_args()

    generate_markdown(args.root_path, args.output_path, args.ignore)


if __name__ == "__main__":
    main()

```

## ./src/code2md/generator.py

```python
from pathlib import Path
from typing import Dict, List, Set

import nbformat
import pathspec  # .gitignoreのため

# 収集するファイルの拡張子リスト
TARGET_EXTENSIONS = {
    ".py",
    ".sql",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".scss",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    "Dockerfile",
    ".env.example",
    ".ipynb",
}

# デフォルトの無視パターン
DEFAULT_IGNORE_PATTERNS = {
    "__pycache__",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "dist",
    "build",
    ".DS_Store",
}

# 拡張子とMarkdownの言語指定子のマッピング
LANG_MAP: Dict[str, str] = {
    ".py": "python",
    ".sql": "sql",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".sh": "bash",
    "dockerfile": "dockerfile",
    ".ipynb": "python",  # ipynbのコードセルはpythonとして扱う
}


def _get_language(file_path: Path) -> str:
    """ファイルパスの拡張子から言語名を取得する"""
    if file_path.name.lower() == "dockerfile":
        return LANG_MAP.get("dockerfile", "")
    return LANG_MAP.get(file_path.suffix.lower(), "")


def _adjust_markdown_header(line: str) -> str:
    """Markdownの見出しレベルを調整する (最大H3)"""
    if line.startswith("#"):
        level = line.count("#")
        # H1 -> H3, H2 -> H3, H3 -> H3...
        new_level = min(level + 2, 3)
        return "#" * new_level + " " + line.lstrip("# ").strip()
    return line


def _process_ipynb_file(file_path: Path) -> str:
    """Jupyter Notebook (.ipynb) ファイルを処理してMarkdown形式の文字列を返す"""
    if not nbformat:
        return (
            "```\n[ERROR] `nbformat` is not installed. "
            "Please run `pip install nbformat` to process .ipynb files.\n```"
        )

    try:
        with file_path.open("r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        md_parts = []
        for cell in nb.cells:
            if cell.cell_type == "markdown":
                # Markdownセルの見出しを調整
                adjusted_source = "\n".join(
                    _adjust_markdown_header(line) for line in cell.source.splitlines()
                )
                md_parts.append(adjusted_source)
            elif cell.cell_type == "code":
                # コードセルをコードブロックに
                lang = LANG_MAP.get(".py", "python")  # デフォルトはpython
                md_parts.append(f"```{lang}\n{cell.source}\n```")

        return "\n\n".join(md_parts)

    except Exception as e:
        return f"```\n[ERROR] Could not process .ipynb file: {e}\n```"


def _load_gitignore(root_path: Path) -> pathspec.PathSpec:
    """ルートディレクトリの.gitignoreを読み込む"""
    gitignore_path = root_path / ".gitignore"
    patterns = []
    if gitignore_path.is_file():
        with gitignore_path.open("r", encoding="utf-8") as f:
            patterns = f.read().splitlines()
    spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return spec


def find_target_files(root_path: Path, ignored_extensions: Set[str]) -> List[Path]:
    """対象となるコーディングファイルを探す (.gitignoreも考慮)"""
    target_files = []

    # .gitignoreの読み込み
    gitignore_spec = _load_gitignore(root_path)

    # 無視パターンの結合
    ignore_patterns = DEFAULT_IGNORE_PATTERNS

    for p in root_path.rglob("*"):
        # パスを文字列に変換して.gitignoreの判定に使う
        relative_path_str = str(p.relative_to(root_path))

        # .gitignoreのルールにマッチするかチェック
        if gitignore_spec.match_file(relative_path_str):
            continue

        if any(ignore in p.parts for ignore in ignore_patterns):
            continue

        if p.is_file():
            # 除外指定された拡張子をスキップ
            if p.suffix.lower() in ignored_extensions:
                continue

            if p.suffix.lower() in TARGET_EXTENSIONS or p.name in TARGET_EXTENSIONS:
                target_files.append(p)

    return sorted(target_files)


def generate_markdown(
    root_path_str: str, output_path_str: str, ignored_extensions: List[str]
) -> None:
    """指定されたディレクトリのファイルを1つのMarkdownファイルにまとめる"""
    root_path = Path(root_path_str).resolve()
    output_path = Path(output_path_str)

    # 無視する拡張子をセットに変換 (高速化のため)
    ignored_ext_set = {f".{ext.lstrip('.')}".lower() for ext in ignored_extensions}

    if not root_path.is_dir():
        print(f"😱 エラー: 指定されたルートパスが見つからないよ！ -> {root_path}")
        return

    print(f"🔍 ファイルを探してるよ... (from: {root_path})")
    target_files = find_target_files(root_path, ignored_ext_set)

    if not target_files:
        print("🤷‍♂️ 対象ファイルが見つからなかったよ。")
        return

    print(f"✨ {len(target_files)}個のファイルが見つかった！Markdownを生成するよ！")

    md_content = [f"# {root_path.name}\n"]

    for file_path in target_files:
        relative_path = file_path.relative_to(root_path)

        try:
            md_content.append(f"## ./{relative_path}\n")  # パスを./から始めるように

            # ipynbファイルの場合の特別処理
            if file_path.suffix.lower() == ".ipynb":
                content = _process_ipynb_file(file_path)
                md_content.append(f"{content}\n")
            else:
                lang = _get_language(file_path)
                content = file_path.read_text(encoding="utf-8")
                md_content.append(f"```{lang}\n{content}\n```\n")

        except Exception as e:
            print(f"⚠️ ファイルの処理に失敗したよ: {file_path} ({e})")
            md_content.append(f"## ./{relative_path}\n")
            md_content.append(f"```\n[ERROR] Could not read file content: {e}\n```\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md_content), encoding="utf-8")
    print(f"🎉 やったね！Markdownファイルを出力したよ！ -> {output_path.resolve()}")
    print(f"🎉 やったね！Markdownファイルを出力したよ！ -> {output_path.resolve()}")

```

## ./test.md

```markdown
# code2md

## ./README.md

```markdown

```

## ./notebooks/test.ipynb

### これはテストです

```python
import pandas as pd
import numpy as np
```

```python
test = str('test')
```

### うまく反映されているかな

- どうだろうか？
- daijoubukana

## ./pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "code2md"
version = "0.1.0"
authors = [{ name = "a-duty-rookie", email = "yutaro1127@gmail.com" }]
description = "A CLI tool to bundle coding files into a single Markdown file."
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
# 👇 依存関係を追加！
dependencies = [
    "nbformat",
    "pathspec", # .gitignoreを解釈するために追加！
]

[project.scripts]
code2md = "code2md.__main__:main"

```

## ./src/code2md/__init__.py

```python

```

## ./src/code2md/__main__.py

```python
import argparse

from code2md.generator import generate_markdown


def main():
    parser = argparse.ArgumentParser(
        description="指定したディレクトリのコーディングファイルを1つのMarkdownファイルにまとめます。"
    )
    parser.add_argument("root_path", help="ファイル収集の起点となるディレクトリのパス")
    parser.add_argument(
        "output_path", help="出力するMarkdownファイルのパス (例: output/summary.md)"
    )
    # 👇 除外オプションを追加！
    parser.add_argument(
        "-i",
        "--ignore",
        nargs="+",  # 複数の値をリストとして受け取る
        default=[],
        help="無視するファイルの拡張子をスペース区切りで指定 (例: .log .tmp)",
    )

    args = parser.parse_args()

    generate_markdown(args.root_path, args.output_path, args.ignore)


if __name__ == "__main__":
    main()

```

## ./src/code2md/generator.py

```python
# import json
# import os
from pathlib import Path
from typing import Dict, List, Set

import pathspec  # .gitignoreのため

# nbformatをインポート
try:
    import nbformat

    # from nbformat.v4 import NotebookNode, new_code_cell, new_markdown_cell
except ImportError:
    nbformat = None  # インポート失敗してもエラーにしない

# 収集するファイルの拡張子リスト
TARGET_EXTENSIONS = {
    ".py",
    ".sql",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".scss",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    "Dockerfile",
    ".env.example",
    ".ipynb",
}

# デフォルトの無視パターン
DEFAULT_IGNORE_PATTERNS = {
    "__pycache__",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "dist",
    "build",
    ".DS_Store",
}

# 拡張子とMarkdownの言語指定子のマッピング
LANG_MAP: Dict[str, str] = {
    ".py": "python",
    ".sql": "sql",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".sh": "bash",
    "dockerfile": "dockerfile",
    ".ipynb": "python",  # ipynbのコードセルはpythonとして扱う
}


def _get_language(file_path: Path) -> str:
    """ファイルパスの拡張子から言語名を取得する"""
    if file_path.name.lower() == "dockerfile":
        return LANG_MAP.get("dockerfile", "")
    return LANG_MAP.get(file_path.suffix.lower(), "")


def _adjust_markdown_header(line: str) -> str:
    """Markdownの見出しレベルを調整する (最大H3)"""
    if line.startswith("#"):
        level = line.count("#")
        # H1 -> H3, H2 -> H3, H3 -> H3...
        new_level = min(level + 2, 3)
        return "#" * new_level + " " + line.lstrip("# ").strip()
    return line


def _process_ipynb_file(file_path: Path) -> str:
    """Jupyter Notebook (.ipynb) ファイルを処理してMarkdown形式の文字列を返す"""
    if not nbformat:
        return (
            "```\n[ERROR] `nbformat` is not installed. "
            "Please run `pip install nbformat` to process .ipynb files.\n```"
        )

    try:
        with file_path.open("r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        md_parts = []
        for cell in nb.cells:
            if cell.cell_type == "markdown":
                # Markdownセルの見出しを調整
                adjusted_source = "\n".join(
                    _adjust_markdown_header(line) for line in cell.source.splitlines()
                )
                md_parts.append(adjusted_source)
            elif cell.cell_type == "code":
                # コードセルをコードブロックに
                lang = LANG_MAP.get(".py", "python")  # デフォルトはpython
                md_parts.append(f"```{lang}\n{cell.source}\n```")

        return "\n\n".join(md_parts)

    except Exception as e:
        return f"```\n[ERROR] Could not process .ipynb file: {e}\n```"


def _load_gitignore(root_path: Path) -> pathspec.PathSpec:
    """ルートディレクトリの.gitignoreを読み込む"""
    gitignore_path = root_path / ".gitignore"
    patterns = []
    if gitignore_path.is_file():
        with gitignore_path.open("r", encoding="utf-8") as f:
            patterns = f.read().splitlines()
    spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return spec


def find_target_files(root_path: Path, ignored_extensions: Set[str]) -> List[Path]:
    """対象となるコーディングファイルを探す (.gitignoreも考慮)"""
    target_files = []

    # .gitignoreの読み込み
    gitignore_spec = _load_gitignore(root_path)

    # 無視パターンの結合
    ignore_patterns = DEFAULT_IGNORE_PATTERNS

    for p in root_path.rglob("*"):
        # パスを文字列に変換して.gitignoreの判定に使う
        relative_path_str = str(p.relative_to(root_path))

        # .gitignoreのルールにマッチするかチェック
        if gitignore_spec.match_file(relative_path_str):
            continue

        if any(ignore in p.parts for ignore in ignore_patterns):
            continue

        if p.is_file():
            # 除外指定された拡張子をスキップ
            if p.suffix.lower() in ignored_extensions:
                continue

            if p.suffix.lower() in TARGET_EXTENSIONS or p.name in TARGET_EXTENSIONS:
                target_files.append(p)

    return sorted(target_files)


def generate_markdown(
    root_path_str: str, output_path_str: str, ignored_extensions: List[str]
) -> None:
    """指定されたディレクトリのファイルを1つのMarkdownファイルにまとめる"""
    root_path = Path(root_path_str).resolve()
    output_path = Path(output_path_str)

    # 無視する拡張子をセットに変換 (高速化のため)
    ignored_ext_set = {f".{ext.lstrip('.')}".lower() for ext in ignored_extensions}

    if not root_path.is_dir():
        print(f"😱 エラー: 指定されたルートパスが見つからないよ！ -> {root_path}")
        return

    print(f"🔍 ファイルを探してるよ... (from: {root_path})")
    target_files = find_target_files(root_path, ignored_ext_set)

    if not target_files:
        print("🤷‍♂️ 対象ファイルが見つからなかったよ。")
        return

    print(f"✨ {len(target_files)}個のファイルが見つかった！Markdownを生成するよ！")

    md_content = [f"# {root_path.name}\n"]

    for file_path in target_files:
        relative_path = file_path.relative_to(root_path)

        try:
            md_content.append(f"## ./{relative_path}\n")  # パスを./から始めるように

            # ipynbファイルの場合の特別処理
            if file_path.suffix.lower() == ".ipynb":
                content = _process_ipynb_file(file_path)
                md_content.append(f"{content}\n")
            else:
                lang = _get_language(file_path)
                content = file_path.read_text(encoding="utf-8")
                md_content.append(f"```{lang}\n{content}\n```\n")

        except Exception as e:
            print(f"⚠️ ファイルの処理に失敗したよ: {file_path} ({e})")
            md_content.append(f"## ./{relative_path}\n")
            md_content.append(f"```\n[ERROR] Could not read file content: {e}\n```\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md_content), encoding="utf-8")
    print(f"🎉 やったね！Markdownファイルを出力したよ！ -> {output_path.resolve()}")
    print(f"🎉 やったね！Markdownファイルを出力したよ！ -> {output_path.resolve()}")

```

## ./test.md

```markdown
# code2md

## ./README.md

```markdown

```

## ./pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "code2md"
version = "0.1.0"
authors = [{ name = "a-duty-rookie", email = "yutaro1127@gmail.com" }]
description = "A CLI tool to bundle coding files into a single Markdown file."
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
# 👇 依存関係を追加！
dependencies = [
    "nbformat",
    "pathspec", # .gitignoreを解釈するために追加！
]

[project.scripts]
code2md = "code2md.__main__:main"

```

## ./src/code2md/__init__.py

```python

```

## ./src/code2md/__main__.py

```python
import argparse

from code2md.generator import generate_markdown


def main():
    parser = argparse.ArgumentParser(
        description="指定したディレクトリのコーディングファイルを1つのMarkdownファイルにまとめます。"
    )
    parser.add_argument("root_path", help="ファイル収集の起点となるディレクトリのパス")
    parser.add_argument(
        "output_path", help="出力するMarkdownファイルのパス (例: output/summary.md)"
    )
    # 👇 除外オプションを追加！
    parser.add_argument(
        "-i",
        "--ignore",
        nargs="+",  # 複数の値をリストとして受け取る
        default=[],
        help="無視するファイルの拡張子をスペース区切りで指定 (例: .log .tmp)",
    )

    args = parser.parse_args()

    generate_markdown(args.root_path, args.output_path, args.ignore)


if __name__ == "__main__":
    main()

```

## ./src/code2md/generator.py

```python
# import json
# import os
from pathlib import Path
from typing import Dict, List, Set

import pathspec  # .gitignoreのため

# nbformatをインポート
try:
    import nbformat

    # from nbformat.v4 import NotebookNode, new_code_cell, new_markdown_cell
except ImportError:
    nbformat = None  # インポート失敗してもエラーにしない

# 収集するファイルの拡張子リスト
TARGET_EXTENSIONS = {
    ".py",
    ".sql",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".scss",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    "Dockerfile",
    ".env.example",
    ".ipynb",
}

# デフォルトの無視パターン
DEFAULT_IGNORE_PATTERNS = {
    "__pycache__",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "dist",
    "build",
    ".DS_Store",
}

# 拡張子とMarkdownの言語指定子のマッピング
LANG_MAP: Dict[str, str] = {
    ".py": "python",
    ".sql": "sql",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".sh": "bash",
    "dockerfile": "dockerfile",
    ".ipynb": "python",  # ipynbのコードセルはpythonとして扱う
}


def _get_language(file_path: Path) -> str:
    """ファイルパスの拡張子から言語名を取得する"""
    if file_path.name.lower() == "dockerfile":
        return LANG_MAP.get("dockerfile", "")
    return LANG_MAP.get(file_path.suffix.lower(), "")


def _adjust_markdown_header(line: str) -> str:
    """Markdownの見出しレベルを調整する (最大H3)"""
    if line.startswith("#"):
        level = line.count("#")
        # H1 -> H3, H2 -> H3, H3 -> H3...
        new_level = min(level + 2, 3)
        return "#" * new_level + " " + line.lstrip("# ").strip()
    return line


def _process_ipynb_file(file_path: Path) -> str:
    """Jupyter Notebook (.ipynb) ファイルを処理してMarkdown形式の文字列を返す"""
    if not nbformat:
        return (
            "```\n[ERROR] `nbformat` is not installed. "
            "Please run `pip install nbformat` to process .ipynb files.\n```"
        )

    try:
        with file_path.open("r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        md_parts = []
        for cell in nb.cells:
            if cell.cell_type == "markdown":
                # Markdownセルの見出しを調整
                adjusted_source = "\n".join(
                    _adjust_markdown_header(line) for line in cell.source.splitlines()
                )
                md_parts.append(adjusted_source)
            elif cell.cell_type == "code":
                # コードセルをコードブロックに
                lang = LANG_MAP.get(".py", "python")  # デフォルトはpython
                md_parts.append(f"```{lang}\n{cell.source}\n```")

        return "\n\n".join(md_parts)

    except Exception as e:
        return f"```\n[ERROR] Could not process .ipynb file: {e}\n```"


def _load_gitignore(root_path: Path) -> pathspec.PathSpec:
    """ルートディレクトリの.gitignoreを読み込む"""
    gitignore_path = root_path / ".gitignore"
    patterns = []
    if gitignore_path.is_file():
        with gitignore_path.open("r", encoding="utf-8") as f:
            patterns = f.read().splitlines()
    spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return spec


def find_target_files(root_path: Path, ignored_extensions: Set[str]) -> List[Path]:
    """対象となるコーディングファイルを探す (.gitignoreも考慮)"""
    target_files = []

    # .gitignoreの読み込み
    gitignore_spec = _load_gitignore(root_path)

    # 無視パターンの結合
    ignore_patterns = DEFAULT_IGNORE_PATTERNS

    for p in root_path.rglob("*"):
        # パスを文字列に変換して.gitignoreの判定に使う
        relative_path_str = str(p.relative_to(root_path))

        # .gitignoreのルールにマッチするかチェック
        if gitignore_spec.match_file(relative_path_str):
            continue

        if any(ignore in p.parts for ignore in ignore_patterns):
            continue

        if p.is_file():
            # 除外指定された拡張子をスキップ
            if p.suffix.lower() in ignored_extensions:
                continue

            if p.suffix.lower() in TARGET_EXTENSIONS or p.name in TARGET_EXTENSIONS:
                target_files.append(p)

    return sorted(target_files)


def generate_markdown(
    root_path_str: str, output_path_str: str, ignored_extensions: List[str]
) -> None:
    """指定されたディレクトリのファイルを1つのMarkdownファイルにまとめる"""
    root_path = Path(root_path_str).resolve()
    output_path = Path(output_path_str)

    # 無視する拡張子をセットに変換 (高速化のため)
    ignored_ext_set = {f".{ext.lstrip('.')}".lower() for ext in ignored_extensions}

    if not root_path.is_dir():
        print(f"😱 エラー: 指定されたルートパスが見つからないよ！ -> {root_path}")
        return

    print(f"🔍 ファイルを探してるよ... (from: {root_path})")
    target_files = find_target_files(root_path, ignored_ext_set)

    if not target_files:
        print("🤷‍♂️ 対象ファイルが見つからなかったよ。")
        return

    print(f"✨ {len(target_files)}個のファイルが見つかった！Markdownを生成するよ！")

    md_content = [f"# {root_path.name}\n"]

    for file_path in target_files:
        relative_path = file_path.relative_to(root_path)

        try:
            md_content.append(f"## ./{relative_path}\n")  # パスを./から始めるように

            # ipynbファイルの場合の特別処理
            if file_path.suffix.lower() == ".ipynb":
                content = _process_ipynb_file(file_path)
                md_content.append(f"{content}\n")
            else:
                lang = _get_language(file_path)
                content = file_path.read_text(encoding="utf-8")
                md_content.append(f"```{lang}\n{content}\n```\n")

        except Exception as e:
            print(f"⚠️ ファイルの処理に失敗したよ: {file_path} ({e})")
            md_content.append(f"## ./{relative_path}\n")
            md_content.append(f"```\n[ERROR] Could not read file content: {e}\n```\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md_content), encoding="utf-8")
    print(f"🎉 やったね！Markdownファイルを出力したよ！ -> {output_path.resolve()}")
    print(f"🎉 やったね！Markdownファイルを出力したよ！ -> {output_path.resolve()}")

```

```

```
