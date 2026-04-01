"""
Base62 encoding utility for converting integers to short codes.
Uses a-z, A-Z, 0-9 (62 characters) for maximum density.
"""

BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(BASE62_ALPHABET)


def encode_base62(num: int) -> str:
    """
    Convert an integer to a Base62 string.
    Supports up to 3.5 trillion unique combinations with 7 characters.
    
    Args:
        num: The integer to encode (must be >= 0)
        
    Returns:
        A Base62 encoded string, padded to 7 characters
    """
    if num < 0:
        raise ValueError("Number must be non-negative")
    
    if num == 0:
        return BASE62_ALPHABET[0].zfill(7)
    
    result = []
    while num > 0:
        num, remainder = divmod(num, BASE)
        result.append(BASE62_ALPHABET[remainder])
    
    # Reverse to get correct order and pad to 7 characters
    encoded = ''.join(reversed(result))
    return encoded.zfill(7)


def decode_base62(short_code: str) -> int:
    """
    Convert a Base62 string back to an integer.
    
    Args:
        short_code: The Base62 string to decode
        
    Returns:
        The decoded integer
    """
    num = 0
    for char in short_code:
        num = num * BASE + BASE62_ALPHABET.index(char)
    return num
