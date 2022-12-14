import hashlib
from custom_tor import socket, AF_INET, SOCK_STREAM, colored

class Server:
    def __init__(self):
        # This is the secret password that the server knows
        SERVER_PASSWORD = "mysecretpassword"
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

                input("resend message ?")
                connectionSocket.send(message)

                print(f"Server : message sent : {message.decode()}")

                connectionSocket.close()

        except ValueError as e:
            print(colored(f"{e}", 'red'))
            self.__init__()







"""
# This is the challenge that the server sends to the client
CHALLENGE = "Please enter your password:"



# The server receives the client's response and calculates the expected response
# by hashing the password that it knows
expected_response = hashlib.sha256(SERVER_PASSWORD.encode()).hexdigest()

# The server checks the client's response against the expected response
if client_response == expected_response:
    print("Authentication successful")
else:
    print("Authentication failed")
"""
