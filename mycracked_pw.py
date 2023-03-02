import pwnagotchi.plugins as plugins
import logging
import qrcode
import csv
import os


class MyCrackedPasswords(plugins.Plugin):
    __author__ = '@silentree12th'
    __version__ = '4.2.5'
    __license__ = 'GPL3'
    __description__ = 'A plugin to grab and sort all cracked passwords to use with quickdic-plugin'
    __defaults__ = {
        'enabled': False,
        'wordlist_folder': '/home/pi/wordlists/',
        'qrcodes_folder': '/home/pi/qrcodes/', 
        'face': '(uωu)',
    }

    def on_loaded(self):
        logging.info('[mycracked_pw] loaded')
        if 'face' not in self.options:
            self.options['face'] = '(uωu)'
        if 'wordlist_folder' not in self.options:
            self.options['wordlist_folder'] = '/home/pi/wordlists/'
        if 'wordlist_folder' not in self.options:
            self.options['qrcodes_folder'] = '/home/pi/qrcodes/'
        if 'enabled' not in self.options:
            self.options['enabled'] = False
        
        wordlist_folder = self.options['wordlist_folder']
        qrcodes_folder = self.options['qrcodes_folder']
        
        if not os.path.exists(wordlist_folder):
            os.makedirs(wordlist_folder)
            
        if not os.path.exists(qrcodes_folder):
            os.makedirs(qrcodes_folder)
            
        # start with blank file
        path_wordlist = os.path.join(wordlist_folder, "my_cracked.txt")
        open(path_wordlist, 'w+').close()
        
        all_passwd=[]
        all_bssid=[]
        all_ssid=[]
        
        wpa_sec = '/root/handshakes/wpa-sec.cracked.potfile'
        if os.path.exists(wpa_sec):
            f=open(wpa_sec, 'r+')
            for line_f in f:
                pwd_f = line_f.split(':')
                all_passwd.append(pwd_f[-1])
                all_bssid.append(pwd_f[0])
                all_ssid.append(pwd_f[-2])
            f.close()
        else:
            logging.info('[mycracked_pw] no cracked pw for wpa-sec found')
        
        onlinehashcrack = '/root/handshakes/onlinehashcrack.cracked'
        if os.path.exists(onlinehashcrack):
            h = open(onlinehashcrack, 'r+')
            for line_h in csv.DictReader(h):
                pwd_h = line_h['password']
                bssid_h = line_h['BSSID']
                ssid_h = line_h['ESSID']
                if pwd_h != None:
                    all_passwd.append(pwd_h)
                    all_bssid.append(bssid_h)
                    all_ssid.append(ssid_h)
            h.close()
        else:
            logging.info('[mycracked_pw] no cracked pw for onlinehashcrack found')
        
        #create pw list
        new_lines = sorted(set(all_passwd))
        with open(path_wordlist,'w+') as g:
            for i in new_lines:
                g.write(i+"")
        
        logging.info("[mycracked_pw] pw list updated")
        
        #save all the wifi-qrcodes
        security="WPA"
        for ssid,password,bssid in zip(all_ssid, all_passwd, all_bssid):
            wifi_config = f"WIFI:S:{ssid};T:{security};P:{password};;"
            
            # Create the QR code object
            qr_code = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_code.add_data(wifi_config)
            qr_code.make(fit=True)
            
            filename = f"{ssid}-{bssid}.txt"
            path_qrcode = os.path.join(qrcodes_folder, filename)
            with open(path_qrcode, 'w+') as file:
                qr_code.print_ascii(out=file)
        logging.info("[mycracked_pw] qrcodes generated. use cat file to see it.")
