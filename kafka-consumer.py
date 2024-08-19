from confluent_kafka import Consumer
import numpy as np
import cv2
import pickle
import base64
import argparse


def draw_labels(frame, metadata):
    for label in metadata["labels"]:
        x1, y1, x2, y2 = label["coordinates"]
        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return frame


def main(args):
    hafka_host = args.kafka_host
    # Configuration for Kafka Consumer
    conf = {
        "bootstrap.servers": hafka_host,  # Replace with your Kafka broker's address
        "group.id": "my_consumer_group",  # Consumer group ID
        "auto.offset.reset": "latest",  # Start reading at the earliest offset
    }

    # Create Consumer instance
    consumer = Consumer(conf)

    # Subscribe to a topic
    topic = "test_topic"
    consumer.subscribe([topic])

    while True:
        # Poll for a message
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        data = pickle.loads(msg.value())
        buffer = data["image"]
        stream = data["stream"]
        image_bytes = base64.b64decode(buffer)
        image_np = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        frame = draw_labels(frame, data["metadata"])
        cv2.imshow(stream, frame)
        cv2.waitKey(1)

        print(
            f"Received {len(msg.value())} bytes from {msg.topic()}  [{msg.partition()}] offset {msg.offset()}]"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kafka_host", type=str, default="2.tcp.eu.ngrok.io:17273", help="Kafka host"
    )
    args = parser.parse_args()
    main(args)
