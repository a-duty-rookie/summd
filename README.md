# code2md

`code2md` は、指定したディレクトリ内のソースコードや設定ファイルを一つのMarkdownファイルにまとめるためのコマンドラインツールです。プロジェクト全体の概要を把握したり、LLM（大規模言語モデル）へのインプットとして整形する際に役立ちます。

## ✨ 主な機能

- **複数ファイルの一括集約**: プロジェクト内の多数のファイルを1つのMarkdownにまとめます。
- **`.gitignore` 対応**: `.gitignore` ファイルに記載されたパターンを自動で無視し、不要なファイルを除外します。
- **Jupyter Notebook 対応**: `.ipynb` ファイルを解析し、Markdownセルとコードセルを整形して出力に含めます。
- **柔軟な除外設定**: デフォルトの無視パターン（`node_modules`など）に加え、任意の拡張子をコマンドラインオプションで除外できます。
- **多様な言語サポート**: Python, JavaScript, HTML, CSS, Dockerfileなど、多くの言語に対応しています。

## 🚀 インストール

``` bash
pip install code2md
```

<!-- リポジトリをクローンし、`pip` を使ってインストールします。

```bash
git clone https://github.com/a-duty-rookie/code2md.git
cd code2md
pip install .
``` -->

## 使い方

基本的な使い方は以下の通りです。

```bash
code2md <対象ディレクトリ> <出力ファイルパス>
```

### 例

現在のディレクトリ (`.`) の内容を `output/summary.md` に出力する場合:

```bash
code2md . output/summary.md
```

## ⚙️ オプション

### `-i`, `--ignore`

特定の拡張子を持つファイルを無視します。複数の拡張子を指定する場合は、スペースで区切ります。

#### 例

`.log` ファイルと `.tmp` ファイルを無視する場合:

```bash
code2md . summary.md --ignore .log .tmp
```

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。
