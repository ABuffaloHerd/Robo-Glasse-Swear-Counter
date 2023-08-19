import json
import os
import re
from collections import Counter


def init_generic_word_db():
    """
    Initialize the generic word database.
    """
    if not os.path.exists('generic_db.json'):
        with open('generic_db.json', 'w') as f:
            json.dump({}, f)
            print("dump")

def get_generic_words(**kwargs):
    """
    Get the generic words.
    kwargs specifies a server to get the generic words for.
    no keyword arg means get the entire database.
    """
    if 'server' in kwargs:
        server = kwargs['server']
        db = get_generic_words()
        if server in db:
            return db[server]
        else:
            return {}

    with open('generic_db.json', 'r') as f:
        return json.load(f)
    
def generic_word_counter(server, message, author):
    """
    Search the message for generic words for THIS server and return the number of generic words found.
    """
    db = get_generic_words()

    # Data to return
    data = {}

    if server in db:
        # Dig until we find it
        words = db[server]

        # Now we have a dict of words and their counts
        for word in words.keys():

            # count = sum(1 for w in message.split() if word in w.lower())
            # count = sum(1 for _ in re.finditer(r'\b' + re.escape(word) + r'\b', message, re.IGNORECASE)) # Thanks harrison
            count = len(re.findall(re.escape(word), message, re.IGNORECASE)) # Thanks again harrison
            # Increment total

            if count > 0:
                db[server][word]['total'] += count
                
                if author in db[server][word]['users']:
                    db[server][word]['users'][author] += count
                else:
                    db[server][word]['users'][author] = count

                data[word] = count

        # Save the db
        with open('generic_db.json', 'w') as f:
            json.dump(db, f)
    
    return data

def get_top_users(server, word):
    """
    Gets the top 3 users from this server for the given word.
    """
    db = get_generic_words()
    if server in db:
        if word in db[server]:
            users = db[server][word]['users']
            top = sorted(users.items(), key=lambda x: x[1], reverse=True)
            return top

    return None

def register_generic_word(server, word):
    db = get_generic_words()
    if server not in db:
        db[server] = {}

    if word not in db[server]:
        db[server][word] = {"total": 0, "users": {}}
    else: return False

    with open('generic_db.json', 'w') as f:
        json.dump(db, f)
        
    return True

def unregister_generic_word(server, word):
    db = get_generic_words()

    if server in db:
        if word in db[server]:
            del db[server][word]
            with open('generic_db.json', 'w') as f:
                json.dump(db, f)

            return True
    
    return False