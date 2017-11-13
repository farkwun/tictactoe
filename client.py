"""
This UDP base client code is sourced from
https://pymotw.com/2/socket/udp.html
"""
import socket
import sys
import threading
import time
import shared

if len(sys.argv) <= 1:
    print("usage: client <PORT NUMBER>")
    sys.exit()

EXIT_CODES = {
    shared.SERVER_FULL : "Server is full! Try again later",
    shared.GAME_END : "Thank you for playing!"
}

DISPLAY = {
    'X': 'X',
    'O': 'O',
    shared.NULL_CHAR: ' '
}

GAME_OVER = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', int(sys.argv[1]))

def display_game(game_info):
    # this function handles displaying the game
    game_info = list(game_info)

    for i in range(len(game_info)):
        game_info[i] = DISPLAY[game_info[i]]

    print("\nThis is the current game board:\n")
    print("   1 | 2 | 3\n")
    print("A  %s | %s | %s" % (tuple(game_info[:3])))
    print('  ' + '-' * 9)
    print("B  %s | %s | %s" % (tuple(game_info[3:6])))
    print('  ' + '-' * 9)
    print("C  %s | %s | %s\n" % (tuple(game_info[6:])))

def display_thread():
    # this function handles display
    global GAME_OVER
    while not GAME_OVER:
        response, _ = sock.recvfrom(shared.BUFLEN)
        if response[0] == shared.GAME_INFO:
            display_game(response[1:])
        elif response in EXIT_CODES:
            print(EXIT_CODES[response])
            GAME_OVER = True
        else:
            print(response)

def user_thread():
    # this function handles user input
    while not GAME_OVER:
        message = raw_input()
        sock.sendto(message, server_address)

def launch_game():
    # this function launches the game
    user    = threading.Thread(target=user_thread)
    display = threading.Thread(target=display_thread)
    user.daemon    = True
    display.daemon = True
    user.start()
    display.start()
    while not GAME_OVER:
        time.sleep(1)

def initialize():
    print("Connecting to server...")
    sock.sendto(shared.REGISTER, server_address)

initialize()
launch_game()
