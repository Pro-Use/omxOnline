import sys
import getopt
import glob
import os
from omxplayer import OMXPlayer
from mimetypes import guess_type
from omxsync import Receiver, Broadcaster


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
    files.sort()
    print files
    config_file = '/home/pi/.omxOnline.config'
    if os.path.isfile(config_file):
        with open(config_file, 'r') as config:
            for line in config:
                if 'FILE' in line:
                    files = [line.replace('\n', '').replace('FILE ', '')]
    if len(files) > 1 and sync:
        print('\ncannot sync multiple files, looping %s\n' % files[0])
    player = None
    for media_file in files:
        print media_file
        # esc_media_file = media_file
        mime_type = guess_type(media_file)
        print mime_type
        if any(f in str(mime_type[0]) for f in ['audio', 'video']):
            try:
                player = OMXPlayer(media_file, args=['-o', audio, '--no-osd', '--loop'])
                break
            except SystemError, msg:
                print(msg)
                files.remove(media_file)
        else:
            print("'audio' or 'video' not in %s for %s" % (mime_type[0], media_file))
            files.remove(media_file)
    if player is None:
        print('\nNo video to play in specified directory\n')
        sys.exit(2)
    sync_ctl = None
    if sync == 'slave':
        sync_ctl = Receiver(player, verbose=True, background=False)
    elif sync == 'master':
        sync_ctl = Broadcaster(player, interval=0.5, verbose=False, background=False)
    return directory, files, sync, audio, player, sync_ctl
