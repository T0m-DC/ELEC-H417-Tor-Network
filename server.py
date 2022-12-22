from custom_tor import Server
import sys


n = len(sys.argv)
if n == 2:
    server = Server(port=int(sys.argv[1]))
else:
    server = Server()


