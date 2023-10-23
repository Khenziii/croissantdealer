import chess
import random

class Engine:
    """The setup for the braining thing"""
    def __init__(self, color: str) -> None:
        self.board = chess.Board()
        self.game_just_started = True
        self.color = color
        self.values = {
            "pawn": 1,
            "rook": 5,
            "knight": 3,
            "bishop": 3,
            "queen": 9
        }

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

    def get_pieces(self, board: chess.Board):
        """returns the list of all pieces"""
        pieces = {
            "white": {
                "pawns": 0,
                "rooks": 0,
                "knights": 0,
                "bishops": 0,
                "queens": 0
            },
            "black": {
                "pawns": 0,
                "rooks": 0,
                "knights": 0,
                "bishops": 0,
                "queens": 0
            }
        }

        for square, piece in board.piece_map().items():
            if piece.color == chess.WHITE:
                match piece.piece_type:
                    case chess.PAWN:
                        pieces["white"]["pawns"] += 1
                    case chess.ROOK:
                        pieces["white"]["rooks"] += 1
                    case chess.KNIGHT:
                        pieces["white"]["knights"] += 1
                    case chess.BISHOP:
                        pieces["white"]["bishops"] += 1
                    case chess.QUEEN:
                        pieces["white"]["queens"] += 1
            else:
                match piece.piece_type:
                    case chess.PAWN:
                        pieces["black"]["pawns"] += 1
                    case chess.ROOK:
                        pieces["black"]["rooks"] += 1
                    case chess.KNIGHT:
                        pieces["black"]["knights"] += 1
                    case chess.BISHOP:
                        pieces["black"]["bishops"] += 1
                    case chess.QUEEN:
                        pieces["black"]["queens"] += 1

        return pieces

    # methods that get inherited (by the Croissantdealer class) are defined below
    def get_move(self):
        pass

    def evaluate(self, board: chess.Board):
        pass


class Croissantdealer(Engine):
    """The braining thing"""
    def get_move(self):
        """calculate the move to make"""
        moves = self.get_legal_moves()

        # return the move with highest evaluation
        best_moves = []
        best_move_eval = -1000

        for move in moves:
            temp_board = self.board.copy()
            temp_board.push(move)

            eval = self.evaluate(temp_board)
            if eval > best_move_eval:
                best_move_eval = eval
                best_moves = [move]
            elif eval == best_move_eval:
                best_moves.append(move)

        # get a random move from the moves that had the same highest eval
        best_move = best_moves[random.randint(0, len(best_moves)-1)]

        return best_move

    def evaluate(self, board: chess.Board):
        pieces = self.get_pieces(board=board)

        worthiness_white = 0
        worthiness_black = 0

        # calculate the worthiness of white
        for piece in pieces["white"].keys():
            match piece:
                case "pawns":
                    worthiness_white += pieces["white"]["pawns"] * self.values["pawn"]
                case "rooks":
                    worthiness_white += pieces["white"]["rooks"] * self.values["rook"]
                case "knights":
                    worthiness_white += pieces["white"]["knights"] * self.values["knight"]
                case "bishops":
                    worthiness_white += pieces["white"]["bishops"] * self.values["bishop"]
                case "queens":
                    worthiness_white += pieces["white"]["queens"] * self.values["queen"]

        # calculate the worthiness of black
        for piece in pieces["black"].keys():
            match piece:
                case "pawns":
                    worthiness_black += pieces["black"]["pawns"] * self.values["pawn"]
                case "rooks":
                    worthiness_black += pieces["black"]["rooks"] * self.values["rook"]
                case "knights":
                    worthiness_black += pieces["black"]["knights"] * self.values["knight"]
                case "bishops":
                    worthiness_black += pieces["black"]["bishops"] * self.values["bishop"]
                case "queens":
                    worthiness_black += pieces["black"]["queens"] * self.values["queen"]

        evaluation = 0
        if self.color == "white":
            evaluation = worthiness_white - worthiness_black
        elif self.color == "black":
            evaluation = worthiness_black - worthiness_white

        return evaluation
