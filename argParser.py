import sys
import getopt
import glob
import os
from re import escape
from omxplayer import OMXPlayer
from mimetypes import guess_type

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
    if len(files) > 1 and sync:
        print('\ncannot sync multiple files, looping %s\n' % files[0])
    player = None
    for media_file in files:
        # esc_media_file = media_file
        if 'audio' or 'video' not in guess_type(media_file)[0]:
            files.remove(media_file)
        else:
            try:
                player = OMXPlayer(media_file, args=['-o', audio, '--no-osd', '--loop'])
                break
            except SystemError:
                files.remove(media_file)
    if player is None:
        print('\nNo video to play in specified directory\n')
        sys.exit(2)
    return directory, files, sync, audio, player
