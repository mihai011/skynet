import numpy as np
import cv2
import pickle
import base64
import argparse
import pulsar
from pulsar import ConsumerKeySharedPolicy


key_shared_policy = ConsumerKeySharedPolicy()


def draw_labels(frame, metadata):
    for label in metadata["labels"]:
        x1, y1, x2, y2 = label["coordinates"]
        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return frame


def main(args):
    topic = args.topic
    subscription = args.subscription
    pulsar_host = args.pulsar_host

    client = pulsar.Client(pulsar_host)

    consumer = client.subscribe(
        topic,
        subscription,
        consumer_type=pulsar.ConsumerType.KeyShared,
        key_shared_policy=key_shared_policy,
    )

    while True:
        # Poll for a message
        msg = consumer.receive()
        if msg is None:
            continue
        data = pickle.loads(msg.value())
        buffer = data["image"]
        stream = data["stream"]
        print(f"Received message with length {len(msg.data())} topic: {msg.topic_name()} stream: {msg.partition_key()}")  
        image_bytes = base64.b64decode(buffer)
        image_np = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        frame = draw_labels(frame, data["metadata"])
        cv2.imshow(stream, frame)
        cv2.waitKey(1)
        consumer.acknowledge(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topic", type=str, default="result-surveillance", help="Topic name"
    )
    parser.add_argument(
        "--subscription", type=str, default="operator", help="Subscription"
    )
    parser.add_argument(
        "--pulsar_host", type=str, default="pulsar://localhost:6650", help="Pulsar host"
    )
    args = parser.parse_args()
    main(args)
