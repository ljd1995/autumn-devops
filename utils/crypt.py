import base64
import hashlib
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from config.setting import settings


class AESCipher(object):
    # 使用ECB模式加密
    MODE = AES.MODE_CBC
    # 使用默认的pkcs7 padding
    PAD_STYLE = "pkcs7"
    # 编码方式
    ENCODING = "UTF-8"
    # 密钥
    KEY = settings.AES_KEY
    # 初始化向量
    IV = settings.AES_IV

    # key长度只能为16或24或32，分别对应AES-128、AES-192、AES-256
    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        # 将密钥编码为UTF-8格式的bytes
        key_bytes = cls.KEY.encode(cls.ENCODING)
        iv_bytes = cls.IV.encode(cls.ENCODING)
        # 创建AES对象
        cipher = AES.new(key_bytes, cls.MODE, iv_bytes)
        # 将明文编码为UTF-8格式的bytes
        plaintext_bytes = plaintext.encode(cls.ENCODING)
        # 为编码后的明文添加padding
        plaintext_bytes_padded = pad(plaintext_bytes, AES.block_size, cls.PAD_STYLE)
        # 执行加密
        ciphertext_bytes = cipher.encrypt(plaintext_bytes_padded)
        # 将加密后的bytes进行base64编码
        ciphertext_base64_bytes = base64.b64encode(ciphertext_bytes)
        # 将base64编码过的bytes，解码为Python中使用的字符串类型（即unicode字符串）
        ciphertext = ciphertext_base64_bytes.decode(cls.ENCODING)
        return ciphertext

    @classmethod
    def decrypt(
        cls,
        ciphertext: str,
    ) -> str:
        # 将密钥编码为UTF-8格式的bytes
        key_bytes = cls.KEY.encode(cls.ENCODING)
        iv_bytes = cls.IV.encode(cls.ENCODING)
        # 创建AES对象
        decrypter = AES.new(key_bytes, cls.MODE, iv_bytes)
        # 将密文编码为UTF-8格式的（同时也是base64编码的）bytes
        ciphertext_base64_bytes = ciphertext.encode(cls.ENCODING)
        # 将base64编码的bytes，解码为原始的密文bytes
        ciphertext_bytes = base64.b64decode(ciphertext_base64_bytes)
        # 解码为明文
        plaintext_bytes_padded = decrypter.decrypt(ciphertext_bytes)
        # 去掉Padding
        plaintext_bytes = unpad(plaintext_bytes_padded, AES.block_size, cls.PAD_STYLE)
        # 将UTF-8格式编码的明文bytes，解码为Python中的字符串类型（即unicode字符串）
        plaintext = plaintext_bytes.decode(cls.ENCODING)
        return plaintext


def md5_encode(s: str) -> str:
    """
    md5加密
    """
    md5 = hashlib.md5()
    md5.update(s.encode("utf-8"))
    return md5.hexdigest()


def md5_encode_with_salt(s: str, salt: str | None = None) -> str:
    """
    md5加密
    """
    if salt is None:
        salt = str(int(time.time() * 1000))
    md5 = hashlib.md5()
    md5.update((s + salt).encode("utf-8"))
    return md5.hexdigest()
