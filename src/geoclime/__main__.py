"""Command line: python -m geoclime list | show <dataset> [--start Y] [--end Y]"""
import argparse

from . import list_datasets, load


def main() -> None:
    p = argparse.ArgumentParser(prog="geoclime")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list available datasets")
    show = sub.add_parser("show", help="summarise one dataset")
    show.add_argument("name")
    show.add_argument("--start", type=int)
    show.add_argument("--end", type=int)
    args = p.parse_args()

    if args.cmd == "list":
        print(list_datasets().to_string(index=False))
    else:
        for key, value in load(args.name, start=args.start, end=args.end).summary().items():
            print(f"{key:>17}: {value}")


if __name__ == "__main__":
    main()
