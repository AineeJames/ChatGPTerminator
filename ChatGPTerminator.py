import openai
from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from rich.panel import Panel
import tomllib
import os
import signal

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
    # print(chat_history)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= chat_history
    )
    # return response
    return response['choices'][0]['message']['content']

def handle_sigint(signum, frame):
    console.print("\n[bold green]Closing...[/bold green]")
    exit()                                                                                           

if __name__ == '__main__':

    signal.signal(signal.SIGINT, handle_sigint)                                                                                                   
                                                                                                                                               
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
    console.print(f"[bold green]Initial prompt: {config['system-msg']}[/bold green]")
    console.print(f"[dark-green]Model: {config['model']}[/dark-green]\n")
    
    messages = [] #List of responses along with system prompt
    messages.append({"role": "system","content" : config['system-msg']})  
    while True:
        usr_in = Prompt.ask("[bold green]Input[/bold green][bold gray]>[/bold gray]")
        spinner = Spinner("aesthetic")
        with Live(
            Spinner("aesthetic"),
            transient = True,
            refresh_per_second = 20,
            ) as live:
                response = complete_chat(usr_in, messages)

        console.clear_live()

        messages.append({"role": "assistant", "content" : response})
        resp_md = Markdown(response)
        console.print(Panel.fit(resp_md, border_style="blue"))
