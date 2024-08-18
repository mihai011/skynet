import time
import aiohttp
import asyncio
import argparse
import cv2
import imutils

FPS = 30
time_delay = 1/FPS

async def main(host, video_source, stream_name):
    
    data = {"stream_name":stream_name}
    
    async with aiohttp.ClientSession() as session:
        
        cap = cv2.VideoCapture(video_source)
        ret, frame = cap.read()
        while ret:
            frame = imutils.resize(frame, width=800)
            _, img_encoded = cv2.imencode(".jpg", frame)
            
            # make request
            data["image"] = img_encoded.tobytes()
            async with session.post(host, data=data) as response:
                print(response.status)
                
            ret, frame = cap.read()
            if not ret:
                cap = cv2.VideoCapture(video_source)
                ret, frame = cap.read()
            
            time.sleep(time_delay)

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    host = args.add_argument("--host", type=str)
    video_source = args.add_argument("--video_source", type=str)
    stream_name = args.add_argument("--stream_name", type=str)
    args = args.parse_args()
    
    asyncio.run(main(args.host, args.video_source, args.stream_name))