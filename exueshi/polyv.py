import re
import json
import base64
import hashlib
import binascii
import requests
from Crypto.Cipher import AES
from Crypto.Util import Padding

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/84.0.4147.105'' Safari/537.36'
    ),
}


class PolyvParser:

    def __init__(self, vid: str):
        self.vid = vid # type: str
        self.token = None # type: str
        self._toekn = None # type: str
        self.hls = None # type: list
        self.body = None # type: dict

    def decrypt_body(self, body: str):
        vid_md5 = self.get_vid_md5()
        body_raw = binascii.a2b_hex(body)
        aes_key = bytes([ord(_) for _ in vid_md5[:16]])
        aes_iv = bytes([ord(_) for _ in vid_md5[16:]])
        cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)
        body_plain = Padding.unpad(cipher.decrypt(body_raw), 16).decode('utf-8')
        body_plain = body_plain.replace('-', '+').replace('_', '/')
        body_decodeed = base64.b64decode(body_plain.encode('utf-8')).decode('utf-8')
        self.body = json.loads(body_decodeed)
        print(f'解密body成功')

    def get_vid_md5(self) -> str:
        return hashlib.new('md5', self.vid.encode('utf-8')).hexdigest()

    def get_token(self, prodID: str, vid: str):
        s = requests.Session()
        url = f'https://www.exueshi.com/play/{prodID}'
        print(f'开始解析 -> {url}')
        try:
            r = s.get(url, headers=headers, timeout=3)
            self._toekn = re.findall('name="_token" content="(.*?)"', r.content.decode('utf-8'))[0]
        except Exception as e:
            raise e
        print(f'获取_token成功 -> {self._toekn}')
        url = 'https://www.exueshi.com/play/privilege'
        data = {
            'prodID': prodID.capitalize(),
            'prodContentID': vid,
            'videoId': vid,
            'prodContentType': '视频',
            '_token': self._toekn,
        }
        _headers = headers.copy()
        _headers['X-Requested-With'] = 'XMLHttpRequest'
        try:
            r = s.post(url, data=data, headers=_headers, timeout=3)
            self.token = r.json()['msg']['token']
        except Exception as e:
            raise e
        print(f'获取token成功 -> {self.token}')

    def fetch_vid_body(self):
        url = f'https://player.polyv.net/secure/{self.vid}.json'
        try:
            r = requests.get(url, headers=headers, timeout=3)
            body = json.loads(r.content.decode('utf-8'))['body']
        except Exception as e:
            raise e
        print(f'获取body成功')
        self.decrypt_body(body)

    def parse_body(self):
        print(self.body['weburl'], self.body['title'])
        for hls, res in zip(self.body['hls'], self.body['resolution']):
            print(f'{res} {hls}')


def main():
    prodID = 'p201903981228671dd33a_5'
    vid = 'd06ae002cb4a0bed78fb912c874fdbb2_d'
    parser = PolyvParser(vid)
    parser.get_token(prodID, vid)
    parser.fetch_vid_body()
    parser.parse_body()


if __name__ == '__main__':
    main()