from custom_tor import TorRelay
import sys


n = len(sys.argv)
if n == 2:
    relay = TorRelay(name=str(sys.argv[1]))
    relay.joinTorPool()
    relay.listen()
elif n == 3:
    relay = TorRelay(name=str(sys.argv[1]), port=int(sys.argv[2]))
    relay.joinTorPool()
    relay.listen()
else:
    relay = TorRelay()
    relay.joinTorPool()
    relay.listen()


