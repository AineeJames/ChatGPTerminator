import openai
from openai import error
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
from pathlib import Path
import pyperclip
import time
import requests
import climage

class GPTerminator:
    def __init__(self):
        self.config_path = ""
        self.config_selected = ""
        self.model = ""
        self.temperature = ""
        self.presence_penalty = ""
        self.frequency_penalty = ""
        self.sys_prmpt = ""
        self.msg_hist = []
        self.cmd_init = ""
        self.cmds = {
            "quit": ["q", "quits the program"],
            "help": ["h", "prints a list of acceptable commands"],
            "pconf": [None, "prints out the users current config file"],
            "setconf": [None, "switches to a new config"],
            "regen": ["r", "generates a new response from the last message"],
            "load": ["l", "loads a previously saved chatlog"],
            "save": ["s", "saves the chat history"],
            "ifile": [None, "allows the user to analyze files with a prompt"],
            "cpyall": ["ca", "copies all raw text from the previous response"],
            "ccpy": ["cc", "copies code blocks from the last response"],
            "dalle": [None, "generates images and provides a link for download"],
        }
        self.api_key = ""
        self.prompt_count = 0
        self.save_path = ""
        self.console = Console()

    def getConfigPath(self):
        if "APPDATA" in os.environ:
            confighome = os.environ["APPDATA"]
        elif "XDG_CONFIG_HOME" in os.environ:
            confighome = os.environ["XDG_CONFIG_HOME"]
        else:
            confighome = os.path.join(os.environ["HOME"], ".config")
        configpath = os.path.join(confighome, "gpterminator", "config.ini")
        self.config_path = configpath

    def loadConfig(self):
        self.getConfigPath()
        config = configparser.ConfigParser()
        config.read(self.config_path)
        self.config_selected = config["SELECTED_CONFIG"]["ConfigName"]
        self.model = config[self.config_selected]["ModelName"]
        self.sys_prmpt = config[self.config_selected]["SystemMessage"]
        self.cmd_init = config[self.config_selected]["CommandInitiator"]
        self.save_path = config[self.config_selected]["SavePath"]
        self.temperature = config[self.config_selected]["Temperature"]
        self.presence_penalty = config[self.config_selected]["PresencePenalty"]
        self.frequency_penalty = config[self.config_selected]["FrequencyPenalty"]

    def printError(self, msg):
        self.console.print(Panel(f"[bold red]ERROR: [/]{msg}", border_style="red"))

    def printCmds(self):
        self.console.print(f"[bold bright_black]Command : description[/]")
        for cmd, desc in self.cmds.items():
            short = "" if desc[0] is None else f"({desc[0]})"
            self.console.print(f"[bright_black]{self.cmd_init}{cmd} {short}: {desc[1]}[/]")

    def saveChat(self):
        if self.prompt_count == 0:
            self.printError("cant save an empty discussion")
        else:
            self.console.print(
                f"[yellow]|{self.cmd_init}|[/][bold green] Name this chat[/bold green][bold gray] > [/bold gray]",
                end="",
            )
            user_in = prompt().strip().replace(" ", "_")
            with open(Path(self.save_path) / f"{user_in}.json", "w") as f:
                json.dump(self.msg_hist, f, indent=4)
            self.console.print(f"[bright_black]Saved file as {user_in}.json[/]")

    def copyCode(self):
        last_resp = self.msg_hist[-1]["content"]
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
                        self.console.log(
                            Panel.fit(code_block, title=f"Option {num + 1}")
                        )
                    while True:
                        self.console.print(
                            f"[yellow]|{self.cmd_init}|[/][bold green] Which code block do you want [/bold green][bold gray]> [/bold gray]",
                            end="",
                        )
                        try:
                            idx = int(input())
                            if idx >= 1 and idx <= len(code_block_list):
                                break
                        except:
                            pass
                        self.printError("incorrect input, try again")
                    pyperclip.copy(code_block_list[idx - 1])
                else:
                    self.printError("could not find code in previous response")
                return
            index += 2

    def printConfig(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        self.console.print(f"[bold bright_black]Config Path: {self.config_path}")
        self.console.print("[bold bright_black]Setting: value")
        for setting in config[self.config_selected]:
            self.console.print(
                f"[bright_black]{setting}: {config[self.config_selected][setting]}[/]"
            )

    def loadChatlog(self):
        self.console.print("[bold bright_black]Available saves:[/]")
        file_dict = {}
        for idx, file_name in enumerate(os.listdir(f"{self.save_path}")):
            file_str = file_name.split(".")[0]
            file_dict[idx + 1] = file_str
            self.console.print(
                f"[bold bright_black]({idx + 1}) > [/][red]{file_str}[/]"
            )
        if len(file_dict) == 0:
            self.printError("you have no saved chats")
            return
        while True:
            self.console.print(
                f"[yellow]|{self.cmd_init}|[/][bold green] Select a file to load [/bold green][bold gray]> [/bold gray]",
                end="",
            )
            selection = input()
            if selection.isdigit() == True and int(selection) in file_dict:
                break
            else:
                self.printError(f"{selection} is not a valid selection")
        with open(
            Path(f"{self.save_path}") / f"{file_dict[int(selection)]}.json", "r"
        ) as f:
            save = json.load(f)
        self.prompt_count = 0
        self.msg_hist = save
        for msg in save:
            role = msg["role"]
            if role == "user":
                self.console.print(
                    f"[yellow]|{self.prompt_count}|[/][bold green] Input [/bold green][bold gray]> [/bold gray]",
                    end="",
                )
                self.console.print(msg["content"])
                self.prompt_count += 1
            elif role == "assistant":
                encoding = tiktoken.encoding_for_model(self.model)
                num_tokens = len(encoding.encode(msg["content"]))
                subtitle_str = f"[bright_black]Tokens:[/] [bold red]{num_tokens}[/]"
                md = Panel(
                    Markdown(msg["content"]),
                    border_style="bright_black",
                    title="[bright_black]Assistant[/]",
                    title_align="left",
                    subtitle=subtitle_str,
                    subtitle_align="right",
                )
                self.console.print(md)
                self.console.print()
            else:
                pass

    def setConfig(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        config_dict = {}
        config_num = 1
        for section in config:
            if str(section) != "DEFAULT" and str(section) != "SELECTED_CONFIG":
                config_dict[config_num] = str(section)
                self.console.print(
                    f"[bright_black]({config_num}) > [/][red]{str(section)}[/]"
                )
                config_num += 1
        while True:
            self.console.print(
                f"[yellow]|{self.cmd_init}|[/][bold green] Select which config you want [/bold green][bold gray]> [/bold gray]",
                end="",
            )
            sel_config = input()
            if sel_config.isdigit() == True and int(sel_config) in config_dict:
                break
            else:
                self.printError("invalid selection, please try again")
        config["SELECTED_CONFIG"]["ConfigName"] = f"{config_dict[int(sel_config)]}"
        with open(self.config_path, "w") as configfile:
            config.write(configfile)
        self.loadConfig()
        self.printConfig()

    def copyAll(self):
        if self.prompt_count == 0:
            self.printError("cannot run cpyall when there are no responses")
            return
        last_resp = self.msg_hist[-1]["content"]
        pyperclip.copy(last_resp)
        self.console.print(f"[bright_black]Copied text to keyboard...[/]")

    def useDalle(self):
        while True:
            self.console.print(
                f"[yellow]|{self.prompt_count}|[/][bold green] Image Prompt [/bold green][bold gray]> [/bold gray]",
                end="",
            )
            user_in = prompt()
            if len(user_in) > 10:
                break
            else:
                self.printError("the image prompt should be at least 10 characters")
        with self.console.status(
            "", spinner="bouncingBar", spinner_style="bold red"
        ) as status:
            status.update(status="[bright_black]Generating image...[/]")
            img_response = openai.Image.create(prompt=user_in, n=1, size="1024x1024")
            image_url = img_response["data"][0]["url"]
            resp = requests.get(image_url, stream=True)
            cli_image = climage.convert(resp.raw, is_unicode=True)
        self.console.print(f"[bold green]Image preview:[/]")
        print(cli_image)
        self.console.print(f"[bold green]Link: [/][bright_black]{image_url}[/]")
        pyperclip.copy(image_url)
        self.console.print(f"[bright_black]Image link copied to clipboard![/]")

    def analyzeFile(self):
        while True:
            self.console.print(
                f"[yellow]|!|[/][bold green] Provide the file path to analyze [/bold green][bold gray]> [/bold gray]",
                end="",
            )
            user_in = prompt().strip()
            if os.path.exists(user_in):
                with open(user_in, 'r') as file:
                    file_content = file.read()
                break
            else:
                self.printError(f"{user_in} cannot be found")

        while True:
            self.console.print(
                f"[yellow]|{self.prompt_count}|[/][bold green] Prompt for {user_in} [/bold green][bold gray]> [/bold gray]",
                end="",
            )
            user_prmt = prompt().strip()
            if user_prmt != "":
                break
            else:
                self.printError(f"you cannot have an empty prompt")

        msg = f"{user_prmt}: '{file_content}'"
        self.getResponse(msg)

            



    def queryUser(self):
        self.console.print(
            f"[yellow]|{self.prompt_count}|[/][bold green] Input [/bold green][bold gray]> [/bold gray]",
            end="",
        )
        user_in = prompt().strip()
        if user_in == "":
            self.printError("user input is empty")
        elif user_in[0] == self.cmd_init:
            raw_cmd = user_in.split(self.cmd_init)
            cmd = raw_cmd[1].lower().split()[0]
            if cmd in self.cmds or cmd in [shrt[0] for shrt in self.cmds.values()]:
                if cmd == "quit" or cmd == "q":
                    sys.exit()
                elif cmd == "help" or cmd == "h":
                    self.printCmds()
                elif cmd == "regen" or cmd == "r":
                    if self.prompt_count > 0:
                        self.msg_hist.pop(-1)
                        last_msg = self.msg_hist.pop(-1)["content"]
                        self.prompt_count -= 1
                        return last_msg
                    else:
                        self.printError(
                            "can't regenenerate, there is no previous prompt"
                        )
                elif cmd == "save" or cmd == "s":
                    self.saveChat()
                elif cmd == "ccpy" or cmd == "cc":
                    if self.prompt_count > 0:
                        self.copyCode()
                    else:
                        self.printError("can't copy, there is no previous response")
                elif cmd == "pconf":
                    self.printConfig()
                elif cmd == "load" or cmd == "l":
                    self.loadChatlog()
                elif cmd == "setconf":
                    self.setConfig()
                elif cmd == "cpyall" or cmd == "ca":
                    self.copyAll()
                elif cmd == "dalle":
                    self.useDalle()
                elif cmd == "ifile":
                    self.analyzeFile()
            else:
                self.printError(
                    f"{self.cmd_init}{cmd} in not in the list of commands, type {self.cmd_init}help"
                )
        else:
            return user_in

    def getResponse(self, usr_prompt):
        self.msg_hist.append({"role": "user", "content": usr_prompt})
        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=self.msg_hist,
                stream=True,
                temperature=float(self.temperature),
                presence_penalty=float(self.presence_penalty),
                frequency_penalty=float(self.frequency_penalty),
            )
        except error.Timeout as e:
            self.printError(f"OpenAI API request timed out: {e}")
            sys.exit()
        except error.APIError as e:
            self.printError(f"OpenAI API returned an API Error: {e}")
            sys.exit()
        except error.APIConnectionError as e:
            self.printError(f"OpenAI API request failed to connect: {e}")
            sys.exit()
        except error.InvalidRequestError as e:
            self.printError(f"OpenAI API request was invalid: {e}")
            sys.exit()
        except error.AuthenticationError as e:
            self.printError(f"OpenAI API request was not authorized: {e}")
            sys.exit()
        except error.PermissionError as e:
            self.printError(f"OpenAI API request was not permitted: {e}")
            sys.exit()
        except error.RateLimitError as e:
            self.printError(f"OpenAI API request exceeded rate limit: {e}")
            sys.exit()

        collected_chunks = []
        collected_messages = []
        subtitle_str = f"[bright_black]Tokens:[/] [bold red]{0}[/] | "
        subtitle_str += f"[bright_black]Time Elapsed:[/][bold yellow] {0.0}s [/]"
        md = Panel(
            Markdown(""),
            border_style="bright_black",
            title="[bright_black]Assistant[/]",
            title_align="left",
            subtitle=subtitle_str,
            subtitle_align="right",
        )

        start_time = time.time()

        with Live(md, console=self.console, transient=True) as live:
            for chunk in resp:
                collected_chunks.append(chunk)  # save the event response
                chunk_message = chunk["choices"][0]["delta"]  # extract the message
                collected_messages.append(chunk_message)  # save the message
                full_reply_content = "".join(
                    [m.get("content", "") for m in collected_messages]
                )
                encoding = tiktoken.encoding_for_model(self.model)
                num_tokens = len(encoding.encode(full_reply_content))
                time_elapsed_s = time.time() - start_time
                subtitle_str = f"[bright_black]Tokens:[/] [bold red]{num_tokens}[/] | "
                subtitle_str += f"[bright_black]Time Elapsed:[/][bold yellow] {time_elapsed_s:.1f}s [/]"
                md = Panel(
                    Markdown(full_reply_content),
                    border_style="bright_black",
                    title="[bright_black]Assistant[/]",
                    title_align="left",
                    subtitle=subtitle_str,
                    subtitle_align="right",
                )
                live.update(md)
        self.console.print(md)
        self.console.print()
        self.msg_hist.append({"role": "assistant", "content": full_reply_content})

    def setApiKey(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key == None or self.api_key == "":
            self.printError("the OPENAI_API_KEY environment variable is missing")
            sys.exit()

    def printBanner(self):
        welcome_ascii = """                                                        
 _____ _____ _____               _         _           
|   __|  _  |_   _|___ ___ _____|_|___ ___| |_ ___ ___ 
|  |  |   __| | | | -_|  _|     | |   | .'|  _| . |  _|
|_____|__|    |_| |___|_| |_|_|_|_|_|_|__,|_| |___|_|  
"""
        self.console.print(f"[bold green]{welcome_ascii}[/bold green]", end="")
        self.console.print(f"[bright_black]System prompt: {self.sys_prmpt}[/]")
        self.console.print(f"[bright_black]Model: {self.model}[/]")
        self.console.print(
            f"[bright_black]Type '{self.cmd_init}quit' to quit the program; '{self.cmd_init}help' for a list of cmds[/]\n"
        )

    def checkDirs(self):

        # get paths
        if "APPDATA" in os.environ:
            confighome = os.environ["APPDATA"]
        elif "XDG_CONFIG_HOME" in os.environ:
            confighome = os.environ["XDG_CONFIG_HOME"]
        else:
            confighome = os.path.join(os.environ["HOME"], ".config")
        configpath = os.path.join(confighome, "gpterminator")
        savespath = os.path.join(configpath, "saves")

        #check if paths/files exist
        config_exists = os.path.exists(os.path.join(configpath, "config.ini"))
        configpath_exists = os.path.exists(configpath)
        saves_exist = os.path.exists(savespath)

        if configpath_exists == False:
            self.console.print(f"[bright_black]Initializing config path ({configpath})...[/]")
            os.mkdir(configpath)

        # make paths/files
        if config_exists == False:
            full_config_path = os.path.join(configpath, "config.ini")
            self.console.print(f"[bright_black]Initializing config file ({full_config_path})...[/]")
            config = configparser.ConfigParser()
            config["SELECTED_CONFIG"] = {"configname": "BASE_CONFIG"}
            config["BASE_CONFIG"] = {
                "ModelName": "gpt-3.5-turbo",
                "Temperature": "1",
                "PresencePenalty": "0",
                "FrequencyPenalty": "0",
                "SystemMessage": "You are a helpful assistant named GPTerminator.",
                "CommandInitiator": "!",
                "SavePath": f"{savespath}",
            }
            with open(full_config_path, "w") as configfile:
                config.write(configfile)
        
        if saves_exist == False:
            self.console.print(f"[bright_black]Initializing save path ({savespath})...[/]")
            os.mkdir(savespath)

    def run(self):
        self.checkDirs()
        self.loadConfig()
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.setApiKey()
        self.msg_hist.append({"role": "system", "content": self.sys_prmpt})
        self.printBanner()
        while True:
            usr_input = self.queryUser()
            if usr_input is not None:
                self.prompt_count += 1
                self.getResponse(usr_input)
