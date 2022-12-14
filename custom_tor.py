import random
import os
from socket import socket, AF_INET, SOCK_STREAM
from cryptography.fernet import Fernet
from termcolor import colored

os.system('color')

class TorNetwork:
    def __init__(self):
        try:
            port = int(input('Enter port where the Network will listen : '))
            self.port = port
            self.serverSocket = socket(AF_INET, SOCK_STREAM)
            self.serverSocket.bind(('', port))
            self.serverSocket.listen(1)
            self.nRelays = 0
            self.relayKeys = []
            self.relayPorts = []
        except ValueError as e:
            print(colored(f"{e}", 'red'))
            self.__init__()

    def listen(self):
        while True:
            print(colored(f"Tor network : waiting...", attrs=['bold', 'underline']))
            connectionSocket, addr = self.serverSocket.accept()
            message = connectionSocket.recv(1024).decode()
            print(colored(f"Request received from {addr} : {message}", attrs=['bold']))
            if message == 'GET relays':
                n = 3  # random.randint(3, self.nRelays)
                if n > self.nRelays:
                    print(colored(f"Not enough relays !", "red"))
                    connectionSocket.send('Not enough relays !'.encode())
                    connectionSocket.close()

                else:
                    indChosen = []
                    nbChosen = 0
                    returnMessage = []
                    while nbChosen != n:
                        ind = random.randint(0, self.nRelays - 1)
                        if ind not in indChosen:
                            nbChosen += 1
                            returnMessage.append((self.relayPorts[ind], self.relayKeys[ind]))
                            indChosen.append(ind)

                    returnMessage = str(returnMessage).encode()
                    print(returnMessage.decode())
                    connectionSocket.send(returnMessage)
                    connectionSocket.close()

            elif 'JOIN pool' in message:
                messageParsed = message.split(' ')
                port = messageParsed[2]
                key = messageParsed[3]
                if port not in self.relayPorts:
                    self.relayPorts.append(port)
                    self.relayKeys.append(key)
                    self.nRelays += 1
                    print(colored(f'New relay in the network', 'green'))
                    print(colored(f'List of relays :', attrs=['bold']))
                    for p, k in zip(self.relayPorts, self.relayKeys):
                        print(p, k)
                    connectionSocket.send('SUCCESSFUL'.encode())
                    connectionSocket.close()
                else:
                    print(colored(f"Port already used !", 'red'))
                    connectionSocket.send('Port already used !'.encode())
                    connectionSocket.close()

            else:
                print(colored(f"Invalid request", 'red'))
                connectionSocket.send('Invalid request'.encode())
                connectionSocket.close()

    def close(self):
        self.serverSocket.close()


class Client:
    def __init__(self):
        name = str(input('Enter the name of the Client : '))
        self.name = name
        self.keys = []
        self.ports = []

    def connectToTorNetwork(self):
        clientSocket = socket(AF_INET, SOCK_STREAM)
        try:
            portDestination = int(input(f"{self.name} : Tor network port : "))
            message = 'GET relays'
            try:
                clientSocket.connect(('localhost', portDestination))
                clientSocket.send(message.encode())

                self.keys = []
                self.ports = []

                responseMessage = clientSocket.recv(1024).decode()
                if responseMessage == 'Not enough relays !':
                    print(colored(f"{self.name} : response : {responseMessage}", 'red'))
                    clientSocket.close()
                    return False

                responseMessage = responseMessage[1:len(responseMessage) - 2].split(',')

                t = 0
                for elem in responseMessage:
                    elem = elem.replace("(", "").replace(')', '').replace('"', '').replace("'", '').strip()
                    if t % 2 == 0:
                        self.ports.append(int(elem))
                    else:
                        self.keys.append(elem[1:].encode())
                    t += 1

                print(f"{self.name} : ports : {self.ports}")
                print(f"{self.name} : keys : {self.keys}")
                clientSocket.close()
                return True

            except ConnectionRefusedError:
                print(colored(f"Connection refused ! (probably wrong port)", 'red'))
                return False

        except ValueError as e:
            print(colored(f"{e}", 'red'))
            clientSocket.close()
            self.connectToTorNetwork()

    def sendViaTor(self):
        if self.connectToTorNetwork():
            try:
                encryptors = [Fernet(k) for k in self.keys]
                print()
                portDestination = int(input(f"{self.name} : Port destination : "))
                message = input(colored(f"{self.name} : Message : ", attrs=['bold']))
                message = str(portDestination) + " " + message

                messageEncrypted = message.encode()
                for i in range(len(self.ports)):
                    messageEncrypted = encryptors[i].encrypt(messageEncrypted)
                    if i != len(self.ports) - 1:
                        messageEncrypted = str(self.ports[i]).encode() + ' '.encode() + messageEncrypted

                clientSocket = socket(AF_INET, SOCK_STREAM)
                clientSocket.connect(('localhost', self.ports[len(self.ports)-1]))
                clientSocket.send(messageEncrypted)

                responseMessage = clientSocket.recv(1024)
                responseDecrypted = responseMessage

                for decryptor in reversed(encryptors):
                    responseDecrypted = decryptor.decrypt(responseDecrypted)

                if responseDecrypted.decode() == 'Not a valid port':
                    print(colored(f"{self.name} : response : {responseDecrypted.decode()}", 'red'))
                else:
                    print(colored(f"{self.name} : response : {responseDecrypted.decode()}", attrs=['bold']))
                print()
                clientSocket.close()
            except ValueError as e:
                print(colored(f"{e}", 'red'))
                self.sendViaTor()


