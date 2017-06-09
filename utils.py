import string
import random
import base64
import hashlib
import hmac

def sha1(filename):
  m = hashlib.sha1()
  with open(filename, 'r') as fp:
    while True:
      buff = fp.read(4096)
      if not buff:
        break;
      m.update(buff)
  return m.digest().hexdigest()

def randstring(n):
  base_string = string.ascii_uppercase + string.ascii_lowercase + string.digits
  return ''.join(random.choice(base_string) for _ in range(n))
