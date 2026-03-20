import argparse


def greet(name: str, excited: bool = False) -> str:
    """Return the greeting message for the given name.

    If ``excited`` is True, the greeting ends with three exclamation marks.
    """
    if excited:
        return f"Hello, {name}!!!"
    return f"Hello, {name}!"


def main() -> None:
    parser = argparse.ArgumentParser(description="Greeting CLI with optional excitement.")
    parser.add_argument("name", help="Name of the person to greet")
    parser.add_argument(
        "--excited",
        action="store_true",
        help="Add extra excitement to the greeting",
    )
    args = parser.parse_args()
    print(greet(args.name, args.excited))


if __name__ == "__main__":
    main()
