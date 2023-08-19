import json
import os
import discord
import interactions
import re

nwords = []

REGEX_NWORD_HARDR = re.compile(r'\b(n*[1i!l]+[g9]{2,}[3e]+[r5]+)\b', re.IGNORECASE)
REGEX_NWORD = re.compile(r'\b(n*[1i!l]+[g9]{2,}[a4]+)\b', re.IGNORECASE)

# Returns the number of times the n-word has been said in the text, as well as hard rs in a tuple
# Caller is responsible for updating the json database
def nword_counter(text):
    count = 0
    hard_r = 0
    for word in text.split():
        if re.match(REGEX_NWORD, word):
            count += 1
        if re.match(REGEX_NWORD_HARDR, word):
            hard_r += 1
    return (count, hard_r)

# load a list of possible iterations of the n-word
def load_definitions():
    # load the json database
    if not os.path.exists('nword_db.json'):
        with open('nword_db.json', 'w') as f:
            json.dump({}, f)

def insert_json_db(user, nwords, hard_rs):
    with open('nword_db.json', 'r') as f:
        data = json.load(f)
    if user in data:
        data[user]['nwords'] += nwords
        data[user]['hard_rs'] += hard_rs
    else:
        data[user] = {'nwords': nwords, 'hard_rs': hard_rs}
    with open('nword_db.json', 'w') as f:
        json.dump(data, f)

def get_json_db(user):
    with open('nword_db.json', 'r') as f:
        data = json.load(f)
    if user in data:
        return data[user]
    else:
        return None