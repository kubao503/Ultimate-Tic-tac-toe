from ultimate_tic_tac_toe import (
    LocalBoard,
    GlobalBoard,
    UltimateTicTacToe,
    SpotOccupiedError,
    BoardChoiceError,
    BoardLockedError,
    GameRulesError,
    elements_equal
)
import pytest


# LocalBoard
def test_local_board_constructor():
    local_board_1 = LocalBoard(3)
    assert local_board_1._spots == 9 * ['']
    assert local_board_1._win is None
    assert not local_board_1._full
    assert local_board_1._SIZE == 3

    local_board_1 = LocalBoard(5)
    assert local_board_1._spots == 25 * ['']
    assert local_board_1._SIZE == 5

    with pytest.raises(ValueError):
        LocalBoard(0)


def test_local_board_spot():
    local_board_1 = LocalBoard(4)
    local_board_1._spots[0] = 'x'
    local_board_1._spots[-1] = 'o'

    assert local_board_1.spot(1) == 'x'
    assert local_board_1.spot(16) == 'o'

    with pytest.raises(IndexError):
        local_board_1.spot(0)


def test_local_board_set_spot():
    local_board_1 = LocalBoard(4)
    assert local_board_1.spot(16) == ''

    local_board_1.set_spot(16, 'o')
    assert local_board_1.spot(16) == 'o'

    with pytest.raises(IndexError):
        local_board_1.spot(17)


def test_local_board_win():
    local_board_1 = LocalBoard(3)
    assert local_board_1.win() is None

    local_board_1._win = 'x'
    assert local_board_1.win() == 'x'


def test_local_board_if_move_possible():
    local_board_1 = LocalBoard(3)

    # normal
    assert local_board_1.if_move_possible(False)

    # win
    local_board_1._win = 'x'
    assert local_board_1.if_move_possible(False)
    assert not local_board_1.if_move_possible(True)

    # full
    local_board_1._win = None
    local_board_1._full = True
    assert not local_board_1.if_move_possible(False)


