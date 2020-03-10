#!/bin/python3

# This script does not care about command line options
# Still more effort than a real buzzfeed quiz

import time
import random


def show(text=""):
    with open("buzzfeed.py.out", "a") as f:
        f.write(text + "\n")


open("buzzfeed.py.out", "w+").close()
show("Calculating result based on your input...")
show("Please stand by")
time.sleep(3)
if random.randint(0, 9) == 4:
    show("You are an enigma, your inputs are really special...")
    time.sleep(3)
show("Consulting Star Swirl the Bearded...")
time.sleep(3)
show()

start = [
    "You are totally",
    "Without a doubt, you are",
    "It's really obvious that you are",
    "You are soooooo",
    "There is nobody who fits you better than",
]

pony = [
    "Night Glider",
    "The Smooze",
    "Applejack",
    "Luster Dawn",
    "Spike",
    "Randolph",
    "Princess Luna",
    "Gizmo",
    "Discord",
    "Stygian",
    "Yona",
    "Limestone Pie",
    "Queen Novo",
    "Matilda",
]

r, q = random.randint(0, len(start) - 1), random.randint(0, len(pony) - 1)


show("{} {}!".format(start[r], pony[q]))
