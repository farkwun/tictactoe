"""
This UDP base server code is sourced from
https://pymotw.com/2/socket/udp.html
"""
import socket
import sys
import random

import tictactoe.shared

if len(sys.argv) <= 1:
    print("usage: server <PORT NUMBER>")
    sys.exit()

# Constants
TURN_ERROR = "It isn't your turn right now."
INPUT_ERROR = "Invalid input: %s. Try again."
WAIT_MSG = "Awaiting players... (%s/%s).\n"
AI_PROMPT = ("Type '%s' if you would like to add an AI." %
             tictactoe.shared.AI)
ROLE_PROMPT = "You are playing as: %s\n"
MOVE_PROMPT = ("It's your turn! Here are the moves left:\n"
               "%s\n"
               "Enter the move you would like to perform:\n")
VALID_ROWS = {
    'A': 0,
    'B': 1,
    'C': 2
}
VALID_COLS = {
    '1': 0,
    '2': 1,
    '3': 2
}
SYMBOLS = [
    'X',
    'O'
]

class Board(object):
    def __init__(self):
        self.ROLE = {}
        self.PLAYERS = []
        self.PLAY_PTR = 0
        self.NUM_PLAYERS = 0
        self.GAME_BOARD = [
            [tictactoe.shared.NULL_CHAR] * tictactoe.shared.BOARD_COLS
            for _ in range(tictactoe.shared.BOARD_ROWS)
        ]
        self.LINES = self.generate_lines()
        self.MOVES_LEFT = self.move_set()

    def move_set(self):
        moves = set()
        for row in VALID_ROWS.keys():
            for col in VALID_COLS.keys():
                moves.add(row + col)
        return moves

    def generate_lines(self):
        lines = []

        # rows and cols
        for row in range(tictactoe.shared.BOARD_ROWS):
            temp_rows = []
            temp_cols = []
            for col in range(tictactoe.shared.BOARD_COLS):
                temp_rows.append((row, col))
                temp_cols.append((col, row))
            lines.append(temp_rows)
            lines.append(temp_cols)

        # diagonals
        diag_a = []
        diag_b = []
        for row in range(tictactoe.shared.BOARD_ROWS):
            diag_a.append((row, row))
            diag_b.append((tictactoe.shared.BOARD_ROWS - row - 1, row))
        lines.append(diag_a)
        lines.append(diag_b)

        return lines

    def add_player(self, player_id):
        self.ROLE[player_id] = SYMBOLS[self.NUM_PLAYERS]
        self.PLAYERS.append(player_id)
        self.NUM_PLAYERS += 1

BOARD = Board()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', int(sys.argv[1]))

print('Launching server on %s port %s' % server_address)

sock.bind(server_address)

def send_to_address(message, address):
    if address != tictactoe.shared.AI:
        sock.sendto(message, address)

def broadcast(message):
    for address in BOARD.PLAYERS:
        send_to_address(message, address)

def is_valid_move(move):
    return(len(move) <= 2 and
           move in BOARD.MOVES_LEFT and
           move[0] in VALID_ROWS and
           move[1] in VALID_COLS)

def reset():
    global BOARD
    BOARD = Board()

def increment_play_order():
    BOARD.PLAY_PTR += 1
    if BOARD.PLAY_PTR >= len(BOARD.PLAYERS):
        BOARD.PLAY_PTR = 0

def await_players():
    print("Waiting for players...")
    while BOARD.NUM_PLAYERS < tictactoe.shared.MAX_PLAYERS:
        data, address = sock.recvfrom(tictactoe.shared.BUFLEN)
        if address not in BOARD.ROLE:
            BOARD.add_player(address)
        elif data == tictactoe.shared.AI:
            BOARD.add_player(tictactoe.shared.AI)
        else:
            send_to_address(INPUT_ERROR % data, address)
        broadcast_state()

def broadcast_state():
    message = WAIT_MSG % (BOARD.NUM_PLAYERS, tictactoe.shared.MAX_PLAYERS)
    broadcast(message + AI_PROMPT)

def broadcast_game():
    game_state = [tictactoe.shared.GAME_INFO]
    for row in range(len(BOARD.GAME_BOARD)):
        for col in range(len(BOARD.GAME_BOARD)):
            game_state.append(BOARD.GAME_BOARD[row][col])
    broadcast(''.join(game_state))

def is_winning_set(char_set):
    return (tictactoe.shared.NULL_CHAR not in char_set and
            len(char_set) == 1)

