from struct import pack
from tarfile import data_filter
import cv2
import socket
import math
import pickle
import imutils
import time
import argparse
import json
import base64
import time

max_length = 3000
host = "0.0.0.0"
port = 9191
FPS = 20
time_interval = 1 / FPS


def main(stream_name, video_source):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    cap = cv2.VideoCapture(video_source)
    ret, frame = cap.read()

    while ret:
        # rezise and compress frame
        frame = imutils.resize(frame, width=800)
        retval, buffer = cv2.imencode(".jpg", frame)
        if retval:
            # convert to byte array
            buffer = buffer.tobytes()
            # get size of the frame
            buffer_size = len(buffer)

            num_of_packs = 1
            if buffer_size > max_length:
                num_of_packs = math.ceil(buffer_size / max_length)

            left = 0
            right = max_length
            hash_buffer = round(time.time() * 1000)
            
            for i in range(num_of_packs):
                data = {
                    "packet_index": i + 1,
                    "total_packs": num_of_packs,
                    "stream_name": stream_name,
                    "hash": hash_buffer,
                }

                # truncate data to send
                video_data = buffer[left:right]
                left = right
                right += max_length

                data["video_data"] = base64.b64encode(video_data).decode("utf-8")

                # send the frames accordingly
                data = json.dumps(data)
                data = data.encode("utf-8")
                sock.sendto(data, (host, port))
                
                
                if i == num_of_packs - 1 and video_data[-2:] != b"\xff\xd9":
                    print("problem")
                    
        print(f"-> sent packet in {num_of_packs} parts with hash {hash_buffer}")


        time.sleep(time_interval)
        ret, frame = cap.read()
        if not ret:
            cap = cv2.VideoCapture(video_source)
            ret, frame = cap.read()

    print("done")


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    stream_name = args.add_argument("--stream_name", required=True)
    video_source = args.add_argument("--video", required=True)
    args = args.parse_args()
    main(args.stream_name, args.video)
