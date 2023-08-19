import random

TIPS = []

def init_tips():
    with open('tttt.txt', 'r') as f:
        for line in f:
            TIPS.append("Here's a Top Gear Top Tip for you: " + line)

    with open('ss13tips.txt', 'r') as f:
        for line in f:
            TIPS.append(line)
    
    with open('tf2tips.txt', 'r') as f:
        for line in f:
            TIPS.append(line)

    with open('tips.txt', 'r', encoding='UTF-8') as f:
        for line in f:
            TIPS.append(line)

def random_tip():
    return random.choice(TIPS)