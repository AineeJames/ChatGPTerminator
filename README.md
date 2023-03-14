# GPTerminal - A ChatGPT Terminal Interface :robot:

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
   pip install -r < requirements.txt
   ```

5. Set the OPENAI_API_KEY env variable

   ```
   export OPENAI_API_KEY="PUT_API_KEY_HERE"
   ```

6. Run the following command to start the ChatGPT terminal interface:

   ```
   python ChatGPTerminal.py
   ```

7. You can now start chatting. Type a message and press Enter to get a response.



## Configuration

Currently, a couple basic configuration settings are available for GPTerminal.

   ```
   system-msg="You are a helpful assistant."
   model="gpt-3.5-turbo"
   ```

- **system-msg:** this is the system message sent to openai's api
- **model:** this is the model that GPTerminal

## Screenshots :camera:

Here are some screenshots of the ChatGPT terminal interface:

![ChatGPT Terminal Interface Screenshot 1](screenshots/screenshot1.png)
![ChatGPT Terminal Interface Screenshot 2](screenshots/screenshot2.png)

## Contributing :raised_hands:

We welcome contributions to this project. If you find a bug, have a feature request, or want to contribute code, please open an issue or submit a pull request.
