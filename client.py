"""
This UDP base client code is sourced from
https://pymotw.com/2/socket/udp.html
"""
import socket
import sys

if len(sys.argv) <= 1:
    print("usage: client <PORT NUMBER>")
    sys.exit()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', int(sys.argv[1]))

while(True):
    try:
        message = raw_input('Enter your message:\n')
        sock.sendto(message, server_address)

        data, server = sock.recvfrom(4096)
        print("SERVER SAYS: " + data)
    except:
        print("Unexpected Error! - "+ sys.exc_info()[0])
        raise
