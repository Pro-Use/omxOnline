
import time
from argParser import setup
from omxplayer import OMXPlayer
from flask import Flask, render_template, session, request, jsonify, abort, Markup
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from threading import Lock
import glob

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
    files_str = ''
    get_files = glob.glob(directory + '[a-zA-Z0-9]*.*')
    for get_file in get_files:
        esc_file = get_file.replace(' ', '///')
        if get_file == files[0]:
            checked = 'checked'
        else:
            checked = ''
        files_str += '<td><i class="material-icons">&#xE02C;</i>'\
                     '%s<input type="radio" id="file" value="%s" %s> ' \
                     '</td>\n' % (get_file, get_file, checked)
    files_html = Markup(files_str)
    return render_template('index.html', async_mode=socketio.async_mode,
                           filename=filename,
                           duration=duration_str,
                           files=files_html)


@socketio.on('connect', namespace='/omxSock')
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=position_thread)


@socketio.on('ctl_event', namespace='/omxSock')
def ctl_message(message):
    print(message)
    if message == 'play_pause':
        global paused
        player.play_pause()
        paused = not paused

    elif message == 'skip_fwd':
        remaining = player.duration() - player.position()
        print(player.position())
        if remaining < 12:
            player.set_position(12 - remaining)
        else:
            player.set_position(player.position() + 10)
            print(player.position())

    elif message == 'skip_bwd':
        position = player.position()
        if position < 12:
            player.set_position(player.duration() - (12 - position))
        else:
            player.set_position(player.position() - 10)

@socketio.on('file_event', namespace='/omxSock')
def file_message(message):
    new_file = message
    print(new_file)

@socketio.on('disconnect', namespace='/omxSock')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False)
    player.stop()
