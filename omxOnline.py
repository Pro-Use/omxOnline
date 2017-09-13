import sys
import getopt
import glob
import os
from re import escape
from omxplayer import OMXPlayer
from flask import Flask, render_template, session, request, jsonify, abort
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from threading import Lock


def setup():
    directory = "/home/pi/video/"
    files = glob.glob(directory + '[a-zA-Z0-9]*.*')
    sync = None
    audio = 'local'
    helpstr = '\nomxOnline usage:\n \
        -h print this help message and exit\n \
        -f <file>               full path\n \
        -d <directory> \n \
        -s [master | slave]     sync mode\n \
        -o [local | hdmi | alsa]    audio output\n'

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:d:s:o:")
    except getopt.GetoptError:
        print(helpstr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helpstr)
            sys.exit(2)
        elif opt == '-d':
            if not os.path.exists(arg):
                print('\n%s is not a valid directory\n' % arg)
                sys.exit(2)
            if '-f' in opts:
                print('\nDirectory and file both specified, ignoring directory %s\n' % arg)
            else:
                directory = arg
                files = glob.glob(directory + '[a-zA-Z0-9]*.*')
        elif opt == '-f':
            if not os.path.isfile(arg):
                print('\nCannot find file %s\n' % arg)
                sys.exit(2)
            files = [arg]
        elif opt == '-s':
            if arg not in ['slave', 'master']:
                print('\n"%s" is not a valid sync mode, must be either "master" or "slave"\n' % arg)
                sys.exit(2)
            sync = arg
        elif opt == '-o':
            if arg not in ['local', 'hdmi', 'alsa']:
                print('\n"%s" is not a valid audio output, must be either "local", "hdmi" or "alsa"\n' % arg)
                sys.exit(2)
            audio = arg
        for f in range(0, len(files)):
            files[f] = escape(files[f])
    return directory, files, sync, audio


def setup_sync(sync, files):
    if sync:
            if len(files) > 1:
                print('\ncannot sync multiple files,'
                      ' please specify a file or choose a different directory in order to sync\n')
                sys.exit(2)
            # from omxsync import Broadcaster


def api_server(player, sync_ctl=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app, async_mode='gevent')

    @app.route('/')
    def eyetrack():
        filename = player.get_filename().split('/')[0]
        duration = player.duration()
        return render_template('index.html', async_mode=socketio.async_mode,
                               filename=filename,
                               duration=duration)

    socketio.run(app, debug=True, host='0.0.0.0')

if __name__ == '__main__':
    DIRECTORY, FILES, SYNC, AUDIO = setup()
    print(DIRECTORY, FILES, SYNC, AUDIO)
    PLAYER = OMXPlayer(FILES[0], args=['-o', AUDIO, '--no-osd', '--loop'], pause=True)
    api_server(PLAYER)
    PLAYER.stop()
