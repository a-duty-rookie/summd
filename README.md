# summd

**See below for the English version.**

[Source code available on GitHub! 👥](https://github.com/a-duty-rookie/summd)

`summd` は、ディレクトリ内のソースコードや設定ファイルを **1つのMarkdownファイル** にまとめるためのコマンドラインツールです。
プロジェクト全体の構造を俯瞰したり、LLM（大規模言語モデル）へのインプットとして利用するのに最適です。

---

## ✨ 特徴

- **複数ファイルの一括集約**: プロジェクト内のコード・設定ファイルをまとめて1ファイル化。
- **`.gitignore` 対応**: `.gitignore` の内容を自動反映し、不要ファイルを除外。
- **Jupyter Notebook 対応**: `.ipynb` のMarkdownセル・コードセルを抽出して整形。
- **柔軟な除外設定**: デフォルト無視パターン（`node_modules/`, `.venv/`, `__pycache__/`など）に加えて、任意の拡張子やパターンを指定可能。
- **多言語サポート**: Python, JavaScript, HTML, CSS, Dockerfile, YAML など主要言語に対応。

---

## 🚀 インストール

開発中のツールのため、`pipx` でのインストールを推奨します。

```bash
pipx install summd
```

※ `pip install summd` でも利用可能ですが、CLIツールは pipx 管理が便利です。

⸻

## 💡 使い方

基本コマンド：`summd <対象ディレクトリ> <出力ファイルパス>`

例: 現在のディレクトリをまとめる

``` bash
summd . output/summary.md
```

⸻

## ⚙️ オプション

`-i`, `--ignore`

特定の拡張子を持つファイルを除外します。複数指定可能。

例: .log と .tmp を無視

```bash
summd . summary.md --ignore .log .tmp
```

⸻

## 📚 ユースケース

- LLMへのインプット用に、リポジトリを丸ごとMarkdown化
- プロジェクト概要をキャッチアップするためのドキュメント生成
- レビューやアーカイブ用途でのコードスナップショット化

⸻

## 📝 ライセンス

このプロジェクトは MITライセンス の下で公開されています。

---

`summd` is a command-line tool that consolidates source code and configuration files in a directory into **a single Markdown file**.
It’s ideal for getting an overview of an entire project or preparing input for LLMs (Large Language Models).

---

## ✨ Features

- **Aggregate multiple files**: Combine code and config files across a project into one Markdown file.
- **`.gitignore` support**: Automatically respects `.gitignore` rules to exclude unwanted files.
- **Jupyter Notebook support**: Parses `.ipynb` files, extracting and formatting Markdown and code cells.
- **Flexible exclusions**: Skips default patterns (`node_modules/`, `.venv/`, `__pycache__/`, etc.) and lets you specify custom extensions or patterns.
- **Multi-language support**: Handles Python, JavaScript, HTML, CSS, Dockerfile, YAML, and many more.

---

## 🚀 Installation

As this tool is still under development, we recommend installing with `pipx`:

```bash
pipx install summd
```

※ `pip install summd`also works, but pipx is generally better for managing CLI tools.

⸻

## 💡 Usage

Basic command:`summd <target-directory> <output-file>`

Example: consolidate the current directory into output/summary.md

```bash
summd . output/summary.md
```

⸻

## ⚙️ Options

`-i`, `--ignore`

Exclude files with specific extensions. Multiple extensions can be specified.

Example: ignore .log and .tmp files:

```bash
summd . summary.md --ignore .log .tmp
```

⸻

## 📚 Use Cases

- Consolidate a repository into Markdown for LLM input
- Generate project overviews for quick onboarding
- Create code snapshots for review or archiving

⸻

## 📝 License

This project is released under the MIT License.

⸻
