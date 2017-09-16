
import time
from argParser import setup
from flask import Flask, render_template, session, request, jsonify, abort, Markup
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from threading import Lock
import glob
from dbus import DBusException
from omxplayer import OMXPlayer
from omxsync import Receiver, Broadcaster
import os

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')
thread = None
thread_lock = Lock()
directory, files, sync, audio, player, sync_ctl = setup()
duration = player.duration()
duration_percent = 100 / duration
duration_str = time.strftime('%H:%M:%S', time.gmtime(duration))
filename = player.get_filename().split('/')[-1]
paused = False
deviation = False
config_file = '/home/pi/.omxOnline.config'


def position_thread():
    while True:
        try:
            global deviation
            socketio.sleep(1)
            pos = player.position()
            percentage = duration_percent * pos
            pos = time.strftime('%H:%M:%S', time.gmtime(pos))
            if sync == 'slave':
                deviation = '%.2f' % sync_ctl.median_deviation
                is_paused = not paused
            else:
                is_paused = paused
            socketio.emit('position',
                          {'position': pos, 'duration': duration, 'duration_str': duration_str,
                           'percentage': percentage, 'paused': is_paused, 'filename': filename, 'deviation': deviation},
                          namespace='/omxSock')
        except DBusException, msg:
            print(msg)
            pass


def write_config(arg, value):
    with open(config_file, 'w+') as config:
        config.write('%s %s\n' % (arg, value))


@app.route('/')
def index():
    files_str = ''
    get_files = glob.glob(directory + '[a-zA-Z0-9]*.*')
    for get_file in get_files:
        if get_file == player.get_filename():
            class_str = 'playing'
        else:
            class_str = 'not-playing'
        esc_file = get_file.replace(' ', '///')
        files_str += '<tr><td class=%s><button class="new-file" value=%s>' \
                     '<i class="material-icons">&#xE02C;</i>%s' \
                     '</button></td></tr>\n' % (class_str, esc_file, get_file)
    files_html = Markup(files_str)
    index_file = 'index.html'
    if sync == 'slave':
        index_file = 'index-slave.html'
    elif sync == 'master':
        index_file = 'index-master.html'
    return render_template(index_file, async_mode=socketio.async_mode,
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

    elif 'seek' in message:
        seek_ctl = message.split(':')
        new_pos = float(seek_ctl[1])
        if new_pos > player.duration():
            new_pos = 0
        player.set_position(new_pos)

    elif message == 'power_off':
        os.system('systemctl poweroff')

    elif message == 'restart':
        os.system('reboot')


@socketio.on('file_event', namespace='/omxSock')
def file_message(message):
    global player, duration, duration_percent, duration_str, filename, sync_ctl
    new_file = message.replace('///', ' ')
    print(new_file)
    playing = player.get_filename()
    try:
        player.load(new_file)
    except SystemError:
        player = OMXPlayer(playing, args=['-o', audio, '--no-osd', '--loop'])
    # sync_ctl.destroy()
    # if sync is not None:
    #     if sync == 'slave':
    #         sync_ctl = Receiver(player, verbose=False)
    #     elif sync == 'master':
    #         sync_ctl = Broadcaster(player, interval=0.5, verbose=False)
    duration = player.duration()
    duration_percent = 100 / duration
    duration_str = time.strftime('%H:%M:%S', time.gmtime(duration))
    filename = player.get_filename().split('/')[-1]
    write_config('FILE', new_file)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False)
    player.stop()
