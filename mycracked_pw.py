import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import os


class MyCrackedPasswords(plugins.Plugin):
    __author__ = '@silentree12th'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin to grab and sort all cracked passwords to use with quickdic-plugin'

    def on_loaded(self):
        logging.info("mycracked_pw loaded")

    def on_handshake(self):
        if not os.path.exists('/home/pi/wordlists/'):
            os.makedirs('/home/pi/wordlists/')
        # start with blank files
        open('/home/pi/wordlists/mycracked.txt', 'w+').close()
        f=open('/root/handshakes/wpa-sec.cracked.potfile', 'r+')
        new_lines=[]
        for line in f:
            pwd=line.split(':')
            new_lines.append(pwd[-1])
        f.close()
        new_lines = sorted(set(new_lines))
        g=open('/home/pi/wordlists/mycracked.txt','w+')
        with open('/home/pi/wordlists/mycracked.txt','w+') as g:
            for i in new_lines:
                g.write(i+"")
        g.close()
