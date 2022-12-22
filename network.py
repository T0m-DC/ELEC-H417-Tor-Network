from custom_tor import TorNetwork
import sys


n = len(sys.argv)
if n == 2:
    torNetwork = TorNetwork(port=int(sys.argv[1]))
    torNetwork.listen()
else:
    torNetwork = TorNetwork()
    torNetwork.listen()
