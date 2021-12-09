import random
from typing import Callable, Optional
from itertools import cycle


class BoardLockedError(Exception):
    def __init__(self, board_index) -> None:
        super().__init__(f'Board {board_index} is not possible to choose')


class SpotOccupiedError(Exception):
    def __init__(self, spot_index):
        super().__init__(f'Spot {spot_index} is already occupied')


class InputError(Exception):
    def __init__(self, given_input):
        super().__init__(given_input)


class BoardChoiceError(Exception):
    def __init__(self, message):
        super().__init__(message)


class GameRulesError(Exception):
    def __init__(self, message):
        super().__init__(message)


def elements_equal(elements_list: list):
    return elements_list.count(elements_list[0]) == len(elements_list)


class LocalBoard():
    """
    Class LocalBoard. Enables playing on it as a normal tic-tac-toe:
    :param  _spots: 9 spots available to put "o" or "x" sign in
    :type   _spots: list of strings
    :param  _win:   Indicates if any player has already won this board
    :type   _win:   None/boolean
    :param  _full:  Indicates if the board is full
    :type   _full:  boolean
    """

    def __init__(self, size):
        self._spots: list = size ** 2 * ['']
        self._win = None
        self._full = False

        if size <= 0:
            raise ValueError("Size must be positive.")
        self._SIZE = size

    def spot(self, spot_index):
        if not (1 <= spot_index <= self._SIZE ** 2):
            raise IndexError("Wrong spot index")
        return self._spots[spot_index - 1]

    def set_spot(self, spot_index, spot_value):
        if not (1 <= spot_index <= self._SIZE ** 2):
            raise IndexError("Wrong spot index")
        if 'x' != spot_value != 'o':
            raise ValueError("Wrong spot value")
        self._spots[spot_index - 1] = spot_value

    def win(self):
        return self._win

    def if_move_possible(self, lock_after_win):
        return not (self._full or self._win and lock_after_win)

    def possible_moves(self, lock_after_win):
        if self._win and lock_after_win or self._full:
            return []

        empty_spots = []
        for index, spot in enumerate(self._spots):
            if not spot:
                empty_spots.append(index + 1)

        return empty_spots

    def make_move(self, spot_index, sign):
        """Allows making move on local board. Returns local_win_check()"""
        if not 1 <= spot_index <= self._SIZE ** 2:
            raise IndexError("Wrong spot index")
        if 'x' != sign != 'o':
            raise ValueError("Wrong spot sign")
        if self.spot(spot_index):
            raise SpotOccupiedError(spot_index)

        self.set_spot(spot_index, spot_value=sign)

        self.full_check()
        return self.local_win_check()

    def local_win_check(self):
        """Checks for a win and sets _win attribute if needed.
        Returns the player who won in the last turn, otherwise False"""
        # someone could already win the board
        if self._win:
            return None

        size = self._SIZE
        for i in range(size):
            # horizonally
            hor_line = [
                spot for spot in self._spots[(i * size):((i + 1) * size)]]
            if hor_line[0] and elements_equal(hor_line):
                self._win = hor_line[0]

            # vertically
            ver_line = [spot for spot in self._spots[i::size]]
            if ver_line[0] and elements_equal(ver_line):
                self._win = ver_line[0]

        # diagonally left (\)
        diagonal_left = [spot for spot in self._spots[::(size + 1)]]
        if diagonal_left[0] and elements_equal(diagonal_left):
            self._win = diagonal_left[0]

        # diagonally right (/)
        diagonal_right = [
            spot for spot in self._spots[(size - 1):(size ** 2 - 1):(size - 1)]
        ]
        if diagonal_right[0] and elements_equal(diagonal_right):
            self._win = diagonal_right[0]

        return self.win()

    def full_check(self):
        self._full = all(self._spots)
        return self._full

    def row_str(self, row, sep, highlight=None):
        size = self._SIZE
        if not 0 <= row < size:
            raise IndexError("Wrong row index")

        spots_to_show = [
            spot for spot in self._spots[(row * size):((row + 1) * size)]]
        formated_spots = [f'{x:1}' for x in spots_to_show]

        if highlight is not None:
            if not 0 <= highlight < size:
                raise IndexError("Wrong highlight index")
            formated_spots[highlight] = formated_spots[highlight].upper()

        return ' ' + f' {sep} '.join(formated_spots) + ' '

    def __eq__(self, other):
        return self._spots == other._spots and self._win == other._win and \
            self._full == other._full and self._SIZE == other._SIZE


