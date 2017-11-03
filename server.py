"""
This UDP base server code is sourced from
https://pymotw.com/2/socket/udp.html
"""
import socket
import sys

if len(sys.argv) <= 1:
    print("usage: server <PORT NUMBER>")
    sys.exit()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', int(sys.argv[1]))

print('Launching server on %s port %s' % server_address)

sock.bind(server_address)

while True:
    print("Waiting for players...")
    data, address = sock.recvfrom(4096)

    print('Received %s bytes from %s' % (len(data), address))
    print(data)

    if data:
        sent = sock.sendto(data, address)
        print('sent %s bytes back to %s' % (sent, address))
    else:
        sent = sock.sendto("Did not receive anything", address)
