""" 
    Run this on the computer with the webcam
    reads in the webcam and sends them over the network to a client.
    really intended for LAN usage, unless you have some balling internet (cries in US telecom monopolies)
"""
import threading
import socket
import cv2
import queue
import pickle
import struct
import sys

DEFAULT_PORT = 42699

def handle_client(*args,**kwargs):
    conn,addr,frame_queue = args
    print("connected with client:",addr)

    success = True
    while success:
        success,frame = frame_queue.get()
        bindump = pickle.dumps(frame)
        packaged_msg = struct.pack('>I',len(bindump)) + bindump
        conn.sendall(packaged_msg)

    conn.close()
    

def run_server(frame_queue,port):
    host = "0.0.0.0"
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((host, port))
    acepting_clients = True
    s.listen(1)

    while acepting_clients:
        conn, addr = s.accept()
        client_thread = threading.Thread(target=handle_client,args=(conn,addr,frame_queue))
        client_thread.start()

def main(port):
    frame_queue = queue.Queue()
    server_thread = threading.Thread(target=run_server,args=(frame_queue,port))
    server_thread.start()
    webcam = cv2.VideoCapture(0)
    success = True
    while success:
        success,frame = webcam.read()
        frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        frame_queue.put((success,frame))


if __name__ == '__main__':
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    main(port)