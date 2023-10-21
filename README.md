# !!!WARNING!!!
At the moment, the whole code is just boilerplate. The bot is not actually "thinking" yet. Working on it :)

# croissantdealer
croissantdealer is a simple chess bot. He probably isn't the toughest enemy that you've ever faced, but it's defienietly fun to create him! :) (He also is an absolute chad that never plays 1. d4 ;>) And no, he doesn't sell croissants. You can play with him <a href="https://lichess.org/?user=croissantdealer#friend">here</a> 👍

# Contributing
If you'd like to contribute, go ahead  :). All of the contributions are **greatly** appreciated. I'll try to close all of the PR's and Issues ASAP. You can checkout the guide to enter the development enviorment below.

# Starting the dev environment
1. create the python virtual environment: `python3 -m venv env`
2. start the virtual environment: `source env/bin/activate` (if you're on Linux, Windows uses different syntax)
3. install all the needed packages: `pip3 install -r requirements.txt`,

After doing that, create the "secrets.env" file in this directory, and define the token there like that: `lichess_api_token="<your_bots_token_here>"` other than that, you should also define the dev_username there like that: `dev_username="<your_lichess_username>"` (the bot will reject other users game requests) and set the environment to dev by pasting this line: `environment="DEVELOPMENT"`. Now you can just run the bot (`python3 main.py`) and then head over to lichess ;D

# TO-DO List
1. actually make him never play 1. d4