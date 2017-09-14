
import time
from argParser import setup
from omxplayer import OMXPlayer
from flask import Flask, render_template, session, request, jsonify, abort
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from threading import Lock

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')
thread = None
thread_lock = Lock()
directory, files, sync, audio = setup()
player = OMXPlayer(files[0], args=['-o', audio, '--no-osd', '--loop'])
duration = player.duration()
duration_percent = 100 / duration
duration_str = time.strftime('%H:%M:%S', time.gmtime(duration))
filename = player.get_filename().split('/')[-1]
paused = False


def position_thread():
    while True:
        socketio.sleep(1)
        pos = player.position()
        percentage = duration_percent * pos
        pos = time.strftime('%H:%M:%S', time.gmtime(pos))
        socketio.emit('position',
                      {'position': pos, 'percentage': percentage, 'paused': paused},
                      namespace='/omxSock')


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode,
                           filename=filename,
                           duration=duration_str)


@socketio.on('connect', namespace='/omxSock')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=position_thread)


@socketio.on('my_event', namespace='/omxSock')
def ctl_message(message):
    print(message)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False)
    player.stop()
