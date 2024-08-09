# skynet
How China's video surveillance works?



To run this demo use the follwing commands:

Run the pulsar docker compose file:
```
docker compose up -d  
```
Create virtual environment:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install ngrok from official site by making an account:
then erun the following command:
```
ngrok tcp <local_port_server>
```