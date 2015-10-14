from Crypto.PublicKey import RSA
import base64
import struct
import six
from functools import wraps
from flask import abort, g

KEYPAIR_DEFAULT = {
    'bits': 2048,
}


def generate_ssh_keypair(bits=KEYPAIR_DEFAULT['bits']):
    new_key = RSA.generate(bits)
    public_key = new_key.publickey().exportKey(format="OpenSSH")
    private_key = new_key.exportKey(format="PEM")
    return private_key, public_key


def validate_ssh_pubkey(pubkey):
    """
    Check if the given string looks like a SSH public key.
    Based on https://github.com/jirutka/ssh-ldap-pubkey
    """
    if not pubkey:
        return False

    key_parts = pubkey.split()
    if len(key_parts) < 2:
        return False

    key_type, key_data = key_parts[0:2]
    if key_type not in ("ssh-rsa", "ssh-dss"):
        return False

    try:
        key_bytes = base64.decodestring(six.b(key_data))
    except base64.binascii.Error:
        return False

    int_len = 4
    str_len = struct.unpack('>I', key_bytes[:int_len])[0]
    if six.u(key_bytes[int_len:(int_len + str_len)]) != six.b(key_type):
        return False

    return True


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated


def memoize(func):
    """
    Generic memoization implementation suitable for decorator use
    """
    cache = {}

    def inner(x):
        if x not in cache:
            cache[x] = func(x)
        return cache[x]
    return inner
