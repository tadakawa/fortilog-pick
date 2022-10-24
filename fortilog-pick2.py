"""とりあえず今のテクニックで作り直し
"""
import csv
import gzip
import sys
from argparse import ArgumentParser
from pathlib import Path


def pick_column(row: list[str], columns: tuple[str], sep: str = "=") -> list[str]:
    def to_dict(row: list[str], columns: tuple[str]):
        return dict(col.split(sep, 1) for col in row if col.startswith(columns))

    try:
        row_dict = to_dict(row, columns)
        return [row_dict.get(column, "") for column in columns]
    except ValueError:
        print("ログフォーマットが不正です", file=sys.stderr)
        sys.exit(1)


def main():
    parser = ArgumentParser(
        description='ログファイル(CSV)のカラム抽出 ("field1=value","field2=value",)'
    )
    parser.add_argument(
        "field",
        type=str,
        help='取得カラム名 (形式："srcip,dstip,...")',
    )
    parser.add_argument(
        "filename",
        type=str,
        nargs="+",
        help="ログファイル名（.csv or .csv.gz)",
    )
    parser.add_argument(
        "-F",
        type=str,
        metavar="fs",
        help='カラム名と値のセパレータ (default "=")',
        default="=",
    )
    args = parser.parse_args()

    columns = tuple(args.field.split(","))

    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    writer.writerow(columns)
    for filename in args.filename:
        for file in Path().glob(filename):
            open_log = gzip.open if file.name.endswith(".gz") else open
            with open_log(file, mode="rt") as f:
                writer.writerows(
                    pick_column(row, columns, args.F) for row in csv.reader(f)
                )


if __name__ == "__main__":
    main()
