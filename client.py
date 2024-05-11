# This is client code to receive video frames over UDP and save as .MP4 file
import cv2, imutils, socket
import numpy as np
import time
import uuid
import base64
import json 
from datetime import datetime

fourcc =0x7634706d 
now = datetime.now()
time_str = now.strftime("%d%m%Y%H%M%S")
time_name = '_Rec_'+time_str+'.mp4'
FPS = 30
frame_shape = False


BUFF_SIZE = 65536
WIDTH=600

def main(my_name):
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    host_name = socket.gethostname()
    host_ip = "0.0.0.0"
    port = 9999


    vid = cv2.VideoCapture("video.mp4")
    if not vid.isOpened():
        print("Cannot open video!")
        exit()
        
    client_socket.connect((host_ip,port))

    while True:
        try:
            _, frame = vid.read()
            if frame is None:
                print("Frame is null!")
                break
            frame = imutils.resize(frame,width=WIDTH)
            encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
            photo = base64.b64encode(buffer).decode()
            message = dict()
            message['photo'] = photo
            message['name'] = my_name
            message = json.dumps(message)
            client_socket.sendall(message.encode())
            response = client_socket.recv(BUFF_SIZE)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        except Exception as e:
            pass
        
if __name__ == "__main__":
    main(str(uuid.uuid1()))