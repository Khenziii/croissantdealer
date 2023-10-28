# croissantdealer
croissantdealer is a simple chess bot. He probably isn't the toughest enemy that you've ever faced, but it's definitely fun to create him! :) He has been written from scratch (well, almost. The communication with Lichess's API and move generation has been self-implemented. The only thing that we're using is the <a href="https://pypi.org/project/chess/">chess</a> library (we're only using it for board manipulation (no already built engines)). Other than that, it's also worth noting that croissantdealer is an absolute chad that never plays 1. d4 ;> And no, he doesn't sell croissants. You can play with him <a href="https://lichess.org/?user=croissantdealer#friend">here</a> 👍

# features
as of right now, croissantdealer has these features:
1. **minimax; alpha beta pruning** - the bot is using minimax for move generation :)
2. **transposition table** - the bot is using a transposition table to avoid evaluating position a couple of times

# Contributing
If you'd like to contribute, go ahead  :). All the contributions are **greatly** appreciated. I'll try to close all of the PR's and Issues ASAP. You can checkout the guide to enter the development enviorment below.

# Starting the dev environment
1. create the python virtual environment: `python3 -m venv env`
2. start the virtual environment: `source env/bin/activate` (if you're on Linux, Windows uses different syntax)
3. install all the needed packages: `pip3 install -r requirements.txt`,

After doing that, create the "secrets.env" file in this directory, and define the token there like that: `lichess_api_token="<your_bots_token_here>"` other than that, you should also define the dev_username there like that: `dev_username="<your_lichess_username>"` (the bot will reject other users game requests) and set the environment to dev by pasting this line: `environment="DEVELOPMENT"`. Now you can just run the bot (`python3 main.py`) and then head over to lichess ;D

# TO-DO List
1. actually make him never play 1. d4
2. make the bot think about the position while the opponent is thinking
3. implement the evaluation command