import socket

 
msgSize = 1047
msgFromClient       = "A" * msgSize

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("0.0.0.0", 9191)

bufferSize          = 1024


# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)
msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from Server {}".format(msgFromServer[0])

print(msg)