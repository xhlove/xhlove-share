import re
import json
import base64
import hashlib
import binascii
import requests
from pathlib import Path
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
        self.minSeekHole = None # type: float
        self.session = requests.Session()

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
        url = f'https://www.exueshi.com/play/{prodID}'
        print(f'开始解析 -> {url}')
        try:
            r = self.session.get(url, headers=headers, timeout=3)
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
            r = self.session.post(url, data=data, headers=_headers, timeout=3)
            self.token = r.json()['msg']['token']
        except Exception as e:
            raise e
        print(f'获取token成功 -> {self.token}')

    def fetch_vid_body(self):
        url = f'https://player.polyv.net/secure/{self.vid}.json'
        try:
            r = self.session.get(url, headers=headers, timeout=3)
            body = json.loads(r.content.decode('utf-8'))['body']
        except Exception as e:
            raise e
        print(f'获取body成功')
        self.decrypt_body(body)

    def fetch_url(self, url: str, filename: str = None) -> bytes:
        r = None # type: requests.Response
        try:
            r = self.session.get(url, headers=headers, timeout=3)
        except Exception as e:
            print(f'请求发生错误 -> {e}\n\t{url}')
            return
        if r and r.status_code == 200:
            if filename is not None:
                Path(filename).write_bytes(r.content)
            return r.content

    def parse_body(self):
        self.minSeekHole = self.body['seed_const'] / 2
        print(self.body['weburl'], self.body['title'])
        for m3u8_url, res in zip(self.body['hls'], self.body['resolution']):
            print(f'{res} {m3u8_url}')
            filename = m3u8_url.split('?')[0].split('/')[-1].replace('.m3u8', '') + '.m3u8'
            m3u8_content = self.fetch_url(m3u8_url, filename)
            self.decrypt_key(m3u8_url, m3u8_content.decode('utf-8'))

    def decrypt_key(self, m3u8_url: str, content: str):
        key_iv = re.findall('#EXT-X-KEY:METHOD=AES-128,URI="(.*?)",IV=0x(.*)', content)
        if len(key_iv) == 0:
            print('未匹配到key url')
            return
        key_url, hex_iv = key_iv[0]
        _key_url = key_url.split('/') # type: list
        _key_url.insert(3, 'playsafe')
        key_url = f'{"/".join(_key_url)}?token={self.token}'
        filename = key_url.split('?')[0].split('/')[-1].replace('.key', '') + '.key'
        key = self.fetch_url(key_url, filename=filename)
        if key is None:
            return
        # print(list(key))
        # key = bytes([90, 166, 207, 180, 5, 206, 47, 45, 247, 64, 32, 96, 237, 75, 42, 239, 10, 4, 221, 239, 254, 42, 135, 231, 4, 102, 242, 86, 146, 137, 252, 187])
        # minSeekHole = 71
        # print(self.minSeekHole)
        ky = hashlib.new('md5', str(int(2 * self.minSeekHole)).encode('utf-8')).hexdigest()
        aes_key = ky[:16].encode('utf-8')
        _fake_iv = [2, 4, 6, 10, 14, 22, 26, 34, 38, 46, 58, 14, 10, 6, 4, 2]
        aes_iv = bytes([int(_ / 2) for _ in _fake_iv])
        cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)
        key_plain = cipher.decrypt(key)[:16]
        # print(list(key_plain))
        b64key = base64.b64encode(key_plain).decode('utf-8')
        print(f'N_m3u8DL-CLI_v2.9.4.exe "{m3u8_url}" --useKeyBase64 "{b64key}" --useKeyIV "{hex_iv}"')


def main():
    prodID = 'p201903981228671dd33a_5'
    vid = 'd06ae002cb4a0bed78fb912c874fdbb2_d'
    parser = PolyvParser(vid)
    parser.get_token(prodID, vid)
    parser.fetch_vid_body()
    parser.parse_body()


if __name__ == '__main__':
    main()