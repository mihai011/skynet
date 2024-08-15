import json
import cv2
import socket
import pickle
import numpy as np
from pickle import UnpicklingError
from PIL import Image
import base64

host = "0.0.0.0"
port = 9999
max_length = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))


def main():
    print("-> waiting for connection")

    streams = {}

    while True:
        data, address = sock.recvfrom(max_length)

        data = data.decode("utf-8")
        data = json.loads(data)
        
        if "stream_name" not in data:
            continue
        if "pack_index" not in data:
            continue
        if "total_packs" not in data:
            continue
        
        stream_name = data["stream_name"]
        pack_index = data["pack_index"]
        total_packs = data["total_packs"]
        
        if stream_name not in streams:
            streams[stream_name] = {
                "pack_index": 0,
                "total_packs": total_packs,
                "video_data": b''
            }
            print(f"-> {stream_name} connected")
        if pack_index <= total_packs:
            
            video_data = base64.b64decode(data["video_data"].encode("utf-8"))
            streams[stream_name]["video_data"] += video_data
            
        if pack_index == total_packs:
            
            video_data = streams[stream_name]["video_data"]
            print(video_data[:2] , video_data[-2:])
            if video_data[:2] !=  b"\xff\xd8" and   video_data[-2:] != b"\xff\xd9":
                streams[stream_name]["video_data"] = b''
                print("problem")
                continue
            
            frame_buffer = np.frombuffer(video_data, dtype=np.uint8)
            frame_reshaped = frame_buffer.reshape(frame_buffer.shape[0], 1)
            
            frame_decoded = cv2.imdecode(frame_reshaped, cv2.COLOR_BGR2RGB)
            frame_flipped = cv2.flip(frame_decoded, 1)
            
            if frame_flipped is not None and type(frame_flipped) == np.ndarray:
                cv2.imshow(stream_name, frame_flipped)
                if cv2.waitKey(1) == 27:
                    break
            streams[stream_name]["video_data"] = b''
            

       
    print("goodbye")


if __name__ == "__main__":
    main()
