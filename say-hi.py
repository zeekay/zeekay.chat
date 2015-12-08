#!/usr/bin/env python
#
# Minimal IRC client. Compatible with Python 2 and 3.
import os, select, signal, socket, sys, time

try:    username = os.getlogin()
except: username = "unknown"

hostname = socket.gethostname()
irc      = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if not sys.stdin.isatty():
    sys.stdin = open('/dev/tty')

send = lambda s: irc.send(s.encode('UTF-8'))

def hello():
    send('PRIVMSG zeekay :hello, i am from the internet!\r\n')
    sys.stdout.write('> ')
    sys.stdout.flush()

def goodbye(*args):
    send('DISCONNECT')
    print('\nbye!')
    sys.exit(0)

signal.signal(signal.SIGINT, goodbye)

print('Hi {0}! Poking zk... (press CTRL-C to exit)'.format(username))
irc.connect(('irc.freenode.net', 6667))
send('NICK i_am_{0}\r\n'.format(username))
send('USER {0} {1} irc.freenode.net :{0}\r\n'.format(username, hostname))

while True:
    read, write, error = select.select([sys.stdin, irc], [], [], 0.01)

    for i in read:
        if i == sys.stdin:
            line = i.readline()
            if line.startswith('/'):
                send(line[1:])
            send('PRIVMSG zeekay :{0}\r\n'.format(line))
            sys.stdout.write('> ')
            sys.stdout.flush()

        elif i == irc:
            buffer = i.recv(1024)
            for line in buffer.splitlines():
                try:
                    _, info, line = line.decode('utf-8').split(':', 2)
                except ValueError:
                    break
                server, type = info.split(' ')[:2]
                if type == 'PRIVMSG':
                    sys.stdout.write('\x08' * 2)
                    sys.stdout.write('< {0}\n> '.format(line))
                    sys.stdout.flush()
                elif line.startswith('This server was created'):
                    hello()
                else:
                    print(line)
