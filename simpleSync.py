from omxplayer import OMXPlayer
from omxsync import Receiver, Broadcaster
from time import sleep
import glob
import getopt
import sys
import os

receiver, broadcaster = None, None
files = glob.glob('/home/pi/video/[a-zA-Z0-9]*.*')
files.sort()
video_file = '%s' % files[0]
video_file.replace(' ', '\ ')
audio = 'local'
sync = 'master'
network = None
helpstr = '\nomxOnline usage:\n \
        -h print this help message and exit\n \
        -f <file>               full path\n \
        -s [master | slave]     sync mode\n \
        -o [local | hdmi | alsa]    audio output\n \
        -i [wired | wifi]      network interface\n'

try:
    opts, args = getopt.getopt(sys.argv[1:], "hf:s:o:i")
except getopt.GetoptError:
    print(helpstr)
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print(helpstr)
        sys.exit(2)
    elif opt == '-f':
        if not os.path.isfile(arg):
            print('\nCannot find file %s\n' % arg)
            sys.exit(2)
        video_file = arg
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
    elif opt == '-i':
        if arg not in ['wired', 'wifi']:
            print('\n"%s" is not a valid network interface, must be either "wired" or "wifi"\n' % arg)
            sys.exit(2)
        network = arg

if sync == 'slave':
    player = OMXPlayer(video_file, args=['-o', audio, '--no-osd', '--loop'])
    receiver = Receiver(player, verbose=True, interface=network)
else:
    player = OMXPlayer(video_file, args=['-o', 'local', '--no-osd', '--loop'])
    broadcaster = Broadcaster(player, interval=0.5, verbose=True, interface=network)

print('Sync %s: starting %s' % (sync, video_file))
while True:
    try:
        sleep(1)
    except (KeyboardInterrupt, SystemExit):
        player.stop()
        if sync == 'master':
            broadcaster.destroy()
        sleep(1)
        break