class GlobalBoard:
    """
    Class GlobalBoard. Enables playing ultimate tic-tac-toe. Contains 9 boards
    :param  _local_boards:      9 local boards
    :type   _local_boards:      list of LocalBoard objects
    :param  _LOCK_AFTER_WIN:    Constant indicating if playing
        on a local board is locked after one of the players
        has won but not all spots are occupied
    :type   _LOCK_AFTER_WIN:    boolean
    :param  _previous_spot_idx:     Spot index on which last move was made
    :type   _previous_spot_idx:     int/None
    :param  _previous_spot_idx:     Local board index on which last move was made
    :type   _previous_spot_idx:     int/None
    """

    def __init__(self, size, lock_after_win, choice_after_win):
        self._local_boards = []
        for _ in range(size ** 2):
            self._local_boards.append(LocalBoard(size))
        self._LOCK_AFTER_WIN = lock_after_win
        self._CHOICE_AFTER_WIN = choice_after_win
        self._previous_spot_idx = None
        self._previous_board_idx = None
        self._board_choice = None
        self._last_won = False
        self._SIZE = size

        # strings used for displaying
        # HOR_SEP = '-'
        self.HOR_SEP_2 = '-'
        self.VER_SEP = ':'
        self.VER_SEP_2 = '|'
        self.HL = '#'

    def local_board(self, local_board_index) -> LocalBoard:
        if not (1 <= local_board_index <= self._SIZE ** 2):
            raise IndexError("Wrong board index")
        return self._local_boards[local_board_index - 1]

    def current_board(self):
        """
        Returns the next local board index on which game should be going
        Returns None if player should have board choice
        """
        if self._previous_spot_idx is None:
            return None

        if not 1 <= self._previous_spot_idx <= self._SIZE ** 2:
            raise IndexError("Wrong last spot")

        potential_next_boad = self.local_board(self._previous_spot_idx)
        if not potential_next_boad.if_move_possible(self._LOCK_AFTER_WIN):
            return None

        if self._last_won and self._CHOICE_AFTER_WIN:
            return None

        return self._previous_spot_idx

    def row_clmn_split(self, index):
        """
        Splits spot/board index into row and column indexes
        """
        if index is None:
            return None, None
        if not (1 <= index <= self._SIZE ** 2):
            raise IndexError("Wrong index to split")
        index -= 1
        return index // self._SIZE, index % self._SIZE

    def last_move_highlight(self, row_9, clmn_3):
        """
        Checks if there is spot of the last move to highlight
        in a given position. If yes, returns its row_str position.
        """
        if self._previous_spot_idx is None or self._previous_board_idx is None:
            return None

        size = self._SIZE
        if not (0 <= row_9 < size ** 2 and 0 <= clmn_3 < size):
            raise IndexError("Wrong row or column indexes")

        same_board = (self._previous_board_idx - 1) == \
            (row_9 // size) * size + clmn_3
        same_spot = (self._previous_spot_idx - 1) // size == \
            row_9 % size

        if same_board and same_spot:
            return (self._previous_spot_idx - 1) % size
        return None

    def compare(self, value, model_value, epsilon=0.5):
        """
        Returns True if two given values differ less than epsilon
        """
        return abs(value - model_value) <= epsilon

    def separator_row(self, highlight=None):
        """
        Returns a string of a horizontal line separating local boards.
        Some of its parts can be highlighted.
        """
        size = self._SIZE
        sep_str = ''
        for clmn in range(size + 1):
            # Vertical sign
            if highlight is not None and \
                    self.compare(clmn, highlight + 0.5):
                sep_str += self.HL
            else:
                sep_str += self.VER_SEP_2

            if clmn == size:
                break

            # Sequence of horizontal signs
            if highlight is not None and \
                    clmn == highlight:
                sep_str += (4 * size - 1) * self.HL
            else:
                sep_str += (size - 1) * (3 * self.HOR_SEP_2 + self.VER_SEP)
                sep_str += 3 * self.HOR_SEP_2
        return sep_str

    def row_of_spots(self, row, highlight=None):
        """
        Returns particular row of all boards in one row.
        Some parts can be highlighted.
        """
        size = self._SIZE
        row_str = ''
        for clmn in range(size + 1):
            # local boards borders
            if highlight is not None and \
                    self.compare(clmn, highlight + 0.5):
                row_str += self.HL
            else:
                row_str += self.VER_SEP_2

            if clmn == size:
                break

            if_last_move_highlight = self.last_move_highlight(row, clmn)
            local_board_str = self.local_board(
                (row // size) * size + clmn + 1).row_str(
                    row % size, self.VER_SEP, if_last_move_highlight)
            row_str += local_board_str
        return row_str

    def row_of_wins(self, row_index):
        size = self._SIZE
        row_str = ''
        for i in range(size + 1):
            # separator
            row_str += self.VER_SEP

            if i == size:
                break

            # sign of win
            win_status = self.local_board(size * row_index + i + 1).win()
            row_str += win_status if win_status else ' '
        return row_str

    def map_of_wins(self):
        size = self._SIZE
        def separator(sep): return (2 * size + 1) * sep
        final_str = ''

        # separator
        final_str += separator('_') + '\n'

        # rows of wins
        for i in range(size):
            final_str += self.row_of_wins(i)
            final_str += '\n'

        # separator
        final_str += separator('^')
        return final_str

    def __str__(self) -> str:
        """
        Prints global board and highlits one of the local boards if needed.
        """
        if self._board_choice is None:
            highlight = self.current_board()
        else:
            highlight = self._board_choice

        highlight_row, highlight_clmn = self.row_clmn_split(highlight)

        size = self._SIZE
        final_str = ''
        # {size} rows of local boards
        for row in range(size + 1):
            # Thick horizontal line
            if highlight and \
                    self.compare(row, highlight_row + 0.5):
                final_str += self.separator_row(highlight_clmn)
            else:
                final_str += self.separator_row()
            final_str += '\n'

            if row == size:
                break

            for local_row in range(size):
                if highlight and \
                        row == highlight_row:
                    final_str += self.row_of_spots(
                        size * row + local_row, highlight_clmn)
                else:
                    final_str += self.row_of_spots(
                        size * row + local_row)
                final_str += '\n'

        # map of wins
        final_str += self.map_of_wins()
        return final_str

    def possible_boards(self):
        """
        Returns a list of local boards indexes
        on which making a move is still possible
        """
        boards_indexes = []
        for index, board in enumerate(self._local_boards):
            if board.if_move_possible(self._LOCK_AFTER_WIN):
                boards_indexes.append(index + 1)

        return boards_indexes

    def choose_board(self, board_index):
        if not 1 <= board_index <= self._SIZE ** 2:
            raise IndexError("Invalid board index")

        board_should_be_chosen = self.current_board() is None
        board_already_chosen = bool(self._board_choice)

        if not board_should_be_chosen or board_already_chosen:
            raise BoardChoiceError('Player not permitted to choose the board')

        if board_index not in self.possible_boards():
            raise BoardLockedError(board_index)

        self._board_choice = board_index

    def save_last_move(self, spot_index, board_index):
        self._previous_spot_idx = spot_index
        self._previous_board_idx = board_index

    def make_move(self, sign, spot_index):
        if 'x' != sign != 'o':
            raise ValueError("Invalid sign")
        if not 1 <= spot_index <= self._SIZE ** 2:
            raise IndexError("Invalid spot index")

        if self.current_board() is None and self._board_choice is None:
            raise BoardChoiceError('Attmept to make move without board chosen')

        # set board_choice
        board_index = self.current_board()
        if board_index is None:
            board_index = self._board_choice

        # make actual move
        previous_board: LocalBoard = self.local_board(board_index)
        self._last_won = previous_board.make_move(spot_index, sign)

        self.save_last_move(spot_index, board_index)
        self._board_choice = None
        return self.global_win_check()

    def global_win_check(self):
        """Checks for win in global board.
        Returns a sign of the winnin player, draw or None"""
        size = self._SIZE
        for i in range(size):
            # horizonally
            hor_line = [
                board.win() for board
                in self._local_boards[(i * size):((i + 1) * size)]
            ]
            if hor_line[0] and elements_equal(hor_line):
                return hor_line[0]

            # vertically
            ver_line = [
                board.win() for board
                in self._local_boards[i::size]
            ]
            if ver_line[0] and elements_equal(ver_line):
                return ver_line[0]

        # diagonally left (\)
        diagonal_left = [
            board.win() for board
            in self._local_boards[::(size + 1)]
        ]
        if diagonal_left[0] and elements_equal(diagonal_left):
            return diagonal_left[0]

        # diagonally right (/)
        diagonal_right = [
            board.win() for board
            in self._local_boards[(size - 1):(size ** 2 - 1):(size - 1)]]
        if diagonal_right[0] and elements_equal(diagonal_right):
            return diagonal_right[0]

        if self.possible_boards():
            return None

        # no win and no boards possible to make move
        return 'draw'

    def if_first_turn(self):
        return self._previous_spot_idx is None

    def __eq__(self, other) -> bool:
        return self._local_boards == other._local_boards and            \
            self._LOCK_AFTER_WIN == other._LOCK_AFTER_WIN and           \
            self._CHOICE_AFTER_WIN == other._CHOICE_AFTER_WIN and       \
            self._previous_spot_idx == other._previous_spot_idx and     \
            self._previous_board_idx == other._previous_board_idx and   \
            self._board_choice == other._board_choice and               \
            self._last_won == other._last_won and                       \
            self._SIZE == other._SIZE


class UltimateTicTacToe:
    def __init__(self, size, lock_after_win, choice_after_win):
        if size <= 1:
            raise ValueError("Size must equal at lest 2")
        self._board = GlobalBoard(size, lock_after_win, choice_after_win)

    def global_board(self):
        return self._board

    def get_input(self):
        """
        Constantly takes input from user
        unless correct one is given.
        """
        while True:
            given_input = input('> ')
            if not given_input.isdigit():
                raise InputError(given_input)
            if not 1 <= int(given_input) <= self._board._SIZE ** 2:
                raise InputError(given_input)

            return given_input

    def player(self, sign):

        # let user choose the local board
        if self.global_board().current_board() is None:
            print(self.global_board())

            while True:
                print(sign, "Choose the local board")
                try:
                    board_choice = int(self.get_input())
                except InputError:
                    print(self.global_board())
                    print("Wrong board. Try again")
                    continue

                try:
                    self.global_board().choose_board(board_choice)
                    break
                except BoardLockedError:
                    print(self.global_board())
                    print("Wrong board. Try again")
                    continue

        print(self.global_board(), '\n')

        while True:
            print(sign, "Choose the spot")
            try:
                # choosing the spot
                spot_choice = int(self.get_input())

                # making actual move
                return self.global_board().make_move(sign, spot_choice)
            except InputError:
                print(self.global_board())
                print("Wrong spot. Try again.")
                continue
            except SpotOccupiedError:
                print(self.global_board())
                print("This spot is already occupied. Try another one.")
                continue

    def random_bot(self, sign):
        """
        Bot designed to make random decisions.
        """
        # randomly choose another local board
        board_choice = self.global_board().current_board()
        if board_choice is None:
            possible_boards = self.global_board().possible_boards()
            board_choice = random.choice(possible_boards)
            self.global_board().choose_board(board_choice)

        # randomly choose spot in chosen local board
        chosen_board = self.global_board().local_board(board_choice)
        possible_spots = chosen_board.possible_moves(
            self.global_board()._LOCK_AFTER_WIN)
        spot_choice = random.choice(possible_spots)

        # making actual move
        return self.global_board().make_move(sign, spot_choice)

    def always_winning_bot(self, sign):
        global_board = self.global_board()

        def mirror_board(board_index):
            return 10 - board_index

        # Game rule checks
        if global_board._LOCK_AFTER_WIN or \
                global_board._CHOICE_AFTER_WIN:
            raise GameRulesError(
                "LOCK_AFTER_WIN and CHOICE_AFTER_WIN must be both disabled "
                "in order to run always_winning_bot")
        if not global_board._SIZE == 3:
            raise GameRulesError(
                "Board size must equal 3 "
                "in order to run always_winning_bot")

        # first turn
        if getattr(self, 'turn_count', None) is None:
            # Bot not starting the game
            if not global_board.if_first_turn():
                raise GameRulesError(
                    "Always_winning_bot must start "
                    "in order to always win")

            # setting turn_count attribute
            setattr(self, 'turn_count', 1)

            global_board.choose_board(5)

        # print(global_board)
        # initial part of the game
        if self.turn_count <= 8:
            self.turn_count += 1
            return global_board.make_move(sign, 5)

        # setting sacrificed_board
        if getattr(self, 'sacrificed_board', None) is None:
            setattr(
                self, 'sacrificed_board',
                global_board.current_board())

        # choosing board
        if global_board.current_board() is None:
            global_board.choose_board(mirror_board(self.sacrificed_board))

        try:
            return global_board.make_move(
                sign, self.sacrificed_board)
        except SpotOccupiedError:
            return global_board.make_move(
                sign, mirror_board(self.sacrificed_board))

    def play(self, player_1: Callable[[str], Optional[str]],
             player_2: Callable[[str], int]):

        players = [(player_1, 'x'), (player_2, 'o')]
        for player_method, sign in cycle(players):
            result = player_method(sign)
            # print(self.global_board())
            if result:
                print(self.global_board())
                if result == 'draw':
                    print("Draw.")
                else:
                    print(f'{result} won.')
                return result


def main():
    # x_wins = 0
    # o_wins = 0
    # for i in range(100):
    #     game = UltimateTicTacToe(3, False, False)
    #     result = game.play(game.always_winning_bot, game.random_bot)
    #     if result == 'x':
    #         x_wins += 1
    #     if result == 'o':
    #         o_wins += 1
    # print(x_wins, o_wins, 100 - x_wins - o_wins)

    game = UltimateTicTacToe(3, False, False)
    game.play(game.always_winning_bot, game.player)


if __name__ == '__main__':
    main()
