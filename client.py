"""
This UDP base client code is sourced from
https://pymotw.com/2/socket/udp.html
"""
import socket
import sys
import threading

if len(sys.argv) <= 1:
    print("usage: client <PORT NUMBER>")
    sys.exit()

EXIT_CODES = {
    'F' : "Server is full! Try again later"
}

DISPLAY = {
    'X' : 'X',
    'O' : 'O',
    'Z' : ' '
}

REGISTER = 'R'
GAME_START = 'S'
GAME_INFO  = 'G'

BUFLEN = 4096

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', int(sys.argv[1]))

def display_game(game_info):
    # this function handles displaying the game
    game_info = list(game_info)

    for i in range(len(game_info)):
        game_info[i] = DISPLAY[game_info[i]]

    print("\nThis is the current game board:\n")
    print("%s | %s | %s" % (tuple(game_info[:3])))
    print('-' * 9)
    print("%s | %s | %s" % (tuple(game_info[3:6])))
    print('-' * 9)
    print("%s | %s | %s\n" % (tuple(game_info[6:])))

def display_thread():
    # this function handles display
    while True:
        response, _ = sock.recvfrom(BUFLEN)
        if response[0] == GAME_INFO:
            display_game(response[1:])
        else:
            print(response)

def input_thread():
    # this function handles user input
    while True:
        message = raw_input()
        sock.sendto(message, server_address)

def launch_game():
    # this function launches the game
    thread.Thread(target=input_thread).start()
    thread.Thread(target=display_thread).start()

def initialize():
    print("Connecting to server...")
    sock.sendto(REGISTER, server_address)

initialize()

while True:
    response, _ = sock.recvfrom(BUFLEN)
    if response in EXIT_CODES:
        print(EXIT_CODES[response])
        sys.exit()
    elif response == GAME_START:
        launch_game()
        break
    else:
        print(response)
'''
while True:
    try:
        message = raw_input('Enter your message:\n')
        sock.sendto(message, server_address)

        data, server = sock.recvfrom(BUFLEN)
        print("SERVER SAYS: " + data)
    except:
        print("Unexpected Error! - "+ sys.exc_info()[0])
        raise
'''