def test_local_board_possible_moves():
    # empty
    local_board_1 = LocalBoard(3)
    assert local_board_1.possible_moves(True) == [x + 1 for x in range(9)]
    local_board_2 = LocalBoard(4)
    assert local_board_2.possible_moves(True) == [x + 1 for x in range(16)]

    # win
    local_board_2._win = 'o'
    assert not local_board_2.possible_moves(True)

    # not empty
    local_board_2.set_spot(1, 'x')
    local_board_2.set_spot(5, 'o')
    moves_indexes = [2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    assert local_board_2.possible_moves(False) == moves_indexes


def test_local_board_make_move():
    local_board_1 = LocalBoard(4)
    assert local_board_1._spots == 16 * ['']

    assert not local_board_1.make_move(1, 'x')
    assert local_board_1._spots == ['x'] + 15 * ['']

    assert not local_board_1.make_move(16, 'o')
    assert local_board_1._spots == ['x'] + 14 * [''] + ['o']

    # local_win_check return
    local_board_1._spots = ['', 'x', 'x', 'x'] + 12 * ['']
    assert local_board_1.make_move(1, 'x') == 'x'

    with pytest.raises(IndexError):
        local_board_1.make_move(0, 'x')
    with pytest.raises(ValueError):
        local_board_1.make_move(3, 'z')
    with pytest.raises(SpotOccupiedError):
        local_board_1.make_move(1, 'x')


def test_local_board_elements_equal():
    list_of_equal_elements = ['x', 'x', 'x', 'x', 'x', 'x']
    list_of_different_elements = ['x', 'x', '', 'x', 'x', 'x']
    assert elements_equal(list_of_equal_elements)
    assert not elements_equal(list_of_different_elements)


def test_local_board_local_win_check():
    # no win
    local_board_1 = LocalBoard(3)
    assert local_board_1.local_win_check() is None
    assert local_board_1.win() is None

    # win
    local_board_1._spots = ['x', '', '', '', 'x', '', 'o', 'o', 'o']
    assert local_board_1.local_win_check() == 'o'
    assert local_board_1.win() == 'o'

    # second win
    local_board_1._spots = ['x', 'x', 'x', '', 'x', '', '', '', 'o']
    assert local_board_1.local_win_check() is None
    assert local_board_1.win() == 'o'

    # no win
    local_board_2 = LocalBoard(4)
    assert local_board_2.local_win_check() is None
    assert local_board_2.win() is None

    local_board_2._spots = 13 * [''] + 3 * ['o']
    assert local_board_2.local_win_check() is None
    assert local_board_2.win() is None

    # win
    local_board_2._spots = 12 * [''] + 4 * ['o']
    assert local_board_2.local_win_check() == 'o'
    assert local_board_2.win() == 'o'

    local_board_3 = LocalBoard(5)
    local_board_3._spots = 5 * (4 * [''] + ['x'])
    assert local_board_3.local_win_check() == 'x'
    assert local_board_3.win() == 'x'


def test_local_board_full_check():
    local_board_1 = LocalBoard(3)
    local_board_1._spots = ['x', '', '', '', '', '', '', 'o', '']
    assert not local_board_1.full_check()
    local_board_1._spots = ['x', 'x', 'o', 'o', 'o', 'x', 'x', 'o', 'x']
    assert local_board_1.full_check()


def test_local_board_row_str():
    local_board_1 = LocalBoard(4)
    local_board_1._spots = ['o', 'x', '', '',
                            'x', 'o', 'x', 'o',
                            ' ', 'x', 'x', 'o',
                            'x', 'o', 'x', 'o']
    assert local_board_1.row_str(0, '|') == ' o | x |   |   '
    assert local_board_1.row_str(1, '|', 0) == ' X | o | x | o '
    assert local_board_1.row_str(2, ':', 0) == '   : x : x : o '
    assert local_board_1.row_str(3, ':', 3) == ' x : o : x : O '

    with pytest.raises(IndexError):
        local_board_1.row_str(-1, '|')
    with pytest.raises(IndexError):
        local_board_1.row_str(4, '|')


def test_local_board_eq():
    local_board_1 = LocalBoard(3)
    local_board_2 = LocalBoard(3)
    assert local_board_1 == local_board_2
    local_board_2._spots[0] = 'x'
    assert not local_board_1 == local_board_2
    assert not LocalBoard(3) == LocalBoard(4)


# GlobalBoard
def test_global_board_constructor():
    global_board_1 = GlobalBoard(4, False, False)
    local_boards = []
    for _ in range(16):
        local_boards.append(LocalBoard(4))
    assert global_board_1._local_boards == local_boards
    assert not global_board_1._LOCK_AFTER_WIN
    assert not global_board_1._CHOICE_AFTER_WIN
    assert global_board_1._previous_spot_idx is None
    assert global_board_1._previous_board_idx is None
    assert global_board_1._board_choice is None
    assert not global_board_1._last_won
    assert global_board_1._SIZE == 4

    global_board_2 = GlobalBoard(5, True, True)
    assert global_board_2._LOCK_AFTER_WIN
    assert global_board_2._CHOICE_AFTER_WIN
    assert global_board_2._SIZE == 5


def test_global_board_local_board():
    global_board_1 = GlobalBoard(5, False, False)
    local_board = global_board_1._local_boards[24]
    assert global_board_1.local_board(25) == local_board

    with pytest.raises(IndexError):
        global_board_1.local_board(0)


def test_global_board_current_board():
    global_board_1 = GlobalBoard(4, False, False)

    # global board is new
    assert global_board_1.current_board() is None

    # normal
    global_board_1._previous_spot_idx = 1
    assert global_board_1.current_board() == 1

    # local board full
    global_board_1.local_board(2)._full = True
    global_board_1._previous_spot_idx = 2
    assert global_board_1.current_board() is None

    # local board won and LOCK_AFTER_WIN
    global_board_2 = GlobalBoard(4, True, False)
    global_board_2._previous_spot_idx = 16
    global_board_2.local_board(16)._win = 'o'
    assert global_board_2.current_board() is None

    # previous board won and CHOICE_AFTER_WIN
    global_board_3 = GlobalBoard(4, False, True)
    global_board_3._previous_spot_idx = 4
    global_board_3.local_board(4)._spots = [
        '', 'x', 'x', 'x'] + 12 * ['']
    global_board_3.make_move('x', 1)
    assert global_board_3.current_board() is None

    # Wrong previous spot
    global_board_3._previous_spot_idx = 0
    with pytest.raises(IndexError):
        global_board_3.current_board()


def test_global_board_row_clmn_split():
    global_board_1 = GlobalBoard(4, False, False)
    assert global_board_1.row_clmn_split(1) == (0, 0)
    assert global_board_1.row_clmn_split(2) == (0, 1)
    assert global_board_1.row_clmn_split(5) == (1, 0)
    assert global_board_1.row_clmn_split(16) == (3, 3)
    assert global_board_1.row_clmn_split(None) == (None, None)


def test_global_board_last_move_highlight():
    global_board_1 = GlobalBoard(5, False, False)
    global_board_1._previous_board_idx = 22
    global_board_1._previous_spot_idx = 13
    assert global_board_1.last_move_highlight(21, 1) is None
    assert global_board_1.last_move_highlight(22, 1) == 2

    with pytest.raises(IndexError):
        global_board_1.last_move_highlight(25, 4)
    with pytest.raises(IndexError):
        global_board_1.last_move_highlight(2, 5)


def test_global_board_compare():
    global_board_1 = GlobalBoard(3, False, False)
    assert global_board_1.compare(1, 0.5)
    assert not global_board_1.compare(2, 3)


def test_global_board_separator_row():
    assert GlobalBoard(2, False, False).separator_row(1) == \
        '|---:---#########'
    assert GlobalBoard(4, False, False).separator_row() ==  \
        '|---:---:---:---|---:---:---:---|---:---:---:---|---:---:---:---|'


def test_global_board_row_of_spots():
    global_board_1 = GlobalBoard(4, False, False)
    spots = ['x', '', '', '', '', 'x', '', '', '', '', 'x', '', '', '', '', 'x']
    spots_2 = ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o']
    for i in range(16):
        global_board_1.local_board(i + 1)._spots = spots
    global_board_1.local_board(2)._spots = spots_2

    assert global_board_1.row_of_spots(0) ==    \
        '| x :   :   :   | x : o : x : o | x :   :   :   | x :   :   :   |'
    assert global_board_1.row_of_spots(1, 1) == \
        '|   : x :   :   # x : o : x : o #   : x :   :   |   : x :   :   |'
    assert global_board_1.row_of_spots(4, 3) == \
        '| x :   :   :   | x :   :   :   | x :   :   :   # x :   :   :   #'


def test_global_board_row_of_wins():
    global_board_1 = GlobalBoard(4, True, True)
    for i in range(16):
        global_board_1.local_board(i + 1)._win = 'o' if i % 3 else 'x'
    global_board_1.local_board(10)._win = None

    assert global_board_1.row_of_wins(0) == ':x:o:o:x:'
    assert global_board_1.row_of_wins(1) == ':o:o:x:o:'
    assert global_board_1.row_of_wins(2) == ':o: :o:o:'
    assert global_board_1.row_of_wins(3) == ':x:o:o:x:'


def test_global_board_possible_boards():
    global_board_1 = GlobalBoard(4, True, False)
    global_board_1._local_boards[0]._win = 'x'
    global_board_1._local_boards[2]._full = True
    assert global_board_1.possible_boards() == [
        2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16
    ]


def test_global_board_choose_board():
    global_board_1 = GlobalBoard(4, False, False)

    with pytest.raises(IndexError):
        global_board_1.choose_board(0)

    global_board_1.choose_board(1)
    assert global_board_1._board_choice == 1

    # attempt to choose board when there was already board chosen
    with pytest.raises(BoardChoiceError):
        global_board_1.choose_board(2)

    # attempt to choose board when there is no permition for that
    global_board_2 = GlobalBoard(4, False, False)
    global_board_2._previous_spot_idx = 1
    with pytest.raises(BoardChoiceError):
        global_board_2.choose_board(2)

    # choosing a board that is won or full
    global_board_3 = GlobalBoard(4, True, False)
    global_board_3._local_boards[0]._full = True
    with pytest.raises(BoardLockedError):
        global_board_3.choose_board(1)

    global_board_3._local_boards[2]._win = True
    with pytest.raises(BoardLockedError):
        global_board_3.choose_board(3)


def test_global_board_save_last_move():
    global_board_1 = GlobalBoard(4, False, False)
    assert global_board_1._previous_board_idx is None
    assert global_board_1._previous_spot_idx is None
    global_board_1.save_last_move(1, 2)
    assert global_board_1._previous_board_idx == 2
    assert global_board_1._previous_spot_idx == 1


def test_global_board_make_move():
    global_board_1 = GlobalBoard(3, False, False)
    spots = ['', '', 'x', '', '', '', '', '', '']
    spots_2 = ['', '', 'x', '', '', '', '', '', 'o']
    spots_3 = ['', 'x', 'x', '', '', '', '', '', '']

    # board hasn't been chosen
    with pytest.raises(BoardChoiceError):
        global_board_1.make_move('x', 3)

    global_board_1._board_choice = 3
    global_board_1.make_move('x', 3)
    assert global_board_1.local_board(3)._spots == spots
    assert global_board_1._previous_spot_idx == 3
    assert global_board_1._previous_board_idx == 3
    assert global_board_1._board_choice is None
    assert not global_board_1._last_won

    global_board_1.make_move('o', 9)
    assert global_board_1.local_board(3)._spots == spots_2
    assert global_board_1._previous_spot_idx == 9
    assert global_board_1._previous_board_idx == 3
    assert global_board_1._board_choice is None
    assert not global_board_1._last_won

    # winning
    global_board_1.local_board(1)._spots = spots_3
    global_board_1._previous_spot_idx = 1
    global_board_1.make_move('x', 1)
    assert global_board_1._previous_spot_idx == 1
    assert global_board_1._previous_board_idx == 1
    assert global_board_1._board_choice is None
    assert global_board_1._last_won

    global_board_1.make_move('x', 5)
    assert global_board_1._previous_spot_idx == 5
    assert global_board_1._previous_board_idx == 1
    assert global_board_1._board_choice is None
    assert not global_board_1._last_won

    with pytest.raises(ValueError):
        global_board_1.make_move('z', 2)
    with pytest.raises(IndexError):
        global_board_1.make_move('x', 0)


def test_global_board_global_win_check():
    global_board_1 = GlobalBoard(4, False, False)
    assert global_board_1.global_win_check() is None

    # win diagonally left
    global_board_1._local_boards[0]._win = 'x'
    global_board_1._local_boards[5]._win = 'x'
    global_board_1._local_boards[10]._win = 'x'
    global_board_1._local_boards[15]._win = 'x'
    assert global_board_1.global_win_check() == 'x'

    # win vertically
    global_board_1._local_boards[1]._win = 'o'
    global_board_1._local_boards[5]._win = 'o'
    global_board_1._local_boards[9]._win = 'o'
    global_board_1._local_boards[13]._win = 'o'
    assert global_board_1.global_win_check() == 'o'

    global_board_2 = GlobalBoard(4, True, False)
    for i in range(16):
        if i == 3:
            global_board_2.local_board(i + 1)._win = 'x'
        else:
            global_board_2.local_board(i + 1)._full = True
    # draw with LOCK_AFTER_WIN
    assert global_board_2.global_win_check() == 'draw'


    global_board_2._LOCK_AFTER_WIN = False
    assert global_board_2.global_win_check() is None


def test_global_board_if_first_turn():
    global_board_1 = GlobalBoard(3, False, False)
    assert global_board_1.if_first_turn()

    global_board_1.choose_board(5)
    global_board_1.make_move('o', 5)
    assert not global_board_1.if_first_turn()


def test_global_board_eq():
    assert GlobalBoard(4, True, False) == GlobalBoard(4, True, False)
    assert not GlobalBoard(4, True, False) == GlobalBoard(4, False, False)

    global_board_1 = GlobalBoard(3, True, True)
    global_board_1._local_boards[8]._spots[8] = 'x'
    assert not global_board_1 == GlobalBoard(3, True, True)

    assert not GlobalBoard(3, False, False) == GlobalBoard(4, False, False)


# UltimateTicTacToe
def test_ultimate_tic_tac_toe_constructor():
    ultimate_tic_tac_toe_1 = UltimateTicTacToe(4, False, False)
    assert ultimate_tic_tac_toe_1._board == GlobalBoard(4, False, False)

    ultimate_tic_tac_toe_2 = UltimateTicTacToe(5, True, True)
    assert ultimate_tic_tac_toe_2._board == GlobalBoard(5, True, True)

    with pytest.raises(ValueError):
        UltimateTicTacToe(1, True, True)


def test_ultimate_tic_tac_toe_get_global_board():
    ultimate_tic_tac_toe_1 = UltimateTicTacToe(4, True, True)
    global_board = ultimate_tic_tac_toe_1._board
    assert ultimate_tic_tac_toe_1.global_board() == global_board


def test_ultimate_tic_tac_toe_play():
    game_1 = UltimateTicTacToe(3, False, False)

    # two random bots play
    assert game_1.play(game_1.random_bot, game_1.random_bot)


def test_ultimate_tic_tac_toe_always_winning_bot():

    # CHOICE_AFTER_WIN enabled
    game_1 = UltimateTicTacToe(3, False, True)
    with pytest.raises(GameRulesError):
        game_1.play(game_1.always_winning_bot, game_1.random_bot)

    # LOCK_AFTER_WIN enabled
    game_2 = UltimateTicTacToe(3, True, False)
    with pytest.raises(GameRulesError):
        game_2.play(game_2.always_winning_bot, game_2.random_bot)

    # wrong board size
    game_3 = UltimateTicTacToe(4, False, False)
    with pytest.raises(GameRulesError):
        game_3.play(game_3.always_winning_bot, game_3.random_bot)

    # always_winning_bot not starting
    game_4 = UltimateTicTacToe(3, False, False)
    with pytest.raises(GameRulesError):
        game_4.play(game_4.random_bot, game_4.always_winning_bot)

    game_5 = UltimateTicTacToe(3, False, False)
    assert game_5.play(game_5.always_winning_bot, game_5.random_bot) == 'x'
