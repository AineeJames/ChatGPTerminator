import openai
from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown
import tomllib
import os

def complete_chat(prompt: str,chat_history: list[dict]) -> str:
    ''' 
	chat_hist is list of messages in format
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
	'''
    chat_history.append({"role": "user", "content": prompt})
    print(chat_history)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= chat_history
    )
    # return response
    return response['choices'][0]['message']['content']


if __name__ == '__main__':

    console = Console()

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key == None or '':
        console.print(f"[bold red]ERROR: [/bold red]Please provide an OPENAI_API_KEY evn varible")
        help_msg = Markdown("""```bash\nexport OPENAI_API_KEY=<place api key here>\n```""")
        console.print(help_msg)
        exit()
    openai.api_key = api_key

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
    messages = [] #List of responses along with system prompt
    messages.append({"role": "system","content" : config['system-msg']}) 
    
    response = complete_chat(usr_in, messages)
    messages.append({"role": "assistant", "content" : response})
    print(response)

