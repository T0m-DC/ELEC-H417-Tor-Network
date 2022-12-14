from custom_tor import TorRelay


relay = TorRelay()
relay.joinTorPool()
relay.listen()
