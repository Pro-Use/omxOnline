import sys
import getopt
import glob
import os
from re import escape


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
        if len(files) > 1:
            print('\ncannot sync multiple files,'
                  ' please specify a file or choose a different directory in order to sync\n')
            sys.exit(2)
    return directory, files, sync, audio
