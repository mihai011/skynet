import asyncio
import socketio

import cv2, imutils, socket
import base64
import json
import argparse

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('connection established')

@sio.on('my_message')
async def my_message(data):
    print('message received with ', data)

@sio.event
async def disconnect():
    print('disconnected from server')

async def main(video_name, name):
    await sio.connect('ws://localhost:8080')
    while True:
        print("Sending image")
        await sio.emit('image', 'Hello from client')
        sio.wait()
    
    # vid = cv2.VideoCapture(video_name)
    # while True:
    #     try:
    #         _, frame = vid.read()
    #         if frame is None:
    #             print("Frame is null!")
    #             break
    #         frame = imutils.resize(frame, width=600)
    #         _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    #         photo = base64.b64encode(buffer).decode()
    #         message = dict()
    #         message["photo"] = photo
    #         message["name"] = name
    #         print(photo)
    #         await sio.emit("image", message)

    #         key = cv2.waitKey(1) & 0xFF
    #         if key == ord("q"):
    #             vid.close()
    #             break
    #     except Exception as e:
    #         pass
    

if __name__ == '__main__':
    
    args = argparse.ArgumentParser()
    args.add_argument("--name", required=True)
    args.add_argument("--video", required=True)

    args = args.parse_args()

    asyncio.run(main(args.video, args.name))