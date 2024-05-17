# This is server code to send video frames over UDP so that client can save it
import cv2, socket
import numpy as np
import base64
import select
import json


BUFF_SIZE = 655360


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    host_ip = "0.0.0.0"  #  socket.gethostbyname(host_name)
    port = 9999
    socket_address = (host_ip, port)
    server_socket.bind(socket_address)
    server_socket.listen()
    print("Listening at:", socket_address)

    # Create a poll object
    poll = select.poll()

    # Register the server socket with the poll object for monitoring
    poll.register(server_socket, select.POLLIN)

    # Dictionary to map file descriptors to their corresponding sockets
    fd_to_socket = {server_socket.fileno(): server_socket}

    fd_to_image = dict()
    while True:
        events = poll.poll()
        for fd, event in events:
            if fd == server_socket.fileno():
                conn, address = server_socket.accept()
                print(f"Accepting new connection from {address}")
                poll.register(conn, select.POLLIN)
                fd_to_socket[conn.fileno()] = conn
            elif event & select.POLLIN:
                conn = fd_to_socket[fd]
                try:
                    msg = conn.recv(BUFF_SIZE)
                    if not msg:
                        raise ConnectionError("Client disconnected")
                    json_message = json.loads(msg.decode())
                    photo = json_message["photo"]
                    client_name = json_message["name"]
                    fd_to_image[fd] = client_name
                    photo_data = base64.b64decode(photo, " /")
                    npdata = np.frombuffer(photo_data, dtype=np.uint8)
                    frame = cv2.imdecode(npdata, 1)
                    cv2.imshow(client_name, frame)
                    conn.sendall(b"OK")
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                except ConnectionError as e:
                    print(f"Connection error on {fd}")
                    cv2.destroyWindow(fd_to_image[fd])
                    cv2.waitKey(1)
                    fd_to_image.pop(fd)
                    poll.unregister(conn)
                    del fd_to_socket[fd]
                    conn.close()
                except ValueError as e:
                    conn.sendall(b"OK")
                    print(e)
            else:
                print(f"Client disconnected on {fd}")
                print(f"Destroying window {fd_to_image[fd]}")
                cv2.destroyWindow(fd_to_image[fd])
                cv2.waitKey(1)
                fd_to_image.pop(fd)
                poll.unregister(conn)
                del fd_to_socket[fd]
                conn.close()


if __name__ == "__main__":
    main()
