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