class TorRelay:
    def __init__(self):
        self.name = None
        self.port = None
        self.key = Fernet.generate_key()
        self.encryptor = Fernet(self.key)
        self.socketListening = socket(AF_INET, SOCK_STREAM)
        self.inPool = False

    def listen(self):
        self.socketListening.bind(('', self.port))
        self.socketListening.listen(1)
        while True:
            print(colored(f"{self.name} : listening on port {self.port}...", attrs=['bold', 'underline']))
            connectionSocket, addr = self.socketListening.accept()
            receivedMessage = connectionSocket.recv(1024)

            print(colored(f"{self.name} : received message from {addr} : {receivedMessage.decode()}", attrs=['bold']))
            messageDecrypted = self.encryptor.decrypt(receivedMessage).decode()

            nextPort = messageDecrypted.split(' ')[0].strip()
            messageToSend = messageDecrypted[len(nextPort):].strip()
            print(f"{self.name} : port : {nextPort}")
            print(f"{self.name} : message : {messageToSend}")

            socketSending = socket(AF_INET, SOCK_STREAM)
            try:
                socketSending.connect(('localhost', int(nextPort)))
                socketSending.send(messageToSend.encode())

                responseMessage = socketSending.recv(1024)
                print(colored(f'{self.name} : response : {responseMessage.decode()}', attrs=['bold']))

                responseMessageEncrypted = self.encryptor.encrypt(responseMessage)
                print(f'{self.name} : response encrypted : {responseMessageEncrypted.decode()}')

                connectionSocket.send(responseMessageEncrypted)
                print(colored(f"{self.name} : message sent on {connectionSocket.getpeername()}", attrs=['bold']))
                print()

            except ValueError as e:
                print(colored(f"{e}", 'red'))
                print(colored('Not a valid port', 'red'))
                print(colored(f"{self.name} : message sent on {connectionSocket.getpeername()}", attrs=['bold']))
                print()
                connectionSocket.send(self.encryptor.encrypt('Not a valid port'.encode()))

            except ConnectionRefusedError as e:
                print(colored(f"{e}", 'red'))
                print(colored('Not a valid port', 'red'))
                print(colored(f"{self.name} : message sent on {connectionSocket.getpeername()}", attrs=['bold']))
                print()
                connectionSocket.send(self.encryptor.encrypt('Not a valid port'.encode()))

            socketSending.close()
            connectionSocket.close()

    def joinTorPool(self):
        self.name = str(input('Enter the name of the Relay : '))
        try:
            self.port = int(input('Enter the port of the Relay : '))
            portDestination = int(input(f"{self.name} : network port : "))

            message = 'JOIN pool' + ' ' + str(self.port) + ' ' + str(self.key)
            try:
                socketSending = socket(AF_INET, SOCK_STREAM)
                socketSending.connect(('localhost', portDestination))
                socketSending.send(message.encode())

                responseMessage = socketSending.recv(1024).decode()
                socketSending.close()
                if responseMessage != 'SUCCESSFUL':
                    print(colored('ERROR !!!', 'red'))
                    print(colored(responseMessage, 'red'))
                    self.joinTorPool()
                else:
                    print(colored('SUCCESSFUL', 'green'))
                    self.inPool = True

            except ConnectionRefusedError:
                print(colored("Connection refused ! (probably wrong port)", "red"))
                self.joinTorPool()

        except ValueError as e:
            print(colored(f"{e}", 'red'))
            self.joinTorPool()


class Server:
    def __init__(self):
        try:
            port = int(input('Enter the port of the Server : '))

            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.bind(('', port))
            serverSocket.listen(1)

            while True:
                print(colored("Server : waiting...", attrs=['bold', 'underline']))
                connectionSocket, addr = serverSocket.accept()
                message = connectionSocket.recv(1024)
                print(f"Server : received message : {message.decode()}")

                connectionSocket.send(message)
                print(f"Server : message sent : {message.decode()}")

                connectionSocket.close()

        except ValueError as e:
            print(colored(f"{e}", 'red'))
            self.__init__()
