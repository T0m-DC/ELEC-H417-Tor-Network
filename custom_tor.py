import hashlib
import random
import os
from socket import socket, AF_INET, SOCK_STREAM
from cryptography.fernet import Fernet
from termcolor import colored
import webbrowser

os.system('color')

class TorNetwork:
    def __init__(self, port=None):
        try:
            if port is None:
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
            print(colored(f"\nTor network : waiting...", attrs=['bold', 'underline']))
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
    def __init__(self, name=None):
        if name is None:
            name = str(input('Enter the name of the Client : '))
        self.name = name
        self.keys = []
        self.ports = []

    def connectToTorNetwork(self):
        clientSocket = socket(AF_INET, SOCK_STREAM)
        try:
            portDestination = int(input(f"\n{self.name} : enter tor network port : "))
            message = 'GET relays'
            try:
                clientSocket.connect(('localhost', portDestination))
                clientSocket.send(message.encode())

                self.keys = []
                self.ports = []

                responseMessage = clientSocket.recv(1024).decode()
                if responseMessage == 'Not enough relays !':
                    print(f"{self.name} : " + colored(f"response : {responseMessage}", 'red'))
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
                print(f"{self.name} : " + colored(f"Connection refused ! (probably wrong port)", 'red'))
                return False

        except ValueError as e:
            print(f"{self.name} : " + colored(f"{e}", 'red'))
            clientSocket.close()
            self.connectToTorNetwork()

    def sendViaTor(self):
        if self.connectToTorNetwork():
            try:
                encryptors = [Fernet(k) for k in self.keys]
                portDestination = int(input(f"\n{self.name} : enter destination port : "))
                message = "GET HTTP"#input(colored(f"{self.name} : Message : ", attrs=['bold']))
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

                if responseDecrypted.decode() == 'NOT A VALID PORT':
                    print(f"{self.name} : " + colored(f"response : {responseDecrypted.decode()}", 'red'))
                elif responseDecrypted.decode() == 'WRONG REQUEST !':
                    print(f"{self.name} : " + colored(f"response : {responseDecrypted.decode()}", 'red'))
                elif "AUTHENTICATION NEEDED" in responseDecrypted.decode():
                    print(f"{self.name} : " + colored("AUTHENTICATION NEEDED", attrs=['bold']))
                    challenge = int(responseDecrypted.decode().split(" ")[2].strip())
                    password = str(input(f"{self.name} : Enter password : "))
                    hashedPassword = hashlib.sha256((password+str(challenge)).encode()).hexdigest()
                    message = str(portDestination) + " " + hashedPassword
                    messageEncrypted = message.encode()
                    for i in range(len(self.ports)):
                        messageEncrypted = encryptors[i].encrypt(messageEncrypted)
                        if i != len(self.ports) - 1:
                            messageEncrypted = str(self.ports[i]).encode() + ' '.encode() + messageEncrypted

                    clientSocket.close()
                    clientSocket = socket(AF_INET, SOCK_STREAM)
                    clientSocket.connect(('localhost', self.ports[len(self.ports) - 1]))
                    clientSocket.send(messageEncrypted)
                    responseMessage = clientSocket.recv(1024)
                    responseDecrypted = responseMessage
                    for decryptor in reversed(encryptors):
                        responseDecrypted = decryptor.decrypt(responseDecrypted)
                    if responseDecrypted.decode() == "WRONG PASSWORD":
                        print(f"{self.name} : " + colored("Wrong password !", 'red'))

                    else:
                        print(colored(f"{self.name} : response : {responseDecrypted.decode()}", attrs=['bold']))
                        with open("response.html", "w") as f:
                            f.write(responseDecrypted.decode())
                        webbrowser.open_new_tab('response.html')

                else:
                    print(f"{self.name} : " + colored(f"Something went wrong", 'red'))

                clientSocket.close()

            except ValueError as e:
                print(f"{self.name} : " + colored(f"{e}", 'red'))
                self.sendViaTor()


