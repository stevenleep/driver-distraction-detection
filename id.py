import uuid
import hashlib


# Generate UUID v4
def gen_uuid():
    return str(uuid.uuid4()).replace('-', '')


# Generate MD5 hash of a file
def calc_file_hash(file):
    md5_hash = hashlib.md5()
    while chunk := file.read(4096):
        md5_hash.update(chunk)
    file.seek(0)
    return md5_hash.hexdigest()

# Generate SHA256 hash of a string
def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()