def get_winner():
    for line in BOARD.LINES:
        temp = set()
        for row, col in line:
            temp.add(BOARD.GAME_BOARD[row][col])
        if is_winning_set(temp):
            return temp.pop()

    if not BOARD.MOVES_LEFT:
        return "Nobody"

    return None

def launch_game():
    broadcast("\nGame on!\n")
    for address in BOARD.PLAYERS:
        message = ROLE_PROMPT % BOARD.ROLE[address]
        send_to_address(message, address)
    manage_board()

def prompt_player(address):
    message = (ROLE_PROMPT % BOARD.ROLE[address] +
               MOVE_PROMPT % str(sorted(list(BOARD.MOVES_LEFT))))
    send_to_address(message, address)

def set_board_at(move, value):
    row = VALID_ROWS[move[0]]
    col = VALID_COLS[move[1]]
    BOARD.GAME_BOARD[row][col] = value
    BOARD.MOVES_LEFT.remove(move)

def point_to_move(point):
    row, col = point[0], point[1]
    move = ""

    for key, value in VALID_ROWS.items():
        if value == row:
            move += key
            break

    for key, value in VALID_COLS.items():
        if value == col:
            move += key
            break

    return move

def moves_and_symbols_from(line):
    line_symbols = {}
    moves = set()
    for point in line:
        symbol = BOARD.GAME_BOARD[point[0]][point[1]]
        if symbol == tictactoe.shared.NULL_CHAR:
            moves.add(point_to_move(point))
        elif symbol in line_symbols:
            line_symbols[symbol] += 1
        else:
            line_symbols[symbol] = 1

    return moves, line_symbols

def enemy_is_winning(symbol_dict):
    if len(symbol_dict.keys()) > 1:
        return False
    for key, value in symbol_dict.items():
        if value > 1 and key != BOARD.ROLE[tictactoe.shared.AI]:
            return True
    return False

def can_win_line(symbol_dict):
    return (BOARD.ROLE[tictactoe.shared.AI] in symbol_dict and
            len(symbol_dict.keys()) <= 1)

def will_win_on_move(symbol_dict):
    ai_symbol = BOARD.ROLE[tictactoe.shared.AI]
    return (ai_symbol in symbol_dict and
            symbol_dict[ai_symbol] == tictactoe.shared.BOARD_ROWS - 1)

def get_ai_move():
    center = (tictactoe.shared.BOARD_ROWS//2, tictactoe.shared.BOARD_COLS//2)
    center_move = point_to_move(center)
    enemy_block_moves = set()
    win_attempt_moves = set()
    ideal_moves = set()

    for line in BOARD.LINES:
        moves, line_symbols = moves_and_symbols_from(line)
        if not moves:
            continue
        if will_win_on_move(line_symbols):
            return moves.pop()
        if enemy_is_winning(line_symbols):
            enemy_block_moves = enemy_block_moves.union(moves)
        elif can_win_line(line_symbols):
            win_attempt_moves = win_attempt_moves.union(moves)

    ideal_moves = enemy_block_moves.intersection(win_attempt_moves)

    if ideal_moves:
        return ideal_moves.pop()

    if enemy_block_moves:
        return enemy_block_moves.pop()

    if win_attempt_moves:
        return win_attempt_moves.pop()

    if center_move in BOARD.MOVES_LEFT:
        return center_move

    return random.choice(tuple(BOARD.MOVES_LEFT))

def get_move_from(player):
    valid_move = None
    if player == tictactoe.shared.AI:
        return get_ai_move()
    prompt_player(player)
    while not valid_move:
        move, address = sock.recvfrom(tictactoe.shared.BUFLEN)
        if address not in BOARD.ROLE:
            send_to_address(tictactoe.shared.SERVER_FULL, address)
            continue
        move = move.upper()
        if address != player:
            send_to_address(TURN_ERROR, address)
        elif is_valid_move(move):
            valid_move = move
        else:
            send_to_address(INPUT_ERROR % move, address)

    return valid_move

def manage_board():
    while True:
        broadcast_game()
        active_player = BOARD.PLAYERS[BOARD.PLAY_PTR]
        move = get_move_from(active_player)
        set_board_at(move, BOARD.ROLE[active_player])
        increment_play_order()
        winner = get_winner()
        if winner:
            broadcast_game()
            message = "%s won!" % winner
            broadcast(message)
            broadcast(tictactoe.shared.GAME_END)
            break

while True:
    reset()
    await_players()
    launch_game()
