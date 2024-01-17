# this file save the initial exploration of the file save as some absolute path
import json
import os
import hashlib

def get_file_hash(file_content):
    md5_hash = hashlib.md5(file_content).hexdigest()
    return md5_hash

def get_desc_from_db(hash_):

    desc_data = json.load(open('/Users/olzhas/PycharmProjects/textualDS/database/db.json'))

    if hash_ in desc_data:
        return desc_data[hash_]
    else:
        return None

def save_to_db(hash_, init_desc):

    desc_data = json.load(open('/Users/olzhas/PycharmProjects/textualDS/database/db.json'))
    desc_data[hash_] = init_desc

    with open('/Users/olzhas/PycharmProjects/textualDS/database/db.json', 'w') as f:
        json.dump(desc_data, f)
