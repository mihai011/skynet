import pulsar

client = pulsar.Client('pulsar://localhost:6650')

consumer = client.subscribe('result-surveilance', 'operator')
data = []
while True:
    msg = consumer.receive()
    try:
        # Acknowledge successful processing of the message
        consumer.acknowledge(msg)
    except Exception:
        # Message failed to be processed
        consumer.negative_acknowledge(msg)
        break

client.close()