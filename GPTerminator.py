import openai
import tiktoken
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
import os
import json
import sys
import configparser
from prompt_toolkit import prompt
from datetime import datetime
from pathlib import Path
import pyperclip
import inquirer

class GPTerminator:
    def __init__(self):
        self.config_selected = 'BASE_CONFIG'
        self.model = ''
        self.sys_prmpt = ''
        self.msg_hist = []
        self.cmd_init = ''
        self.cmds = {
                "quit": "quits the program",
                "help": "prints a list of acceptable commands",
                "regen": "requeries the last message",
                "save": "saves the chat history",
                "ccpy": "copies code block in last response",
                }
        self.api_key = ''
        self.prompt_count = 0
        self.save_folder = ''
        self.console = Console()

    def loadConfig(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.model = config[self.config_selected]['ModelName']
        self.sys_prmpt = config[self.config_selected]['SystemMessage']
        self.cmd_init = config[self.config_selected]['CommandInitiator']
        self.save_folder = config[self.config_selected]['SaveFolder']

    def printError(self, msg):
        self.console.print(f"[bold red]ERROR: [/]{msg}")

    def printCmds(self):
        self.console.print(f"[bold bright_black]Command : description[/]")
        for cmd, desc in self.cmds.items():
            self.console.print(f"[bright_black]{self.cmd_init}{cmd} : {desc}[/]")

    def saveChat(self):
        if self.prompt_count == 0:
            self.printError("cant save an empty discussion")
        else:
            self.console.print(f"[yellow]|!|[/][bold green] Name this chat[/bold green][bold gray] > [/bold gray]", end="")
            user_in = prompt().strip()
            save_path = Path('.') / self.save_folder / f"{user_in}.json"
            with open(save_path, "w") as f:
                json.dump(self.msg_hist, f, indent=4)

    def copyCode(self):
        last_resp = self.msg_hist[-1]['content']
        code_block_list = []
        index = 1
        while True:
            try: 
                code_block = last_resp.split("```")[index]
                code_block = "\n".join(code_block.split("\n")[1:])
                code_block_list.append(code_block)
            except:
                lst_len = len(code_block_list)
                if lst_len == 1:
                    pyperclip.copy(code_block_list[0])
                elif lst_len > 1:
                    for num, code_block in enumerate(code_block_list):
                        self.console.log(Panel.fit(code_block, title=f"Option {num + 1}"))
                    while True:
                        self.console.print(f"[yellow]|!|[/][bold green] Which code block do you want [/bold green][bold gray]> [/bold gray]", end="")
                        try:
                            idx = int(input())
                            if idx >= 1 and idx <= len(code_block_list):
                                break
                        except: pass
                        self.printError("incorrect input, try again")
                    pyperclip.copy(code_block_list[idx - 1])
                else:
                    self.printError("could not find code in previous response")
                return
            index += 2

    def queryUser(self):
        self.console.print(f"[yellow]|{self.prompt_count}|[/][bold green] Input [/bold green][bold gray]> [/bold gray]", end="")
        user_in = prompt().strip()
        if user_in == '':
            self.printError("user input is empty")
        elif user_in[0] == self.cmd_init:
            raw_cmd = user_in.split(self.cmd_init)
            cmd = raw_cmd[1].lower()
            if cmd in self.cmds:
                if cmd == 'quit':
                    sys.exit()
                elif cmd == 'help':
                    self.printCmds()
                elif cmd == 'regen':
                    if self.prompt_count > 0:
                        self.msg_hist.pop(-1)
                        last_msg = self.msg_hist.pop(-1)['content']
                        self.prompt_count -= 1
                        return last_msg
                    else:
                        self.printError("can't regenenerate, there is no previous prompt")
                elif cmd == 'save':
                    self.saveChat()
                elif cmd == 'ccpy':
                    if self.prompt_count > 0:
                        self.copyCode()
                    else:
                        self.printError("can't copy, there is no previous response")
            else:
                self.printError(f"{self.cmd_init}{cmd} in not in the list of commands")
        else:
            return user_in

    def getResponse(self, usr_prompt):
        self.msg_hist.append({'role': 'user', 'content': usr_prompt})
        resp = openai.ChatCompletion.create(model=self.model, messages=self.msg_hist, stream=True)
        collected_chunks = []
        collected_messages = []
        md = Markdown('')
        self.console.rule(title="Response", align="left", style="bright_black")
        with Live(md, console=self.console, transient=True) as live:
            for chunk in resp:
                collected_chunks.append(chunk)  # save the event response
                chunk_message = chunk['choices'][0]['delta']  # extract the message
                collected_messages.append(chunk_message)  # save the message
                full_reply_content = ''.join([m.get('content', '') for m in collected_messages])
                md = Markdown(full_reply_content)
                live.update(md)
                encoding = tiktoken.encoding_for_model(self.model)
                num_tokens = len(encoding.encode(full_reply_content))
        self.console.print(md)
        self.console.rule(title=f"TOKENS: {num_tokens} | {self.getTime()}", align="right", style="bright_black")
        self.console.print()
        self.msg_hist.append({"role": "assistant", "content": full_reply_content})

    def getTime(self):
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        return current_time

    def setApiKey(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key == None or self.api_key == '':
            self.printError("the OPENAI_API_KEY environment variable is missing")
            sys.exit()

    def printBanner(self):
        welcome_ascii = '''                                                        
 _____ _____ _____               _         _           
|   __|  _  |_   _|___ ___ _____|_|___ ___| |_ ___ ___ 
|  |  |   __| | | | -_|  _|     | |   | .'|  _| . |  _|
|_____|__|    |_| |___|_| |_|_|_|_|_|_|__,|_| |___|_|  
'''                                                       
        self.console.print(f"[bold green]{welcome_ascii}[/bold green]", end='')
        self.console.print(f"[bright_black]System prompt: {self.sys_prmpt}[/]")
        self.console.print(f"[bright_black]Model: {self.model}[/]")
        self.console.print(f"[bright_black]Type '{self.cmd_init}quit' to quit the program; '{self.cmd_init}help' for a list of cmds[/]\n")

    def run(self):
        self.loadConfig()
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        self.setApiKey()
        self.msg_hist.append({"role": "system", "content": self.sys_prmpt})
        self.printBanner()
        while True:
            usr_input = self.queryUser()
            if usr_input is not None:
                self.prompt_count += 1
                self.getResponse(usr_input)

if __name__ == "__main__":
    app = GPTerminator()
    app.run()
