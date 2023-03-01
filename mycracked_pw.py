import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import csv
import os


class MyCrackedPasswords(plugins.Plugin):
    __author__ = '@silentree12th'
    __version__ = '3.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin to grab and sort all cracked passwords to use with quickdic-plugin'

    def on_loaded(self):
        if not os.path.exists('/home/pi/wordlists/'):
            os.makedirs('/home/pi/wordlists/')
            
        # start with blank file
        open('/home/pi/wordlists/mycracked.txt', 'w+').close()
        
        all_lines=[]
        f=open('/root/handshakes/wpa-sec.cracked.potfile', 'r+')
        for line_f in f:
            pwd_f = line_f.split(':')
            all_lines.append(pwd_f[-1])
        f.close()
        
        h = open('/root/handshakes/onlinehashcrack.cracked', 'r+')
        for line_h in csv.DictReader(h):
            pwd_h = line_h['password']
            if pwd_h != None:
                all_lines.append(pwd_h)
        h.close()
        new_lines = sorted(set(all_lines))
        g=open('/home/pi/wordlists/mycracked.txt','w+')
        with open('/home/pi/wordlists/mycracked.txt','w+') as g:
            for i in new_lines:
                g.write(i+"")
        g.close()
        
        logging.info("[mycracked_pw] pw list updated")
