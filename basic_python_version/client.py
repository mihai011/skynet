# This is client code to receive video frames over UDP and save as .MP4 file
import cv2, imutils, socket
import base64
import json
import argparse


BUFF_SIZE = 65536
WIDTH = 600


def main(video_name, my_name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    host_ip = "0.0.0.0"
    port = 9999

    vid = cv2.VideoCapture(video_name)
    if not vid.isOpened():
        print("Cannot open video!")
        exit()

    client_socket.connect((host_ip, port))

    while True:
        try:
            _, frame = vid.read()
            if frame is None:
                print("Frame is null!")
                break
            frame = imutils.resize(frame, width=WIDTH)
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            photo = base64.b64encode(buffer).decode()
            message = dict()
            message["photo"] = photo
            message["name"] = my_name
            message = json.dumps(message)
            client_socket.sendall(message.encode())
            client_socket.recv(10)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                vid.close()
                break
        except Exception as e:
            pass


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--name", required=True)
    args.add_argument("--video", required=True)

    args = args.parse_args()

    main(args.video, args.name)
