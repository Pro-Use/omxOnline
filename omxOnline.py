
import time
from argParser import setup
from flask import Flask, render_template, Markup, flash
from flask_socketio import SocketIO
from threading import Lock, Event, Thread
import glob
from dbus import DBusException
from omxplayer import player as PLAYER
from subprocess import call

app = Flask(__name__)
app.secret_key = b')\x9c\xc7\xa7\xb3\xd2\xa9\x8ch\xd6\xc9\xfc\xe6g!c'
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
sync_ctl_thread = None
sync_pause = Event()


def sync_thread(e):
    global deviation
    print('syncing started')
    while not e.isSet():
        try:
            sync_ctl.update()
        except DBusException:
            pass
    print('syncing stopped')
    if sync == 'slave':
        deviation = 'Not syncing'


def position_thread():
    global deviation
    while True:
        try:
            socketio.sleep(1)
            pos = player.position()
            percentage = duration_percent * pos
            pos = time.strftime('%H:%M:%S', time.gmtime(pos))
            if sync == 'slave':
                if sync_ctl.duration_match is True:
                    deviation = '%.2f seconds' % sync_ctl.median_deviation
                else:
                    deviation = 'Master/Slave durations do not match'
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
        except PLAYER.OMXPlayerDeadError, msg:
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
        call('sudo systemctl poweroff', shell=True)

    elif message == 'restart':
        call('sudo reboot', shell=True)


@socketio.on('file_event', namespace='/omxSock')
def file_message(message):
    global player, duration, duration_percent, duration_str, filename, sync_ctl, sync_ctl_thread
    sync_pause.set()
    new_file = message.replace('///', ' ')
    print(new_file)
    playing = player.get_filename()
    try:
        player.load(new_file)
    except SystemError:
        player = PLAYER.OMXPlayer(playing, args=['-o', audio, '--no-osd', '--loop'])
        time.sleep(1)
    duration = player.duration()
    duration_percent = 100 / duration
    duration_str = time.strftime('%H:%M:%S', time.gmtime(duration))
    filename = player.get_filename().split('/')[-1]
    write_config('FILE', filename)
    if sync is not None:
        if sync == 'slave':
            sync_ctl.duration_match = None
        sync_ctl_thread = Thread(target=sync_thread, args=[sync_pause])
        sync_ctl_thread.start()
    sync_pause.clear()
    return filename


if __name__ == '__main__':
    if sync is not None:
        sync_ctl_thread = Thread(target=sync_thread, args=[sync_pause])
        sync_ctl_thread.start()
    socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False)
    sync_pause.set()
    sync_ctl.socket.close()
    player.stop()