class TorRelay:
    def __init__(self, name=None, port=None):
        self.name = name
        self.port = port
        self.key = Fernet.generate_key()
        self.encryptor = Fernet(self.key)
        self.socketListening = socket(AF_INET, SOCK_STREAM)
        self.inPool = False

    def listen(self):
        self.socketListening.bind(('', self.port))
        self.socketListening.listen(1)
        while True:
            print(colored(f"\n{self.name} : listening on port {self.port}...", attrs=['bold', 'underline']))
            connectionSocket, addr = self.socketListening.accept()
            receivedMessage = connectionSocket.recv(1024)

            print(f"{self.name} : " + colored(f"received message from {addr} : {receivedMessage.decode()}", attrs=['bold']))
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
                print(f"{self.name} : " + colored(f'response : {responseMessage.decode()}', attrs=['bold']))

                responseMessageEncrypted = self.encryptor.encrypt(responseMessage)
                print(f'{self.name} : response encrypted : {responseMessageEncrypted.decode()}')

                connectionSocket.send(responseMessageEncrypted)
                print(f"{self.name} : " + colored(f"message sent on {connectionSocket.getpeername()}", attrs=['bold']))

            except ValueError as e:
                print(f"{self.name} : " + colored(f"{e}", 'red'))
                print(f"{self.name} : " + colored('NOT A VALID PORT', 'red'))
                print(f"{self.name} : " + colored(f"message sent on {connectionSocket.getpeername()}", attrs=['bold']))
                connectionSocket.send(self.encryptor.encrypt('NOT A VALID PORT'.encode()))

            except ConnectionRefusedError as e:
                print(f"{self.name} : " + colored(f"{e}", 'red'))
                print(f"{self.name} : " + colored('NOT A VALID PORT', 'red'))
                print(f"{self.name} : " + colored(f"message sent on {connectionSocket.getpeername()}", attrs=['bold']))
                connectionSocket.send(self.encryptor.encrypt('NOT A VALID PORT'.encode()))

            socketSending.close()
            connectionSocket.close()

    def joinTorPool(self):

        try:
            if self.name is None:
                self.name = str(input('Enter the name of the Relay : '))
            if self.port is None:
                self.port = int(input('Enter the port of the Relay : '))
            portDestination = int(input(f"{self.name} : tor network port to join : "))

            message = 'JOIN pool' + ' ' + str(self.port) + ' ' + str(self.key)
            try:
                socketSending = socket(AF_INET, SOCK_STREAM)
                socketSending.connect(('localhost', portDestination))
                socketSending.send(message.encode())

                responseMessage = socketSending.recv(1024).decode()
                socketSending.close()
                if responseMessage != 'SUCCESSFUL':
                    print(f"{self.name} : " + colored('ERROR !!!', 'red'))
                    print(f"{self.name} : " + colored(responseMessage, 'red'))
                    self.joinTorPool()
                else:
                    print(f"{self.name} : " + colored('SUCCESSFUL', 'green'))
                    self.inPool = True

            except ConnectionRefusedError:
                print(f"{self.name} : " + colored("Connection refused ! (probably wrong port)", "red"))
                self.joinTorPool()

        except ValueError as e:
            print(f"{self.name} : " + colored(f"{e}", 'red'))
            self.joinTorPool()


class Server:
    def __init__(self, port=None, password=None):
        if password is None:
            password = "unicorn"
        password = str(password)
        try:
            if port is None:
                port = input('Enter the port of the Server : ')

            port = int(port)
            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.bind(('', port))
            serverSocket.listen(1)

            while True:
                print(colored("\nServer : waiting...", attrs=['bold', 'underline']))
                connectionSocket, addr = serverSocket.accept()
                message = connectionSocket.recv(1024)
                print(f"Server : received message : {message.decode()} from {addr}")
                if message.decode() ==  "GET HTTP":
                    print(colored("Authentication needed !", attrs=['bold']))
                    challenge = str(random.randint(1, 100000))
                    
                    connectionSocket.send(("AUTHENTICATION NEEDED "+challenge).encode())
                    rightResponse = hashlib.sha256((password+challenge).encode()).hexdigest()

                    connectionSocket, addr = serverSocket.accept()
                    response = connectionSocket.recv(1024).decode()

                    print(f"Expected response : {rightResponse}")
                    print(f"Recived response : {response}")

                    if response == rightResponse:
                        print(colored("Successful authentication !", 'green'))
                        connectionSocket.send(b"<html><body>Hello World</body></html>")
                        print(f"Server : message sent : {b'<html><body>Hello World</body></html>'.decode()}")
                    else:
                        print(colored("Wrong password !", 'red'))
                        connectionSocket.send("WRONG PASSWORD".encode())
                        print(f"Server : message sent : WRONG PASSWORD")
                else:
                    connectionSocket.send("WRONG REQUEST !".encode())
                    print(f"Server : message sent : {colored('WRONG REQUEST !', 'red')}")

                connectionSocket.close()

        except ValueError as e:
            print(colored(f"{e}", 'red'))
            self.__init__()
