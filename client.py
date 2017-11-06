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

REGISTER = 'R'
GAME_START = 'S'
GAME_INFO  = 'G'

BUFLEN = 4096

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', int(sys.argv[1]))

def display_thread():
    # this function handles display
    return

def input_thread():
    # this function handles user input
    return

def launch_game():
    # this function launches the game
    return

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
