#!/bin/bash

 # Set the file path for apikey.txt
 FILEPATH="apikey.txt"

 # Read the contents of apikey.txt into the OPENAI_API_KEY environment variable
 export OPENAI_API_KEY=$(cat $FILEPATH)
