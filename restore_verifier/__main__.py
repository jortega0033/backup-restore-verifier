# Command line entry point: parses options; product commands are not built yet.
import argparse
import sys

from . import __version__

NOT_BUILT = "not implemented yet: see #2"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="restore_verifier",
        description="Local backup restore rehearsal and comparison workbench.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--workspace", help="workspace directory")
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.add_parser("init-demo", help="create the demo workspace (not built yet)")
    serve = sub.add_parser("serve", help="run the app on 127.0.0.1 (not built yet)")
    serve.add_argument("--port", type=int, default=8768, help="port (default 8768)")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    print(NOT_BUILT, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
