"""Command line entry point for rendering the sticker set."""

import argparse
import sys
from pathlib import Path

from .designs import DESIGNS

DEFAULT_OUTPUT_DIR = Path("output")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="python -m stickers",
        description="Render the retro-futurist sticker set as transparent PNGs.",
    )
    parser.add_argument(
        "-o", "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
        help="directory to write PNGs into (default: %(default)s)",
    )
    parser.add_argument(
        "--only", action="append", metavar="NAME", dest="only",
        help="render just this design; repeatable. See --list for valid names.",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="list the available design names and exit",
    )
    return parser


def select(only):
    """Return the (name, draw) pairs to render, in registry order."""
    if not only:
        return list(DESIGNS.items())

    unknown = [name for name in only if name not in DESIGNS]
    if unknown:
        raise SystemExit(
            f"unknown design(s): {', '.join(unknown)}\n"
            f"available: {', '.join(DESIGNS)}"
        )
    return [(name, fn) for name, fn in DESIGNS.items() if name in set(only)]


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.list:
        for name in DESIGNS:
            print(name)
        return 0

    selected = select(args.only)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for name, fn in selected:
        print(f"Generating {name}...", end=" ", flush=True)
        path = args.output_dir / f"{name}.png"
        fn().save(path, "PNG")
        print(f"saved → {path}")

    count = len(selected)
    print(f"\nDone! {count} sticker{'s' if count != 1 else ''} "
          f"generated in {args.output_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
