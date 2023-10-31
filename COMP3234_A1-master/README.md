# COMP3234_A1
Implemented a simple game house application using Python socket programming. A game house is an application in which multiple clients connect to a game server, get authorized, and then select a game room to enter and play a game with another player in the same room.

# Setup (For Mac)
1. Open a terminal window and navigate to the repository created after unzipping the files.
2. Start the server using the command `python GameServer.py <listening port> <path to UserInfo.txt>`. You will be able to see "The server is ready" message upon successfully running the server.

![Screenshot of server terminal](https://github.com/satijakritik/images/blob/master/comp3234_a1_server.png?raw=true)

3. For creating a client connection, open a new terminal window and navigate to the repository.
4. Start the client using the command `python GameClient.py <hostname/server IP address> <server's listening port>`. You will be prompted to enter the user name and password for authentication.

![Screenshot of client terminal](https://github.com/satijakritik/images/blob/master/comp3234_a1_client.png?raw=true)
