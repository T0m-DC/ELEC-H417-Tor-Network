from custom_tor import Client
import sys


n = len(sys.argv)
if n == 2:
    client = Client(name=str(sys.argv[1]))
    while True:
        client.sendViaTor()
else:
    client = Client()
    while True:
        client.sendViaTor()
