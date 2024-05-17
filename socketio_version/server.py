from aiohttp import web
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


    
@sio.event
async def image(sid, data):
    print("image ", data)
    
@sio.event
def messsage(sid, data):
    sio.emit(data)
    print("message ", data)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def chat_message(sid, data):
    print("message", data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    web.run_app(app)