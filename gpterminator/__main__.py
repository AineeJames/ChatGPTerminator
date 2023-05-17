import sys

from . import GPTerminator


def main():
    app = GPTerminator.GPTerminator()
    passed_input = " ".join(sys.argv[1:]) if sys.argv[1:] else None

    app.run(passed_input)


if __name__ == "__main__":
    main()
