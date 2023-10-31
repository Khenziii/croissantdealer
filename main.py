import requests
from dotenv import load_dotenv
import os
import threading
import json
import datetime
import pytz

from engine import Croissantdealer

# define stuff
# get the token from secrets.env
# load all the variables from secrets.env into python environment
load_dotenv("secrets.env")
# get the variables
token = os.getenv('lichess_api_token')
# prod - "PRODUCTION", dev - "DEVELOPMENT"
environment = os.getenv("environment")
# the username that will be able to play with the bot if in dev environment
dev_username = os.getenv("dev_username")
verbose = os.getenv("verbose")

# set some constants
headers = {'Authorization': f'Bearer {token}'}
url = "https://lichess.org"

# set some variables
active_games = []


class Logger:
    """
    Logs stuff

    :param timezone: The timezone to use
    """

    def __init__(self, timezone: str = "Europe/Warsaw"):
        self.timezone = timezone

    def get_current_time(self, timezone: str = None):
        """returns the current time in string format"""
        if not timezone:
            timezone = self.timezone

        # get the time in the specified timezone
        time = pytz.timezone(timezone)
        # get the datetime object
        datetime_time = datetime.datetime.now(time)

        return datetime_time.strftime(f"%d/%m/%y - %H:%M:%S")

    def info(self, msg: str):
        print(f"[i] {self.get_current_time()} > {msg}")

    def warning(self, msg: str):
        print(f"[w] {self.get_current_time()} > {msg}")

    def error(self, msg: str):
        print(f"[e] {self.get_current_time()} > {msg}")


