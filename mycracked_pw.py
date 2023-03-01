import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import os


class MyCrackedPasswords(plugins.Plugin):
    __author__ = '@silentree12th'
    __version__ = '2.0.3'
    __license__ = 'GPL3'
    __description__ = 'A plugin to grab and sort all cracked passwords to use with quickdic-plugin'

    def on_loaded(self):
        logging.info("mycracked_pw loaded")

    def on_handshake(self, agent, filename, access_point, client_station):
        if not os.path.exists('/home/pi/wordlists/'):
            os.makedirs('/home/pi/wordlists/')
            
        # start with blank file
        open('/home/pi/wordlists/mycracked.txt', 'w+').close()
        
        all_lines=[]
        f=open('/root/handshakes/wpa-sec.cracked.potfile', 'r+')
        for line_f in f:
            pwd_f = line_f.split(':')[-1]
            all_lines.append(pwd_f)
        f.close()
        
        h=open('/root/handshakes/onlinehashcrack.cracked', 'r+')
        for line_h in h:
            pwd_h = line_h.split(',')[-2]
            if len(pwd_h) > 2:
                all_lines.append(pwd_h[1:-1])
        h.close()
        new_lines = sorted(set(all_lines))
        g=open('/home/pi/wordlists/mycracked.txt','w+')
        with open('/home/pi/wordlists/mycracked.txt','w+') as g:
            for i in new_lines:
                g.write(i+"")
        g.close()
        
        logging.info("mycracked.txt updated")
