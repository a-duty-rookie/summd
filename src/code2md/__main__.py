import argparse
from pathlib import Path
from typing import Sequence

from code2md.generator import generate_markdown


def main(argv: Sequence[str] | None = None) -> None:
    """
    code2mdツールのCLIエントリーポイント。

    コマンドライン引数を解析し、Markdown生成関数を呼び出します。
    """
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

    args = parser.parse_args(argv)

    # 文字列をPathオブジェクトに変換
    root_path = Path(args.root_path)
    output_path = Path(args.output_path)

    generate_markdown(root_path, output_path, args.ignore)


if __name__ == "__main__":
    main()
