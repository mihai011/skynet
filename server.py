# This is server code to send video frames over UDP so that client can save it
from calendar import c
from os import name
import cv2, socket
import numpy as np
import base64
import select
import json
import pulsar

BUFF_SIZE = 65536

def draw_labels(frame, metadata):

    for label in metadata["labels"]:
        x1, y1, x2, y2 = label["coordinates"]
        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return frame

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    host_ip = "0.0.0.0"  #  socket.gethostbyname(host_name)
    port = 9998
    socket_address = (host_ip, port)
    server_socket.bind(socket_address)
    server_socket.listen()
    print("Listening at:", socket_address)
    
    client = pulsar.Client('pulsar://localhost:6650')
    producer = client.create_producer('result-surveilance')
    print("Pulsar producer created")

    # Create a poll object
    poll = select.poll()

    # Register the server socket with the poll object for monitoring
    poll.register(server_socket, select.POLLIN)

    # Dictionary to map file descriptors to their corresponding sockets
    fd_to_socket = {server_socket.fileno(): server_socket}

    while True:
        events = poll.poll()
        for fd, event in events:
            if fd == server_socket.fileno():
                conn, _ = server_socket.accept()
                print("Accepting new connection")
                poll.register(conn, select.POLLIN)
                fd_to_socket[conn.fileno()] = conn
            elif event & select.POLLIN:
                conn = fd_to_socket[fd]
                try:
                    msg = conn.recv(BUFF_SIZE)
                    if not msg:
                        raise ConnectionError("Client disconnected")
                    json_message = json.loads(msg)
                    photo = json_message["photo"]
                    client_name = json_message["name"]
                    metadata = json_message["metadata"] # use labels here for showing on the screen
                    photo_data = base64.b64decode(photo, " /")
                    npdata = np.frombuffer(photo_data, dtype=np.uint8)
                    frame = cv2.imdecode(npdata, 1)
                    frame = draw_labels(frame, metadata)
                    cv2.imshow(client_name, frame)
                    producer.send(json.dumps(json_message).encode('utf-8'))
                    conn.send(b"OK")
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                except ConnectionError as e:
                    cv2.destroyAllWindows()
                    poll.unregister(conn)
                    del fd_to_socket[fd]
                    conn.close()
                except json.JSONDecodeError as e:
                    print("Invalid message")
                    conn.send(b"Invalid message")
                    


if __name__ == "__main__":
    main()
