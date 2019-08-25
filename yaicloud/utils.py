import time
import random

def wait(min=5, max=10):
    d = max - min
    time.sleep(min + random.random() * d)
