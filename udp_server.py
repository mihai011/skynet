import json
import cv2
import socket
import numpy as np
import base64

host = "0.0.0.0"
port = 9999
max_length = 65000
batch_size = 1000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))

def first_difference_index(sorted_list):
    for i in range(1, len(sorted_list)):
        if sorted_list[i][0] != sorted_list[i - 1][0]:
            return i

def main():
    print("-> waiting for connection")

    streams = {}
    
    while True:
        data, address = sock.recvfrom(max_length)
        
        data = data.decode("utf-8")
        data = json.loads(data)
        
        if "stream_name" not in data:
            continue
        if "packet_index" not in data:
            continue
        if "hash" not in data:
            continue
        
        stream_name = data["stream_name"]
        packet_index = data["packet_index"]
        packet_hash = data["hash"]
        
        if stream_name not in streams:
            print(f"-> creating stream {stream_name}")
            streams[stream_name] = []
            
        video_data = base64.b64decode(data["video_data"].encode("utf-8"))
        streams[stream_name].append((packet_hash, packet_index , video_data))
            
        if len(streams[stream_name]) == batch_size:
            
            streams[stream_name].sort(key=lambda x: (x[0], x[1]))
            
            image_index = first_difference_index(streams[stream_name])
            video_interval = streams[stream_name][:image_index]
            streams[stream_name] = streams[stream_name][image_index:]
            current_packet_hash = video_interval[0][0]
                        
            print(f"-> received {len(video_interval)} frames with hash {current_packet_hash}")
            video_data = b"".join([x[2] for x in video_interval])
            
            frame_buffer = np.frombuffer(video_data, dtype=np.uint8)
            frame_reshaped = frame_buffer.reshape(frame_buffer.shape[0], 1)
            
            frame_decoded = cv2.imdecode(frame_reshaped, cv2.COLOR_BGR2RGB)
            frame_flipped = cv2.flip(frame_decoded, 1)
            
            if frame_flipped is not None and type(frame_flipped) == np.ndarray:
                cv2.imshow(stream_name, frame_flipped)
                if cv2.waitKey(1) == 27:
                    break            

       
    print("goodbye")


if __name__ == "__main__":
    main()
