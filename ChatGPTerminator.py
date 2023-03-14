import openai
from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from rich.panel import Panel
py3tomllib = False
try:
    import tomllib
    py3tomllib = True
except: 
    import toml
    py3tomllib = False
import os
import signal
from datetime import datetime
from datetime import timezone
from zoneinfo import ZoneInfo
import json
import logging
import argparse
import sys

parser = argparse.ArgumentParser(description="Toggle logging")
parser.add_argument('--log', action='store_true', help='enable logging')
args = parser.parse_args()

if args.log:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

from prompt_toolkit import prompt

def complete_chat(prompt: str,chat_history: list[dict],model) -> str:
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
        model=model,
        messages= chat_history
    )
    # return response
    logging.debug(f"Got response from openai api")
    return response['choices'][0]['message']['content']

def make_chat_record():
    if not os.path.exists("chatlog"):
        os.makedirs("chatlog")
     # Get the current timestamp
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")

    # Create the file in the chatlog directory with the same name as the timestamp 
    file_path = os.path.join("chatlog", timestamp + '.txt')
    with open(file_path, 'w') as file:
        file.write('This is a file created at ' + timestamp)
        logging.debug(f"Made initial log file at {file_path}")
    return file_path

def save_chatlog(log_path,messages):
    # use json to save a log of the messages sent each time
    # user sends a message
    with open(log_path, 'w') as f:
        json.dump(messages, f, indent = 4)

def get_curr_time() -> str:
    now = datetime.now()
    current_time = now.strftime("%I:%M:%S %p") 
    return current_time

if __name__ == '__main__':
    log_path = make_chat_record()
                                                                                                                                               
    console = Console()

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key == None or '':
        console.print(f"[bold red]ERROR: [/bold red]Please provide an OPENAI_API_KEY evn varible")
        help_msg = Markdown("""```bash\nexport OPENAI_API_KEY=<place api key here>\n```""")
        console.print(help_msg)
        exit()
    openai.api_key = api_key

    with open("config.toml", "rb") as f:
        if py3tomllib:
            config = tomllib.load(f)
        else:
            config = toml.load("config.toml")

    welcome_ascii = '''                                                        
 _____ _____ _____               _         _           
|   __|  _  |_   _|___ ___ _____|_|___ ___| |_ ___ ___ 
|  |  |   __| | | | -_|  _|     | |   | .'|  _| . |  _|
|_____|__|    |_| |___|_| |_|_|_|_|_|_|__,|_| |___|_|  
'''                                                       
    console.print(f"[bold green]{welcome_ascii}[/bold green]", end='')
    console.print(f"[bright_black]System prompt: {config['system-msg']}[/]")
    console.print(f"[bright_black]Model: {config['model']}[/]\n")
    
    messages = [] #List of responses along with system prompt
    messages.append({"role": "system","content" : config['system-msg']})  
    while True:
        console.print("[bold green]Input[/bold green][bold gray] > [/bold gray]", end="")
        usr_in = prompt()
        if usr_in == 'exit':
            sys.exit()

        spinner = Spinner("aesthetic")
        with Live(
            Spinner("aesthetic"),
            transient = True,
            refresh_per_second = 20,
            ) as live:
                response = complete_chat(usr_in, messages,config['model'])

        console.clear_live()

        messages.append({"role": "assistant", "content" : response})
        resp_md = Markdown(response)
        console.rule(title="Response", align="left", style="bright_black")
        console.print(resp_md)
        console.rule(title=get_curr_time(), align="right", style="bright_black")
        console.print()
        save_chatlog(log_path,messages)
