#http://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent

#from gevent import monkey
# monkey.patch_all()

# Re-add sslwrap to Python 2.7.9
# https://github.com/gevent/gevent/issues/477#issuecomment-56292848
import inspect
__ssl__ = __import__('ssl')

try:
    _ssl = __ssl__._ssl
except AttributeError:
    _ssl = __ssl__._ssl2


def new_sslwrap(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=__ssl__.CERT_NONE, ssl_version=__ssl__.PROTOCOL_SSLv23, ca_certs=None, ciphers=None):
    context = __ssl__.SSLContext(ssl_version)
    context.verify_mode = cert_reqs or __ssl__.CERT_NONE
    if ca_certs:
        context.load_verify_locations(ca_certs)
    if certfile:
        context.load_cert_chain(certfile, keyfile)
    if ciphers:
        context.set_ciphers(ciphers)

    caller_self = inspect.currentframe().f_back.f_locals['self']
    return context._wrap_socket(sock, server_side=server_side, ssl_sock=caller_self)

if not hasattr(_ssl, 'sslwrap'):
    _ssl.sslwrap = new_sslwrap
##############


import time
import json
import boto
import Scroller
from threading import Thread
from flask import Flask, render_template
from flask.ext.socketio import SocketIO

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)
thread = None

def squaresEmitter(squares):
    socketio.emit('my response', squares, namespace='/test')

def background_thread():
    print "starting thread"
    sqs = boto.sqs.connect_to_region("us-west-2")
    queue = boto.sqs.queue.Queue(sqs, "http://us-west-2.queue.amazonaws.com/612895797421/NeopixelText")
    s = Scroller.Scroller(squaresEmitter)
    s.scrollText("getting started...", 0, 255, 0)

    while True:
        messages = queue.get_messages(num_messages=1, wait_time_seconds=10)
        for m in messages:
            body = json.loads(m.get_body())
            message = body["Message"]
            for item in message.split("\n"):
                if item.startswith('LogicalResourceId=') or item.startswith('ResourceStatus='):
                    item = item.replace("LogicalResourceId='", "")
                    item = item.replace("ResourceStatus='", "")
                    item = item.replace("'", "")
                    print item
                    s.scrollText(item, 0, 0, 255)
            queue.delete_message(m)



@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    print 'Client connected'
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print 'Client disconnected'


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
