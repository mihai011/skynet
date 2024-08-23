# skynet
How China's video surveillance works?

![Alt text](skynet-terminator.webp "I need your clothes, boots and motorycle!")

To run this demo use the follwing commands:

Run the pulsar docker compose file:
```
docker compose up -d  
```
This will open a pulsar server locally at port 6650.
Create virtual environment:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install ngrok from official site by making an account:
then run the following command:
```
ngrok tcp 6650
```
to expose your local pulsar service to the reverse proxy.
Soon a domain name will be shown available to you that
can be usen by consumers to send traffic to your local 
service.