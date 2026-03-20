import argparse


def greet(name: str, shout: bool = False) -> str:
    """Return the greeting message for the given name.

    If ``shout`` is True, the greeting ends with three exclamation marks.
    """
    if shout:
        return f"Hello, {name}!!!"
    return f"Hello, {name}!"


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple greeting CLI.")
    parser.add_argument("name", help="Name of the person to greet")
    parser.add_argument(
        "--shout",
        action="store_true",
        help="Print the greeting with extra exclamation marks",
    )
    args = parser.parse_args()
    print(greet(args.name, shout=args.shout))


if __name__ == "__main__":
    main()
