import logging
import sys
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
    if line.strip().startswith("#"):
        stripped_line = line.lstrip()
        content = stripped_line.lstrip("#")
        level = len(stripped_line) - len(content)

        # H1 -> H3, H2 -> H4 のようにレベルを2つ下げる
        # Markdownの最大見出しレベルはH6なので、それを超えないようにする
        new_level = min(level + 2, 6)
        return "#" * new_level + content
    return line


def _process_ipynb_file(file_path: Path) -> str:
    """Jupyter Notebook (.ipynb) ファイルを処理してMarkdown形式の文字列を返す"""
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
    # デフォルトの無視パターンを基本にする
    patterns = list(DEFAULT_IGNORE_PATTERNS)

    gitignore_path = root_path / ".gitignore"
    if gitignore_path.is_file():
        with gitignore_path.open("r", encoding="utf-8") as f:
            # コメントや空行を除外して追加
            patterns.extend(
                line
                for line in f.read().splitlines()
                if line.strip() and not line.strip().startswith("#")
            )
    spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return spec


def find_target_files(root_path: Path, ignored_extensions: Set[str]) -> List[Path]:
    """対象となるコーディングファイルを探す (.gitignoreとデフォルトパターンを考慮)"""
    target_files = []

    # .gitignoreの読み込み
    gitignore_spec = _load_gitignore(root_path)

    for p in root_path.rglob("*"):
        # パスを文字列に変換して.gitignoreの判定に使う
        relative_path_str = str(p.relative_to(root_path))

        # .gitignoreとデフォルトの無視パターンにマッチするかチェック
        if gitignore_spec.match_file(relative_path_str):
            continue

        if p.is_file():
            # 除外指定された拡張子をスキップ
            if p.suffix.lower() in ignored_extensions:
                continue

            if p.suffix.lower() in TARGET_EXTENSIONS or p.name in TARGET_EXTENSIONS:
                target_files.append(p)

    return sorted(target_files)


def _read_file_content(file_path: Path) -> str:
    """ファイルを読み込み、処理してMarkdownチャンクを返す"""
    if file_path.suffix.lower() == ".ipynb":
        return _process_ipynb_file(file_path)

    try:
        lang = _get_language(file_path)
        content = file_path.read_text(encoding="utf-8")
        return f"```{lang}\n{content}\n```"
    except UnicodeDecodeError:
        logging.warning(
            f"⚠️  Could not decode file {file_path} as UTF-8. Skipping content."
        )
        return "```\n[ERROR] Could not read file content due to encoding issues.\n```"
    except Exception as e:
        logging.warning(f"⚠️  Failed to process file {file_path}: {e}")
        return f"```\n[ERROR] Could not read file content: {e}\n```"


def generate_markdown(
    root_path: Path, output_path: Path, ignored_extensions: List[str]
) -> None:
    """指定されたディレクトリのファイルを1つのMarkdownファイルにまとめる"""
    # ロガーの設定
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    logger = logging.getLogger(__name__)

    # 無視する拡張子をセットに変換 (高速化のため)
    ignored_ext_set = {f".{ext.lstrip('.')}".lower() for ext in ignored_extensions}

    if not root_path.is_dir():
        logger.error(
            f"😱 エラー: 指定されたルートパスが見つからないよ！ -> {root_path}"
        )
        return

    logger.info(f"🔍 ファイルを探してるよ... (from: {root_path})")
    target_files = find_target_files(root_path, ignored_ext_set)

    if not target_files:
        logger.info("🤷‍♂️ 対象ファイルが見つからなかったよ。")
        return

    logger.info(
        f"✨ {len(target_files)}個のファイルが見つかった！Markdownを生成するよ！"
    )

    md_content = [f"# {root_path.absolute().name}\n"]

    for file_path in target_files:
        relative_path = file_path.relative_to(root_path)
        md_content.append(f"## ./{relative_path}\n")
        content = _read_file_content(file_path)
        md_content.append(f"{content}\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(md_content), encoding="utf-8")
    print(f"🎉 やったね！Markdownファイルを出力したよ！ -> {output_path.resolve()}")
