from confluent_kafka import Consumer
import numpy as np
import cv2
import pickle
import base64
# Configuration for Kafka Consumer
conf = {
    "bootstrap.servers": "localhost:9092",  # Replace with your Kafka broker's address
    "group.id": "my_consumer_group",  # Consumer group ID
    "auto.offset.reset": "latest",  # Start reading at the earliest offset
}

# Create Consumer instance
consumer = Consumer(conf)

# Subscribe to a topic
topic = "test_topic"
consumer.subscribe([topic])

try:
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
        cv2.imshow(stream, frame)
        cv2.waitKey(1)

        print(f"Received {len(msg.value())} bytes from {msg.topic()}  [{msg.partition()}] offset {msg.offset()}]")
finally:
    # Close down consumer to commit final offsets
    consumer.close()
