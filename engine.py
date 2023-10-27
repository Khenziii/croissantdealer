import chess
import random

class Engine:
    """The setup for the braining thing"""
    def __init__(self, color: str) -> None:
        self.board = chess.Board()
        self.color = color
        self.values = {
            "pawn": 1,
            "rook": 5,
            "knight": 3,
            "bishop": 3,
            "queen": 9
        }
        self.transposition_table = {}

    def new_board(self) -> None:
        """Resets the board"""
        self.board = chess.Board()

    def our_move(self, board: chess.Board = None):
        """returns True if our move and False if theirs"""
        if not board:
            board = self.board

        if board.turn == chess.WHITE and self.color.lower() == "white":
            return True
        if board.turn == chess.BLACK and self.color.lower() == "black":
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

    def get_legal_moves(self, board: chess.Board = None):
        """return the list of all legal moves"""
        if not board:
            board = self.board

        return list(board.legal_moves)

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

    def get_move(self, board: chess.Board = None, depth: int = 3) -> list[chess.Move | int]:
        """Calculate the move to make"""
        if not board:
            board = self.board

        # initialize some variables
        best_moves = []

        # use the minimax function to evaluate deeply every move
        moves = self.get_legal_moves(board=board)

        # set the temporary best_eval
        if self.color == "white":
            best_eval = -10000
        else:
            best_eval = 10000

        # loop through each legal move
        for move in moves:
            # create a copy of the original board
            temp_board = board.copy()
            # play the random move
            temp_board.push(move)

            # evaluate the moves (with depth, using minimax)
            if self.color == "white":
                # get the eval of the line
                best_move_eval_minimax = self.minimax(board=temp_board, depth=depth-1, alpha=-10000, beta=10000,
                                                      maximizing=False)

                # if the line is better than our current best one, replace the current one
                if best_move_eval_minimax > best_eval:
                    best_eval = best_move_eval_minimax
                    best_moves = [move]
                elif best_move_eval_minimax == best_eval:
                    # if the line is as good as our current one, add it to the possible moves list
                    best_moves.append(move)
            elif self.color == "black":
                # get the eval of the line
                best_move_eval_minimax = self.minimax(board=temp_board, depth=depth-1, alpha=-10000, beta=10000,
                                                      maximizing=True)

                # if the line is better than our current best one, replace the current one
                if best_move_eval_minimax < best_eval:
                    best_eval = best_move_eval_minimax
                    best_moves = [move]
                elif best_move_eval_minimax == best_eval:
                    # if the line is as good as our current one, add it to the possible moves list
                    best_moves.append(move)

        # get a random move from the equally best moves
        best_move = random.choice(best_moves)

        return [best_move, best_eval]

    def minimax(self, board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool):
        if not board:
            board = self.board

        # if reached the end of the line, return the evaluation
        if depth <= 0 or board.is_game_over():
            return self.evaluate(board=board)

        if maximizing:
            max_eval = -100000

            moves = self.get_legal_moves(board=board)
            for move in moves:
                # create a copy of the current board
                temp_board = board.copy()
                # play a move on the copied board
                temp_board.push(move)

                eval = self.minimax(board=temp_board, depth=depth-1, alpha=alpha, beta=beta, maximizing=False)
                max_eval = max(max_eval, eval)

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 10000

            moves = self.get_legal_moves(board=board)
            for move in moves:
                # create a copy of the current board
                temp_board = board.copy()
                # play a move on the copied board
                temp_board.push(move)

                eval = self.minimax(board=temp_board, depth=depth-1, alpha=alpha, beta=beta, maximizing=True)
                min_eval = min(min_eval, eval)

                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate(self, board: chess.Board):
        # check if we have already evaluated this board
        if board.fen() in self.transposition_table:
            return self.transposition_table[board.fen()]

        # if the board is checkmate
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return -10000
            else:
                return 10000

        # if the position is a draw
        if board.is_stalemate():
            # stalemate
            return 0
        elif board.is_insufficient_material():
            # insufficient material to mate
            return 0
        elif board.can_claim_threefold_repetition():
            # threefold repetition
            return 0
        elif board.can_claim_fifty_moves():
            # the 50 moves rule
            return 0

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

        evaluation = worthiness_white - worthiness_black

        # save the evaluation to the transposition table
        self.transposition_table[board.fen()] = evaluation

        return evaluation
