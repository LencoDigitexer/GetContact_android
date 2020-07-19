from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch


import requests
import base64
import time
import hmac
import hashlib
import binascii
import json
from Crypto import Random
from Crypto.Cipher import AES

AES_KEY = 'e62efa9ff5ebbc08701f636fcb5842d8760e28cc51e991f7ca45c574ec0ab15c' # Юзайте пока работает :)
TOKEN = 'hjiZQ512eb3247fcf22952f1d9b2af80cf0459450e54eb422dd20798c04'

key = b'2Wq7)qkX~cp7)H|n_tc&o+:G_USN3/-uIi~>M+c ;Oq]E{t9)RC_5|lhAA_Qq%_4'

class AESCipher(object):

    def __init__(self, AES_KEY): 
        self.bs = AES.block_size
        self.AES_KEY = binascii.unhexlify(AES_KEY)

    def encrypt(self, raw):
        raw = self._pad(raw)
        cipher = AES.new(self.AES_KEY, AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.AES_KEY, AES.MODE_ECB)
        return self._unpad(cipher.decrypt(enc)).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


aes = AESCipher(AES_KEY)

class MainApp(MDApp):

    def sendPost(self, url, data, sig, ts):
        headers = {'X-App-Version': '4.9.1',
            'X-Token':TOKEN,
            'X-Os': 'android 5.0',
            'X-Client-Device-Id': '14130e29cebe9c39',
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Encoding': 'deflate',
            'X-Req-Timestamp': ts,
            'X-Req-Signature': sig,
            'X-Encrypted': '1'}
        r = requests.post(url, data=data, headers=headers, verify=True)
        return json.loads(aes.decrypt(r.json()['data']))

    def getByPhone(self, phone):
        ts = str(int(time.time()))
        req = f'"countryCode":"RU","source":"search","token":"{TOKEN}","phoneNumber":"{phone}"'
        req = '{'+req+'}'
        string = str(ts)+'-'+req
        sig = base64.b64encode(hmac.new(key, string.encode(), hashlib.sha256).digest()).decode()
        crypt_data = aes.encrypt(req)
        return self.sendPost('https://pbssrv-centralevents.com/v2.5/search',
                        b'{"data":"'+crypt_data+b'"}', sig, ts)

    def main(self, ins):
        phone = self.textinput.text
        if '+' not in phone:
            phone = '+'+phone
        print('======================')
        print(phone)
        finfo = self.getByPhone(phone)
        print("finfo " + str(finfo))
        try:
            if finfo['result']['profile']['displayName']:
                print(finfo['result']['profile']['displayName'])
                self.label.text = str(phone + " = " + finfo['result']['profile']['displayName'])
            if finfo['result']['profile']['displayName'] is None:
                self.label.text = str("Номера в базе нет")
        except: self.label.text = str("Неправильный номер")

    def switchTheme(self, value):
        print("test")
        self.theme_cls.theme_style = "Dark"

    def build(self):
        #self.theme_cls.theme_style = "Dark"
        bl = MDBoxLayout(orientation="vertical",  padding= "40dp",  spacing=40, adaptive_height= True)

        self.selection = MDSwitch(pos_hint= {'center_x': .5, 'center_y': .5}, on_release=self.switchTheme)
        self.label = MDLabel(text="Введите номер в поле", halign="center", theme_text_color="Primary")
        self.textinput = MDTextField(hint_text="Max text length = 11",  max_text_length="11", mode="rectangle", pos_hint={"center_x": .5, "center_y": .5}, padding= "40dp")
        self.button = MDRaisedButton(text="Определить номер", pos_hint={"center_x": .5}, on_press=self.main)
        
        #bl.add_widget(self.selection)
        bl.add_widget(self.label)
        bl.add_widget(self.textinput)
        #bl.add_widget(self.nulllabel)
        bl.add_widget(self.button)
        

        return bl


MainApp().run()