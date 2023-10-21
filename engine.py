import chess
import random


class Croissantdealer:
    """The braining thing"""
    def __init__(self, color: str) -> None:
        self.board = chess.Board()
        self.game_just_started = True
        self.color = color

    def new_board(self) -> None:
        """Resets the board"""
        self.board = chess.Board()

    def our_move(self):
        """returns True if our move and False if their's"""
        if self.board.turn == chess.WHITE and self.color.lower() == "white":
            return True
        if self.board.turn == chess.BLACK and self.color.lower() == "black":
            return True

        return False

    def make_move(self, move: str):
        """update the board to match a made move"""
        self.board.push_uci(move)

    def get_uci(self):
        """get the current board in UCI"""
        uci_string = ""
        for move in self.board.move_stack:
            uci_string += f" {move.uci()}"
        
        # there is a space at the start, lets get rid of it
        uci_string = uci_string.strip()

        return uci_string

    def get_legal_moves(self):
        """return the list of all legal moves"""
        return list(self.board.legal_moves)

    def get_move(self):
        """calculate the move to make"""
        moves = self.get_legal_moves()

        # check if not mate

        # return a random move (for now :>)
        random_index = random.randint(0, len(moves)-1)
        return moves[random_index]