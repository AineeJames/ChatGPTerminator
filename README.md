# GPTerminal - A ChatGPT Terminal Interface :robot:

![Screenshot of GPTerminal](./imgs/example.png)

This terminal interface provides a convenient way to interact with ChatGPT using your command line interface.

## Getting Started :rocket:

To use this terminal interface, follow these steps:

1. Clone this repository to your local machine.
2. Navigate to the cloned directory using your command line interface.
3. Create a virtual environment by using the following command:

   ```
   python3 -m venv venv
   ```

4. Install the pip requirements into the venv:

   ```
   pip install -r requirements.txt
   ```

5. Set the OPENAI_API_KEY env variable

   ```
   export OPENAI_API_KEY=PUT_API_KEY_HERE
   ```

6. Run the following command to start the ChatGPT terminal interface:

   ```
   python GPTerminal.py
   ```

7. You can now start chatting. Type a message and press Enter to get a response.

8. Type !help for a list of commands to use


## Configuration

Currently, a couple basic configuration settings are available for GPTerminal.

   ```ini
   [BASE_CONFIG]
   ModelName = gpt-3.5-turbo
   SystemMessage = You are a helpful assistant.
   CommandInitiator = !
   SaveFolder = saves
   ```

- **ModelName:** this is the model used when chatting
- **SystemMessage:** this is the starting system message sent to the API
- **CommandInitiator:** this can be set to change the default !<cmd> structure
- **SaveFolder:** this changes the location of the save folder when running !save

## Contributing :raised_hands:

We welcome contributions to this project. If you find a bug, have a feature request, or want to contribute code, please open an issue or submit a pull request.
