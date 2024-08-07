# This is client code to receive video frames over UDP and save as .MP4 file
import cv2, imutils, socket
import base64
import json
from datetime import datetime
import argparse
import time

fourcc = 0x7634706D
now = datetime.now()
time_str = now.strftime("%d%m%Y%H%M%S")
time_name = "_Rec_" + time_str + ".mp4"
FPS = 30
frame_shape = False


BUFF_SIZE = 65536
WIDTH = 600


def main(my_name, video_source):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    host_ip = "0.0.0.0"
    port = 9999

    if video_source in ["0", "1"]:
        video_source = int(video_source)
    vid = cv2.VideoCapture(video_source)
    if not vid.isOpened():
        print("Cannot open video!")
        exit()

    client_socket.connect((host_ip, port))

    while True:
        try:
            _, frame = vid.read()
            if frame is None:
                print("Frame is null!")
                continue
            frame = imutils.resize(frame, width=WIDTH)
            # code for recognition come here 
            # lavbels must be added also here
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            photo = base64.b64encode(buffer).decode()
            message = dict()
            message["photo"] = photo
            message["name"] = my_name
            time_str = time.time()
            message["labels"] = {"label1":[1,2,3,4], "label2":[1,2,3,4], "timestamp":time_str}
            message = json.dumps(message)
            client_socket.sendall(message.encode())
            client_socket.recv(BUFF_SIZE)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
        except Exception as e:
            pass


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--name", required=True)
    args.add_argument("--video", required=True)
    args = args.parse_args()
    main(args.name, args.video)
