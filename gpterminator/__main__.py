from gpterminator import GPTerminator


def main():
    app = GPTerminator.GPTerminator()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("Goodbye! Feel free to ask me any questions in the future.")
        exit(0)
