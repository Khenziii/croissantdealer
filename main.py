import requests
from dotenv import load_dotenv
import os
import threading
import json
from datetime import datetime, timedelta, timezone

from engine import Croissantdealer

# define stuff
# get the token from secrets.env
# load all of the variables from secrets.env into python environment
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


def get_current_time(hours):
    """returns the current time in string format"""
    sum_time = timezone(timedelta(hours=hours))
    current_datetime = datetime.now(sum_time)

    return current_datetime.strftime(f"%d/%m/%y - %H:%M:%S")


class Logger:
    """
    Logs stuff

    :param timezone_hours: The amount of hours forward in UTC (eg. timezone: 2 = UTC+2)
    """

    def __init__(self, timezone_hours: int):
        self.timezone_hours = timezone_hours

    def info(self, msg: str):
        print(f"[i] {get_current_time(self.timezone_hours)} > {msg}")

    def warning(self, msg: str):
        print(f"[w] {get_current_time(self.timezone_hours)} > {msg}")

    def error(self, msg: str):
        print(f"[e] {get_current_time(self.timezone_hours)} > {msg}")


class Lichess:
    """Talk with Lichess's API"""

    def __init__(self, token: str, headers: dict, url: str, environment: str, verbose: bool = False) -> None:
        self.token = token
        self.headers = headers
        self.url = url
        self.environment = environment
        self.verbose = verbose

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

                    if challenge_variant.lower() == "standard":
                        if not challenge_rated:
                            if environment != "DEVELOPMENT":
                                self.start_game(challenge_id, our_color)
                            else:
                                if sender_username == dev_username:
                                    self.start_game(challenge_id, our_color)
                                else:
                                    self.reject_game(game_id=challenge_id,
                                                     reason=f"we're in dev environment, and the user isn't {dev_username}")
                        else:
                            self.reject_game(game_id=challenge_id, reason=f"the sender tried to play a ranked game", reason_to_send="casual")
                    else:
                        self.reject_game(game_id=challenge_id, reason=f"it didn't contain the correct variant", reason_to_send="standard")

    def play_move(self, game_id: str, move: str, croissantdealer: Croissantdealer):
        croissantdealer.make_move(move)

        response = requests.post(f"{self.url}/api/bot/game/{game_id}/move/{move}", headers=headers)
        if response.status_code != 200:
            logs.error(f"Something went wrong while making the move, here is the error: {response.text}")

    def handle_game_stream(self, game_id: str, color: str):
        # spin up the croissantdealer engine
        croissantdealer = Croissantdealer(color=color)

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
                        # send a "Good Game!" in the chat here later :)
                        if json_data["winner"].lower() == color:
                            logs.info(f"game with an id of {game_id} has ended! We won :)")
                        else:
                            logs.info(f"game with an id of {game_id} has ended! We lost :P")

                        return
                except KeyError:
                    pass

                if croissantdealer.our_move():
                    move = croissantdealer.get_move()
                    self.play_move(game_id=game_id, move=str(move), croissantdealer=croissantdealer)
                else:
                    try:
                        if croissantdealer.get_uci() != json_data["moves"]:
                            croissantdealer.make_move(f'{json_data["moves"].split(" ")[-1]}')

                            move = croissantdealer.get_move()
                            self.play_move(game_id=game_id, move=str(move), croissantdealer=croissantdealer)
                    except KeyError as e:
                        logs.info("lichess send us stuff that is not a move!")

    def start_game(self, game_id: str, color: str):
        # start the game
        response = requests.post(f"{self.url}/api/challenge/{game_id}/accept", headers=self.headers)
        if response.status_code == "200":
            logs.info(f"Successfully started a game with id of: {game_id}")
            active_games.append(game_id)
        else:
            logs.error(f"Something went wrong while trying to start a game with an id of {game_id}, here is the error: {response.text}")

        game_thread = threading.Thread(target=self.handle_game_stream, args=(game_id, color))
        game_thread.start()

    def reject_game(self, game_id: str, reason: str, reason_to_send: str = "later"):
        # avaible options are listed here: https://lichess.org/api#tag/Challenges/operation/challengeDecline
        data = {"reason": reason_to_send}

        response = requests.post(f'{self.url}/api/challenge/{game_id}/decline', headers=self.headers, data=data)
        if response.status_code == 200:
            logs.info(f"Successfully rejected challenge with an id of: '{game_id}', because {reason}")
        else:
            logs.error(f"Failed to reject a challenge with an id of: '{game_id}'. Here is the error: {response.text}")

    def resign(self, game_id: str):
        ...

    def send_message(self, game_id: str):
        ...

    def get_chat(self, game_id: str):
        ...


# initialize the logs
logs = Logger(timezone_hours=2)

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