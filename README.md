# ELEC-H417 : Tor Network Project
***

## Explanation

A tor network consists of a group of relays that will create an encrypted link when a client wants to make a request via the network.
The client will first encrypt the packet with the key of the exit gard, then add the address of the exit gard to the packet. Then the step will be repeated for the two others relays chosen to form the link.

### Network

The tor network will act as a database to store the addresses and keys of the relays. It will listen for relays to join its pool or for a client to ask for and triplet of relays to pass through.
It will be hosted as a server.

### Relay

For a relay to be part of the network, it needs to give its address and its key to the network database. When receiving a packet it will decrypt it with its key and then send it to the next point. This next point is found in the packet because after decryption the relay can read an address and another packet.

### Client

A client can send a http request to a server via the tor network. To do so, it first accesses the database of the network by entering its address. After this, it will have the information of 3 relays to start and craft the packet. Then it will be asked to enter the address of the server to connect to.
If the server has an authentication scheme, the client will be asked to enter a password. The process of encryption and challenge response is explained in the next section.

### Server

The server will listen for packets. If the packet is a http request, the server will ask for authentication to the user. It will be done by a challenge response scheme. The server will first generate a random number and send it back to the client. Then it will concatenate its secret password with the random number and hash it using the SHA-256 algorythm.
When the client has responded with its hashed version of the challenge and password, the server will compare the two hashed version and if they are the same the request will be processed.

---
## Installation

### Python

You should have python already installed on your computer

### Dependencies

To install the dependencies of the project just enter the command below in the folder where you have cloned the project :
```cmd
pip install -r requirements.txt
```

If you are on Windows you can also just launch the **installLibrairies.cmd** file.

---
## How to launch

You can simply launch the individual python scripts to summon each entity. If you do so you will need to configure them directly in the console. But you can already configure them during launch :
```cmd
python server.py port
python network.py port
python relay.py name port
python client.py name
```

But if you wish and are on Windows you can launch the **launchTor.cmd** file. To do so you just have to insert the path of the folder where the files of the project are in the **cmd** file.