class Lichess:
    """Talk with Lichess's API"""

    def __init__(self, token: str, headers: dict, url: str, environment: str, verbose: bool = False) -> None:
        self.token = token
        self.headers = headers
        self.url = url
        self.environment = environment
        self.verbose = verbose
        self.command_list = ["?help", "?eval"]

        # type them in lowercase!!
        self.accepted_variants = ["standard", "fromposition"]

    def login(self):
        return requests.get(f'{self.url}/api/stream/event', headers=self.headers, stream=True)

    def handle_event_stream(self, response):
        for line in response.iter_lines():
            # filter out keep-alive new lines
            if line:
                logs.info("Received a event!")

                decoded_line = line.decode('utf-8')
                json_data = json.loads(decoded_line)

                if self.verbose:
                    logs.info(json_data)

                # process the events here
                # if a challenge request
                if json_data["type"] == "challenge":
                    logs.info(json_data)

                    challenge_id = json_data["challenge"]["id"]
                    # eg. "blitz"
                    challenge_time_control = json_data["challenge"]["speed"]
                    # eg. "standard"
                    challenge_variant = json_data["challenge"]["variant"]["key"]
                    challenge_rated = json_data["challenge"]["rated"]

                    sender_username = json_data["challenge"]["challenger"]["id"]
                    sender_title = json_data["challenge"]["challenger"]["title"]
                    sender_elo = json_data["challenge"]["challenger"]["rating"]
                    sender_color = json_data["challenge"]["finalColor"]

                    if sender_color == "black":
                        our_color = "white"
                    else:
                        our_color = "black"

                    if not sender_title:
                        sender_title = ""

                    logs.info(f"Challenge sent by {sender_title}{sender_username} with an rating of: {sender_elo}.")
                    if self.verbose:
                        logs.info(f"{sender_username}'s challenge id: {challenge_id}, "
                                  f"time control: {challenge_time_control}, challenge variant: {challenge_variant}")

                    if challenge_variant.lower() in self.accepted_variants:
                        if not challenge_rated:
                            if environment != "DEVELOPMENT":
                                self.accept_game(challenge_id)
                            else:
                                if sender_username == dev_username:
                                    self.accept_game(challenge_id)
                                else:
                                    self.reject_game(game_id=challenge_id,
                                                     reason=f"we're in dev environment, and the user isn't {dev_username}")
                        else:
                            self.reject_game(game_id=challenge_id, reason=f"the sender tried to play a ranked game",
                                             reason_to_send="casual")
                    else:
                        self.reject_game(game_id=challenge_id, reason=f"it didn't contain the correct variant",
                                         reason_to_send="variant")

                # create a stream for all the games
                elif json_data["type"] == "gameStart":
                    game_id = json_data["game"]["id"]
                    color = json_data["game"]["color"]
                    fen = json_data["game"]["fen"]

                    self.start_game(game_id=game_id, color=color, fen=fen)

    def play_move(self, game_id: str, move: str, croissantdealer: Croissantdealer):
        croissantdealer.make_move(move)

        response = requests.post(f"{self.url}/api/bot/game/{game_id}/move/{move}", headers=headers)
        if response.status_code != 200:
            logs.error(f"Something went wrong while making the move, here is the error: {response.text}")

    def handle_game_stream(self, game_id: str, color: str, fen: str):
        # spin up the croissantdealer engine
        croissantdealer = Croissantdealer(color=color, fen=fen)

        chat = self.get_chat(game_id=game_id)
        if not chat:
            self.send_message(game_id=game_id, text="Hi! :) Send '?help' for the list of all commands "
                                                    "and their's description. Checkout my bio for the "
                                                    "link to the github repo!")

        # connect to the game stream
        response = requests.get(f'{self.url}/api/bot/game/stream/{game_id}', headers=self.headers, stream=True)

        for line in response.iter_lines():
            # filter out keep-alive new lines
            if line:
                logs.info("Received a event! (game)")

                decoded_line = line.decode('utf-8')
                json_data = json.loads(decoded_line)

                # process the events here
                # check if we need to make a move
                try:
                    if json_data["status"] == "mate":
                        if json_data["winner"].lower() == color:
                            logs.info(f"game with an id of {game_id} has ended! We won :)")
                            self.send_message(game_id=game_id, text="gg's! :)")
                        else:
                            logs.info(f"game with an id of {game_id} has ended! We lost :P")
                            self.send_message(game_id=game_id, text="Well, I'm pretty sure that i was "
                                                                    "close to winning :P. gg's! :)")

                        return
                except KeyError:
                    pass

                if croissantdealer.our_move():
                    # calculate the move to make
                    move = croissantdealer.get_move()[0]
                    self.play_move(game_id=game_id, move=str(move), croissantdealer=croissantdealer)
                else:
                    try:
                        if croissantdealer.get_uci() != json_data["moves"]:
                            # make the move on croissantdealer's board
                            croissantdealer.make_move(f'{json_data["moves"].split(" ")[-1]}')

                            # calculate the move to make
                            move = croissantdealer.get_move()[0]
                            self.play_move(game_id=game_id, move=str(move), croissantdealer=croissantdealer)
                    except KeyError as e:
                        # check if the event is a chat message
                        if json_data["type"] == "chatLine":
                            if json_data["text"] in self.command_list:
                                self.commands(game_id=game_id, text=json_data["text"], croissantdealer=croissantdealer)

    def start_game(self, game_id: str, color: str, fen: str):
        """starts playing a game"""
        # create a thread for the game stream
        game_thread = threading.Thread(target=self.handle_game_stream, args=(game_id, color, fen))
        game_thread.start()

    def accept_game(self, game_id: str):
        """accepts a game"""

        # accept a game
        response = requests.post(f"{self.url}/api/challenge/{game_id}/accept", headers=self.headers)
        if response.status_code == "200":
            logs.info(f"Successfully started a game with id of: {game_id}")
            active_games.append(game_id)
        else:
            logs.error(f"Something went wrong while trying to start a game with an id of {game_id}, here is the error: "
                       f"{response.text}")

    def reject_game(self, game_id: str, reason: str, reason_to_send: str = "later"):
        # available options are listed here: https://lichess.org/api#tag/Challenges/operation/challengeDecline
        data = {"reason": reason_to_send}

        response = requests.post(f'{self.url}/api/challenge/{game_id}/decline', headers=self.headers, data=data)
        if response.status_code == 200:
            logs.info(f"Successfully rejected challenge with an id of: '{game_id}', because {reason}")
        else:
            logs.error(f"Failed to reject a challenge with an id of: '{game_id}'. Here is the error: {response.text}")

    def resign(self, game_id: str):
        """resign a given game"""
        response = requests.post(f'{self.url}/api/bot/game/{game_id}/resign', headers=self.headers)
        if response.status_code == 200:
            logs.info(f"Successfully resigned in a challenge with an id of: '{game_id}'")
        else:
            logs.error(f"Failed to resign in a challenge with an id of: '{game_id}'. Here is the error: {response.text}")

    def send_message(self, game_id: str, text: str, room: str = "player"):
        """send a message in a game's chat"""
        data = {
            "room": f"{room}",
            "text": f"{text}"
        }

        response = requests.post(f'{self.url}/api/bot/game/{game_id}/chat', headers=self.headers, data=data)
        if response.status_code == 200:
            logs.info(f"Successfully send a message in the chat of a challenge with an id of: '{game_id}'")
        else:
            logs.error(f"Failed to send a message in the chat of a challenge with an id of: "
                       f"'{game_id}'. Here is the error: {response.text}")

    def get_chat(self, game_id: str):
        """get chat of a game"""
        response = requests.get(f'{self.url}/api/bot/game/{game_id}/chat', headers=self.headers)
        if response.status_code == 200:
            logs.info(f"Successfully got the chat of a challenge with an id of: '{game_id}'")
            return response.json()
        else:
            logs.error(f"Failed to get the chat of a challenge with an id of: "
                       f"'{game_id}'. Here is the error: {response.text}")

            return 1

    def commands(self, game_id: str, croissantdealer: Croissantdealer, text: str = "?help"):
        defined_commands = {
            "?help": "Available commands: "
                     "1. ?help - displays this message "
                     "2. ?eval - displays the bot evaluation of the current position",
            "?eval": "(+ = white, - = black, 0 = draw) This is the current evaluation of the position:"
        }

        match text:
            case "?help":
                self.send_message(game_id=game_id, text=defined_commands["?help"])
            case "?eval":
                move, evaluation = croissantdealer.get_move()
                self.send_message(game_id=game_id, text=f"{defined_commands['?eval']} {evaluation}. "
                                                        f"Best move ( in my opinion :) ): {str(move)}.")


# initialize the logs
logs = Logger(timezone="Europe/Warsaw")

if not verbose:
    verbose = False
    logs.info("'verbose' variable is set to False! The bot will not be very talkative, "
              "you can change it by setting 'verbose=True' in the secrets.env")

# initialize the bot
bot = Lichess(token=token, headers=headers, url=url, environment=environment, verbose=verbose)

# login
stream = bot.login()
if stream.status_code == 200:
    logs.info("🚀 The bot is active! Waiting for events..")

    thread = threading.Thread(target=bot.handle_event_stream, args=(stream, ))
    thread.start()
else:
    logs.error(f"Someting went wrong while trying to start the bot. Here is the error: {stream.text}")