import argparse


def calculate(a: int, b: int, op: str) -> int:
    """Compute a op b where op is either 'add' or 'mul'."""
    if op == "add":
        return a + b
    if op == "mul":
        return a * b
    # argparse should prevent this, but keep it safe.
    raise ValueError(f"Unsupported op: {op}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple calculator CLI that adds or multiplies two integers."
    )
    # Positional arguments are optional to allow --version without them.
    parser.add_argument("a", type=int, nargs='?', help="First integer")
    parser.add_argument("b", type=int, nargs='?', help="Second integer")
    parser.add_argument(
        "--op",
        choices=["add", "mul"],
        default="add",
        help="Operation to perform (default: add)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed computation info before result",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version information and exit",
    )

    args = parser.parse_args()
    # If version flag is set, print version and exit immediately.
    if args.version:
        print("calc.py 1.0")
        return
    # Ensure that a and b are provided for normal operation.
    if args.a is None or args.b is None:
        parser.error("the following arguments are required: a b")
    if args.verbose:
        print(f"a={args.a}, b={args.b}, op={args.op}")
    print(calculate(args.a, args.b, args.op))


if __name__ == "__main__":
    main()
