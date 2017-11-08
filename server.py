"""
This UDP base server code is sourced from
https://pymotw.com/2/socket/udp.html
"""
import socket
import sys

if len(sys.argv) <= 1:
    print("usage: server <PORT NUMBER>")
    sys.exit()

# Constants
BUFLEN      = 4096
MAX_PLAYERS = 2
SERVER_FULL = 'F'
GAME_START  = 'S'
GAME_END   = "V"
TURN_ERROR  = "It isn't your turn right now."
INPUT_ERROR = "Invalid input: "
USER_PROMPT_A = "\nIt's your turn! Here are the moves left:\n"
USER_PROMPT_B = "\nEnter the move you would like to perform:\n"
VALID_ROWS  = {
    'A' : 0,
    'B' : 1,
    'C' : 2
}
VALID_COLS  = {
    '1' : 0,
    '2' : 1,
    '3' : 2
}
SYMBOLS     = [
    'X',
    'O'
]

# Globals
MOVES_LEFT = set()
NUM_PLAYERS = 0
GAME_BOARD = [['Z'] * 3 for _ in range(3)]
PLAYERS = {}
PLAY_ORDER = []
PLAY_PTR = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', int(sys.argv[1]))

print('Launching server on %s port %s' % server_address)

sock.bind(server_address)

def broadcast(message):
    for address in PLAYERS.keys():
        sock.sendto(message, address)

def is_valid_move(move):
    return(len(move) <= 2 and
           move in MOVES_LEFT and
           move[0] in VALID_ROWS and
           move[1] in VALID_COLS)

def initialize_moves_left():
    for row in VALID_ROWS.keys():
        for col in VALID_COLS.keys():
            MOVES_LEFT.add(row + col)

def reset():
    global GAME_BOARD, PLAYERS, NUM_PLAYERS
    GAME_BOARD  = [['Z'] * 3 for _ in range(3)]
    PLAYERS     = {}
    NUM_PLAYERS = 0
    initialize_moves_left()

def increment_play_order():
    global PLAY_PTR
    PLAY_PTR += 1
    if PLAY_PTR >= len(PLAY_ORDER):
        PLAY_PTR = 0

def await_players():
    print("Waiting for players...")
    global NUM_PLAYERS
    while NUM_PLAYERS < MAX_PLAYERS:
        _, address = sock.recvfrom(BUFLEN)
        if address not in PLAYERS:
            PLAYERS[address] = SYMBOLS[NUM_PLAYERS]
            PLAY_ORDER.append(address)
            NUM_PLAYERS += 1
        broadcast_state()

def broadcast_state():
    WAIT_MSG = "\nAwaiting players... (%s/%s)" % (NUM_PLAYERS, MAX_PLAYERS)
    broadcast(WAIT_MSG)

def broadcast_game():
    game_state = ['G']
    for row in range(len(GAME_BOARD)):
        for col in range(len(GAME_BOARD)):
            game_state.append(GAME_BOARD[row][col])
    broadcast(''.join(game_state))

def get_winner():
    # check rows
    for row in range(len(GAME_BOARD)):
        temp = set(GAME_BOARD[row])
        if 'Z' in temp or len(temp) != 1:
            continue
        else:
            return temp.pop()

    # check cols
    for col in range(len(GAME_BOARD[0])):
        temp = set()
        for row in range(len(GAME_BOARD)):
            temp.add(GAME_BOARD[row][col])
        if 'Z' in temp or len(temp) != 1:
            continue
        else:
            return temp.pop()

    # check diags
    temp = set()
    for row in range(len(GAME_BOARD)):
        temp.add(GAME_BOARD[row][row])

    if 'Z' not in temp and len(temp) == 1:
        return temp.pop()

    temp = set()
    for row in range(len(GAME_BOARD)):
        temp.add(GAME_BOARD[row][len(GAME_BOARD) - row - 1])

    if 'Z' not in temp and len(temp) == 1:
        return temp.pop()

    if len(MOVES_LEFT) == 0:
        return "Nobody"

    return None

def launch_game():
    broadcast(GAME_START)
    broadcast("\nGame on!\n")
    for address in PLAYERS.keys():
        message = "You are playing %s's" % PLAYERS[address]
        sock.sendto(message, address)
    manage_board()

def prompt_player(address):
    message = USER_PROMPT_A + str(sorted(list(MOVES_LEFT))) + USER_PROMPT_B
    sock.sendto(message, address)

def manage_board():
    while True:
        broadcast_game()
        ACTIVE_PLAYER = PLAY_ORDER[PLAY_PTR]
        prompt_player(ACTIVE_PLAYER)
        move, address = sock.recvfrom(BUFLEN)
        move = move.upper()
        if address != PLAY_ORDER[PLAY_PTR]:
            sock.sendto(TURN_ERROR, address)
        elif is_valid_move(move):
            row = VALID_ROWS[move[0]]
            col = VALID_COLS[move[1]]
            GAME_BOARD[row][col] = PLAYERS[address]
            MOVES_LEFT.remove(move)
            increment_play_order()
            winner = get_winner()
            if winner:
                broadcast_game()
                message = "%s won!" % winner
                broadcast(message)
                broadcast(GAME_END)
                break
        else:
            sock.sendto(INPUT_ERROR + move + "\n", address)

while True:
    reset()
    await_players()
    launch_game()
