from setuptools import setup
import os
import configparser


if 'APPDATA' in os.environ:
    confighome = os.environ['APPDATA']
elif 'XDG_CONFIG_HOME' in os.environ:
    confighome = os.environ['XDG_CONFIG_HOME']
else:
    confighome = os.path.join(os.environ['HOME'], '.config')
configpath = os.path.join(confighome, 'gpterminator')
if not os.path.exists(configpath):
    os.mkdir(configpath)
savespath = os.path.join(configpath, "saves")
if not os.path.exists(savespath):
    os.mkdir(savespath)

config = configparser.ConfigParser()
config['SELECTED_CONFIG'] = {"configname": "BASE_CONFIG"}
config['BASE_CONFIG'] = { 
    "ModelName": "gpt-3.5-turbo",
    "Temperature": "1",
    "PresencePenalty": "0",
    "FrequencyPenalty": "0",
    "SystemMessage": "You are a helpful assistant named GPTerminator.",
    "CommandInitiator": "!",
    "SavePath": f"{savespath}",
 }
with open(os.path.join(configpath, 'config.ini'), 'w') as configfile:
    config.write(configfile)

setup()
