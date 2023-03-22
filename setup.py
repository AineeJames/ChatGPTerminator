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
print("CONFIG PATH")
print(configpath)

config = configparser.ConfigParser()
config['SELECTED_CONFIG'] = {"configname": "BASE_CONFIG"}
config['BASE_CONFIG'] = { 
    "modelname": "gpt-3.5-turbo",
    "temperature": "1",
    "presencepenalty": "0",
    "frequencypenalty": "0",
    "systemmessage": "You are a helpful assistant named GPTerminator.",
    "commandinitiator": "!",
    "savefolder": "saves",
 }
with open(os.path.join(configpath, 'config.ini'), 'w') as configfile:
    config.write(configfile)

setup()
