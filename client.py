# This is client code to receive video frames over UDP and save as .MP4 file
from curses import meta
import cv2, imutils, socket
import base64
import json
from datetime import datetime
import argparse
import time
import random

BUFF_SIZE = 65536
RECV_BUFFER = 1024
WIDTH = 600

def frame_analysis(frame):
    # code for recognition come here
    # labels must be added also here
    height, width = frame.shape[:2]
    metadata = {}
    labels = []
    for i in range(random.randrange(1, 10)):
        x1 = random.randrange(1, width)
        y1 = random.randrange(1, height)
        x2 = random.randrange(x1, width)
        y2 = random.randrange(y1, height)
        labels.append({"label":f"label_{i}","coordinates": [x1, y1, x2, y2]})

    metadata["labels"] = labels
    metadata["timestamp"] = time.time()
    return metadata


def main(my_name, video_source, host, port):
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
   

    if video_source in ["0", "1"]:
        video_source = int(video_source)
    vid = cv2.VideoCapture(video_source)
    if not vid.isOpened():
        print("Cannot open video!")
        exit()

    client_socket.connect((host, port))

    while True:
        
        ret, frame = vid.read()
        if ret is False:
            vid =  cv2.VideoCapture(video_source)
            continue
            
        frame = imutils.resize(frame, width=WIDTH)
        metadata = frame_analysis(frame)
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        photo = base64.b64encode(buffer).decode()
        message = dict()
        message["photo"] = photo
        message["name"] = my_name
        message["metadata"] = metadata
        message = json.dumps(message)
        client_socket.sendall(message.encode())
        time.sleep(0.1)
        print(client_socket.recv(RECV_BUFFER))
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--name", required=True)
    args.add_argument("--video", required=True)
    args.add_argument("--host", default="0.0.0.0")
    args.add_argument("--port", default=9999, type=int)
    args = args.parse_args()
    main(args.name, args.video, args.host, args.port)
