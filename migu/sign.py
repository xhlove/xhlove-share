import time
import hashlib
from random import randint

SALT_TABLE = [
    '9b49eed02d9240aeabeb782860cc6be2',
    'd34d010b674341b0b31d60118370e3e7',
    '551c102e19a74dbbbaadf82e0f603725',
    'a49d1441c2ef4ec3881ee03975ed9e64',
    'f9580a84a68b4ff9aface3fac135203a',
    'afef8c8c9ccf47bd9ff5abddffbfab06',
    '49d91578d4cb48a89c91a8f29648d884',
    '41df4cf1d6194f38ae6f8901326f27ea',
    'dd3c4050bba845acbd40d4ebd59f60f9',
    '20d530788ec54dfaa998f564fa0eed54',
    '2dd7693907354fa49e271eeba79a3c3d',
    '7ca04529cd1445e2b8b4df2edf982944',
    '8a8631b96f394283b65c8acc7b118ef6',
    '9730e9e2521d42829fcce6c47ee6e714',
    '0062ddbfd9994cdea21bcfbe8822469b',
    '-',
    'af10e55f740549e293a9d8793094557e',
    '325e13e4d0b6424a9041ce9a6e2a0936',
    '9fb2c2e3d05d4ad8855dd057111a0372',
    '9955c67d6039457e897db4fbb0e4213e',
    '383f42c488e2446c8a209826c21e07a4',
    'ac7e796c016d437e95c4904edecb5706',
    '08509a488f674143a3a565e3672cc1f3',
    '56c8088875ac4d3981021f28795ee7cb',
    '87ff10e325e44ef5a865af4a9948d0cd',
    '3503b2aaa8a849d2a2c2a157594922d9',
    '62657b2522be4905b6396f6d4a45e42d',
    '6ef4148deffd487f887ad5e77eb8b639',
    '294146dd81e04d65bb3499dc2c531227',
    '778a2ea5e7254351aa3d7b0a6ee7a6a4',
    '7ab16383308f4aef80bb91816aaa1571',
    '9ecbdf2d1fdc43b1a9ebb7b703681d1b',
    '364ba40d5cd24cb9be9df68087b9ba50',
    '20c7028e5460482987821c8c8bd44d11',
    '1053bab67a544877a6124b13a1aafd6c',
    '9b8a02b7c3c044a8bae0d22e15296088',
    'cc97fc32d3234500beea4f2a866a5788',
    'a19ef2dee5db46a18e510770002b4108',
    '992e27034ca84cfb82cdaa43e1c1e739',
    '7c228f634ce94bdbbb11c89758f60c00',
    '8c8c596dee1247d09b4d4317af1ef731',
    '1a8957f176bc4739b34d0d3331cda8f5',
    '2f6c2be2e48f49f78decf349e63265de',
    '72f1e5f5cb004912a7557d72e0f7f652',
    'fe15dabd9d984bd489c1478fd18ffe6c',
    '2b8972952cfc497d8826e8021a7d8d92',
    'bf987c51ea5c4ce78ec811d9288481d3',
    'd7b9fbea37954e329ee8608004d2da05',
    '87e9e9a543f9438490c1e59a63926f07',
    '6b558f2e86ad4696a3001ecf9fe4b21d',
    '9aeed1e21fbf4158b908aec943087eb0',
    'ac89a5dda0e143e894d435ac8995d24d',
    '2a15df822c0a4eb8a788e572afa4742c',
    '4c2c0ef25e234098bfb5f18c732a28a9',
    '1cbd413b3a61499bb810f2883303cb6a',
    '969298f797cc4265a3f2e87e4dfdc518',
    'ddac82a533ed48e98fa6b4de3a06feee',
    '3e2e6df232094bb9886b7595096e3e6b',
    '59ded02ca64c4c0ab3d5ede710371123',
    '40661ccbe2e644bc8172922b124a1710',
    'a3fa8d41ab654d56af396a54db24f7b5',
    'f92214baa3db40fabcfdb175a04ade66',
    'db8627874e774b539389f143ab1e0f8c',
    '0d6952220feb4a13a0f93e205b8d62cb',
    '5c3dd326f2da4057aa952256f45305ab',
    '750a698c5ad846f88f87aae00540505f',
    'cf73a3dd6d0c41fc9d9dbda95a4cf536',
    '008128a294ce42afa12f0ef90591aa7b',
    '729157e0c72a4f2087223661836d948f',
    'f8bbac1ddf5c4efb85cec18546a8088a',
    '173b8aa9dd664a33917e04adeff44684',
    '554ab71d3c0a41b1ab60ee7b1b758fae',
    '04a6af281972401d96674bff6fe767bb',
    'c3cb3544785f4a61a5fdf3ab78306561',
    '98a87ce236174e7ab69034aa38f659ba',
    '7f1654c5efa24dadba3703d82f97c45f',
    '5034a1b0f66a4094aabaa2a0d3bdc3b4',
    '9ff967e2f9ec40aab85a6501e8ce4d60',
    'bf0cc5b403c241c8b9323ddb2489a76e',
    '69e96fc4cf254c88a0cc92e7842ed4c8',
    '5f0920c74fef413c9a04aea044b93d7e',
    '4f6ebdd6a504445b9a38020f5a0e7aa7',
    'e00862ac9dc44ee8b3bb1e2c02162fb9',
    '9eec67c764014c139a392175e17a9998',
    '2ff76133ce0047a18219f072ab3adb09',
    '61cadeae84d449f197fad9736bf7921d',
    'f2238ccf20c84cd99336c165e8b40115',
    '25953a714f064300ae9d9d3c684dc6ae',
    '17bd953399894c17a7f96a7d9a14af9f',
    'f9098752968f478491a6d5d0dad456b9',
    '651bf4d967544a08994d1f17fd52bea8',
    '581ddc7f75be466ab3fbcc51d4ee0ffb',
    'bb9007a6f55a4a6daa5271418f0c16e5',
    '0696c78302d34b8cb9122e91c80fd935',
    'fe6afa3b778243548a36e7df3d8e7f68',
    'f5f121881568425d80b6cf2fe3f09e0d',
    '9100fcd3470f4c0f88b403f12eaaf65a',
    '3e1c91e67ff54838b28566f72478e3c6',
    '70689f17ac39440c91b4b0a82e77c58c',
    'd5deac6df499466680d6b6e74d86734c',
]


def get_sign_config(contId: str, appVersion: str = '2500090310'):
    tm = f'{time.time() * 1000 - 1000 * 1000:.0f}'
    md5string = hashlib.new('md5', f'{tm}{contId}{appVersion[:8]}'.encode('utf-8')).hexdigest()
    return tm, url_sign(md5string)


def url_sign(md5string: str):
    ''' 原算法两次随机数合并为一次 所以这里限定了下范围 '''
    salt = f'{randint(10000000, 99999999)}'
    text = f'{md5string}{SALT_TABLE[int(salt[6:]) % 100]}migu{salt[:4]}'
    sign = hashlib.new('md5', text.encode('utf-8')).hexdigest()
    return [salt, sign]


if __name__ == '__main__':
    print(get_sign_config('714725402'))
    # print(url_sign('a42002edf5fdf989cb63a07327eb804c'))