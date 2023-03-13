import openai
from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown
import tomllib
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def complete_chat(prompt: str,chat_history: list[dict]) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= chat_history + {"role": "user", "content": prompt}
    )
    # return response
    return response['choices'][0]['message']['content']

if __name__ == '__main__':

    console = Console()

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    welcome_ascii = '''
       _____ _____ _______                  _             _             
      / ____|  __ \__   __|                (_)           | |            
     | |  __| |__) | | | ___ _ __ _ __ ___  _ _ __   __ _| |_ ___  _ __ 
     | | |_ |  ___/  | |/ _ \ '__| '_ ` _ \| | '_ \ / _` | __/ _ \| '__|
     | |__| | |      | |  __/ |  | | | | | | | | | | (_| | || (_) | |   
      \_____|_|      |_|\___|_|  |_| |_| |_|_|_| |_|\__,_|\__\___/|_|   '''
    console.print(f"[bold green]{welcome_ascii}[/bold green]")
    console.print(f"[dark-green]Model: {config['model']}[/dark-green]\n")

    usr_in = Prompt.ask("[bold green]Input[/bold green][bold gray]>[/bold gray]")
    resp = '''
    This is a test:
    ```python
    import os
    print("hello world")
    # here is a comment
    ```
    - a
    - b
    - c
    '''
    resp_md = Markdown(resp)
    console.print(f"[bold green]GPTerminator[/bold green][bold gray] > [/bold gray]")
    console.print(resp_md)
