#!/usr/bin/python3

import socket
import sys

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host_name = sys.argv[1] #Parameter 1
# server_port = int(sys.argv[2])

if sys.argv[2].isdigit():
    server_port = int(sys.argv[2]) #Parameter 2
else:
    print("Error: Server's listening port is not an integer")
    exit(1)

try:
    clientSocket.connect( (host_name, server_port) )
except socket.error as err:
    print("Connection error: ", err)
    exit(1)

auth = False
in_game_hall = False

while auth == False:
# Get input for sending
    user_name = input("Please input your user name:\n")
    password = input("Please input your password:\n")

    msg = f"/login {user_name} {password}"

    try:
        clientSocket.send(msg.encode())
    except socket.error as err:
        print("Connection error: ", err)
        exit(1)

    try:
        response = clientSocket.recv(1024)
    except socket.error as err:
        print("Connection error: ", err)
        exit(1)
    
    if response.decode() == "1001 Authentication successful":
        auth = True
        in_game_hall = True
    
    print(response.decode())
    
while in_game_hall:
    cmd = input("")
    
    try:
        clientSocket.send(cmd.encode())
    except socket.error as err:
        print("Connection error: ", err)
        exit(1)
    
    try:
        response = clientSocket.recv(1024)
    except socket.error as err:
        print("Connection error: ", err)
        exit(1)
    
    if response.decode() == "4001 Bye bye":
        in_game_hall = False
        print(response.decode())
        print("Client ends")
        clientSocket.close()
        exit(1)
        
    if response.decode() == "3011 Wait":
        
        # response = clientSocket.recv(1024)
        print(response.decode())
        
        while response.decode() != "3012 Game started. Please guess true or false":
            try:
                response = clientSocket.recv(1024)
            except socket.error as err:
                print("Connection error: ", err)
                exit(1)
            # pass
        print(response.decode())
        cmd = input("")
        
        try:
            clientSocket.send(cmd.encode())
        except socket.error as err:
            print("Connection error: ", err)
            exit(1)
        
        try:
            response = clientSocket.recv(1024)
        except socket.error as err:
            print("Connection error: ", err)
            exit(1)
        # print(response.decode())
    
    if response.decode() == "3012 Game started. Please guess true or false":
        print(response.decode())
        cmd = input("")
        
        try:
            clientSocket.send(cmd.encode())
        except socket.error as err:
            print("Connection error: ", err)
            exit(1)
        
        try:
            response = clientSocket.recv(1024)
        except socket.error as err:
            print("Connection error: ", err)
            exit(1)
        # print(response.decode())
    
    print(response.decode())

clientSocket.close()