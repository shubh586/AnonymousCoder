import argparse


def greet(name: str) -> str:
    """Return the greeting message for the given name."""
    return f"Hello, {name}!"


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple greeting CLI.")
    parser.add_argument("name", help="Name of the person to greet")
    args = parser.parse_args()
    print(greet(args.name))


if __name__ == "__main__":
    main()
