"""
This UDP base server code is sourced from
https://pymotw.com/2/socket/udp.html
"""
import socket
import sys
import shared

if len(sys.argv) <= 1:
    print("usage: server <PORT NUMBER>")
    sys.exit()

# Constants
TURN_ERROR = "It isn't your turn right now."
INPUT_ERROR = "Invalid input: %s. Try again."
WAIT_MSG = "Awaiting players... (%s/%s)"
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
        self.GAME_BOARD = [[shared.NULL_CHAR] * shared.BOARD_COLS for _ in range(shared.BOARD_ROWS)]
        self.MOVES_LEFT = self.move_set()

    def move_set(self):
        moves = set()
        for row in VALID_ROWS.keys():
            for col in VALID_COLS.keys():
                moves.add(row + col)
        return moves


BOARD = Board()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', int(sys.argv[1]))

print('Launching server on %s port %s' % server_address)

sock.bind(server_address)

def send_to_address(message, address):
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
    while BOARD.NUM_PLAYERS < shared.MAX_PLAYERS:
        _, address = sock.recvfrom(shared.BUFLEN)
        if address not in BOARD.ROLE:
            BOARD.ROLE[address] = SYMBOLS[BOARD.NUM_PLAYERS]
            BOARD.PLAYERS.append(address)
            BOARD.NUM_PLAYERS += 1
        broadcast_state()

def broadcast_state():
    message = WAIT_MSG % (BOARD.NUM_PLAYERS, shared.MAX_PLAYERS)
    broadcast(message)

def broadcast_game():
    game_state = ['G']
    for row in range(len(BOARD.GAME_BOARD)):
        for col in range(len(BOARD.GAME_BOARD)):
            game_state.append(BOARD.GAME_BOARD[row][col])
    broadcast(''.join(game_state))

def is_winning_set(char_set):
    return shared.NULL_CHAR not in char_set and len(char_set) == 1

def get_winner():
    # check rows
    for row in range(shared.BOARD_ROWS):
        temp = set(BOARD.GAME_BOARD[row])
        if is_winning_set(temp):
            return temp.pop()

    # check cols
    for col in range(shared.BOARD_COLS):
        temp = set()
        for row in range(shared.BOARD_ROWS):
            temp.add(BOARD.GAME_BOARD[row][col])
        if is_winning_set(temp):
            return temp.pop()

    # check diags
    temp = set()
    for row in range(shared.BOARD_ROWS):
        temp.add(BOARD.GAME_BOARD[row][row])

    if is_winning_set(temp):
        return temp.pop()

    temp = set()
    for row in range(shared.BOARD_ROWS):
        temp.add(BOARD.GAME_BOARD[row][shared.BOARD_ROWS - row - 1])

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

def get_move_from(player):
    valid_move = None
    prompt_player(player)
    while not valid_move:
        move, address = sock.recvfrom(shared.BUFLEN)
        if address not in BOARD.ROLE:
            send_to_address(shared.SERVER_FULL, address)
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
            broadcast(shared.GAME_END)
            break

while True:
    reset()
    await_players()
    launch_game()
