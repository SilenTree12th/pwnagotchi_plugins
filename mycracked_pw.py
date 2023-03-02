import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import qrcode
import html
import csv
import os
import io


class MyCrackedPasswords(plugins.Plugin):
    __author__ = '@silentree12th'
    __version__ = '4.2.7'
    __license__ = 'GPL3'
    __description__ = 'A plugin to grab and sort all cracked passwords to use with quickdic-plugin'

    def on_loaded(self):
        if not os.path.exists('/home/pi/wordlists/'):
            os.makedirs('/home/pi/wordlists/')
            
        if not os.path.exists('/home/pi/qrcodes/'):
            os.makedirs('/home/pi/qrcodes/')
            
        # start with blank file
        open('/home/pi/wordlists/mycracked.txt', 'w+').close()
        
        all_passwd=[]
        all_bssid=[]
        all_ssid=[]
        f=open('/root/handshakes/wpa-sec.cracked.potfile', 'r+')
        for line_f in f:
            pwd_f = line_f.split(':')
            all_passwd.append(pwd_f[-1])
            all_bssid.append(pwd_f[0])
            all_ssid.append(pwd_f[-2])
        f.close()
        
        h = open('/root/handshakes/onlinehashcrack.cracked', 'r+')
        for line_h in csv.DictReader(h):
            pwd_h = line_h['password']
            bssid_h = line_h['BSSID'][1:-1]
            ssid_h = line_h['ESSID'][1:-1]
            if pwd_h and bssid_h and ssid_h:
                all_passwd.append(pwd_h)
                all_bssid.append(bssid_h)
                all_ssid.append(ssid_h)
        h.close()
        
        #create pw list
        new_lines = sorted(set(all_passwd))
        g=open('/home/pi/wordlists/mycracked.txt','w+')
        with open('/home/pi/wordlists/mycracked.txt','w+') as g:
            for i in new_lines:
                g.write(i+"")
        g.close()
        
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
            filepath = os.path.join("/home/pi/qrcodes/", filename)
            try:
                with open(filepath, 'w+') as file:
                    qr_code.print_ascii(out=file)
            except:
                logging.error("%s could not be generated as qrcode" %filename)
        logging.info("[mycracked_pw] qrcodes generated. use cat file to see it.")
