from confluent_kafka import Producer
import cv2
import imutils
import pickle
import base64
import argparse
import time
import random


FPS = 30
DELAY = 1 / FPS
IMAGE_WIDTH = 1000


# Function to handle delivery reports
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


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
        labels.append({"label": f"label_{i}", "coordinates": [x1, y1, x2, y2]})

    metadata["labels"] = labels
    metadata["timestamp"] = time.time()
    return metadata


def main(args):
    video = args.video
    topic = args.topic
    stream = args.stream
    kafka_host = args.kafka_host

    # Configuration for Kafka Producer
    conf = {
        "bootstrap.servers": kafka_host,  # Replace with your Kafka broker's address
    }
    # Create Producer instance
    producer = Producer(conf)

    cap = cv2.VideoCapture(video)
    data = {"stream": stream}
    while True:
        ret, frame = cap.read()
        if not ret:
            cap = cv2.VideoCapture(video)
            ret, frame = cap.read()
        frame = imutils.resize(frame, width=IMAGE_WIDTH)
        metadata = frame_analysis(frame)
        _, buffer = cv2.imencode(".jpg", frame)
        image = base64.b64encode(buffer).decode()
        data["image"] = image
        data["metadata"] = metadata
        value = pickle.dumps(data)
        # Produce a message to a specific topic
        producer.produce(topic, key="key", value=value, callback=delivery_report)
        # Wait for all messages in the producer queue to be delivered
        producer.flush()
        time.sleep(DELAY)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default="test_topic", help="Topic name")
    parser.add_argument(
        "--video", type=str, default="intersection_3.mp4", help="Video file path"
    )
    parser.add_argument(
        "--stream", type=str, default="my_name", help="name of the stream"
    )
    parser.add_argument(
        "--kafka_host", type=str, default="2.tcp.eu.ngrok.io:17273", help="Kafka host"
    )
    args = parser.parse_args()
    main(args)
