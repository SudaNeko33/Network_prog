#!/usr/bin/python3

import socket
import threading
import sys
import random

STATES = {0: "OUT_OF_HOUSE", 1: "IN_THE_GAME_HALL", 2: "WAITING_IN_ROOM", 3: "PLAYING_A_GAME"}
CMD_LIST_FOR_STATE = {0: ["/login"], 1: ["/exit", "/list", "/enter"], 2: [], 3: ["/guess"]}
NUM_OF_ROOMS = 5

server_port = int(sys.argv[1]) #Parameter 1
file_path = sys.argv[2] #Parameter 2
room_list = [0 for i in range(NUM_OF_ROOMS)]
room_member_list = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}}
user_state = {}

with open(file_path) as file:
    user_data = [(line.rstrip()).split(":") for line in file]

def thd_func(client, lock):
    connectionSocket, addr = client   
    try: 
        msg = connectionSocket.recv(1024)
    except socket.error as err:
        print("Recv error: ", err)
        connectionSocket.close()
    
    msg = msg.decode()
    cmd_args = msg.split()
    cmd = cmd_args[0] #/login
    user_name = cmd_args[1]
    password = cmd_args[2]
    
    user_state[client] = 0 #OUT_OF_HOUSE
    # print(room_list)
    game_over = False
    cmd_list = CMD_LIST_FOR_STATE[0]
    
    while [user_name, password] not in user_data:
        
        if cmd not in cmd_list: 
            msg = "4002 Unrecognized message"
            
            try:
                connectionSocket.send(msg.encode())
            except socket.error as err:
                print("Recv error: ", err)
                connectionSocket.close()
            
            try:
                msg = connectionSocket.recv(1024)
            except socket.error as err:
                print("Recv error: ", err)
                connectionSocket.close()
            msg = msg.decode()
            cmd_args = msg.split()
            cmd = cmd_args[0] #/login
            user_name = cmd_args[1]
            password = cmd_args[2]
            continue
        
        msg = "1002 Authentication failed"
        
        try:
            connectionSocket.send(msg.encode())
        except socket.error as err:
            print("Recv error: ", err)
            connectionSocket.close()
        
        try:
            msg = connectionSocket.recv(1024)
        except socket.error as err:
            print("Recv error: ", err)
            connectionSocket.close()
                
        msg = msg.decode()
        cmd_args = msg.split()
        cmd = cmd_args[0] #/login
        user_name = cmd_args[1]
        password = cmd_args[2]
    
    msg = "1001 Authentication successful"
    try:
        connectionSocket.send(msg.encode())
    except socket.error as err:
        print("Recv error: ", err)
        connectionSocket.close()
    
    lock.acquire()
    user_state[client] = 1 #IN_THE_GAME_HALL
    lock.release()
    
    try:
        msg = connectionSocket.recv(1024)
    except socket.error as err:
        print("Recv error: ", err)
        connectionSocket.close()
                
    msg = msg.decode()
    
    cmd_args = msg.split()
    cmd = cmd_args[0] #should be /exit or /list or /enter
    
    while cmd != "/exit": #exit
        
        if user_state[client] == 1: #In the game hall
            cmd_list = CMD_LIST_FOR_STATE[1] # cmd_list = ["\list", "\enter", "\exit"]
            
            if cmd not in cmd_list:
                msg = "4002 Unrecognized message"
                try:
                    connectionSocket.send(msg.encode())
                except socket.error as err:
                    print("Recv error: ", err)
                    connectionSocket.close()
                
            if cmd == "/list":
                room_list_str = [str(x) for x in room_list]
                room_list_str = " ".join(room_list_str)
                msg = f"3001 {str(NUM_OF_ROOMS)} {room_list_str}"
                
                try:
                    connectionSocket.send(msg.encode())
                except socket.error as err:
                    print("Recv error: ", err)
                    connectionSocket.close()
                
            if cmd == "/enter":
                arg = int(cmd_args[1])
                if room_list[arg - 1] == 2:
                    msg = "3013 The room is full"
                    
                    try:
                        connectionSocket.send(msg.encode())
                    except socket.error as err:
                        print("Recv error: ", err)
                        connectionSocket.close()
                        
                if room_list[arg - 1] == 1:
                    msg = "3012 Game started. Please guess true or false"
                    
                    try:
                        connectionSocket.send(msg.encode())
                    except socket.error as err:
                        print("Recv error: ", err)
                        connectionSocket.close()
                    
                    lock.acquire()
                    room_list[arg - 1] += 1
                    lock.release()
                    
                    lock.acquire()
                    room_member_list[arg][client] = ""
                    lock.release()
                    
                    lock.acquire()
                    user_state[client] = 3
                    lock.release()
                    
                    continue
                    
                if room_list[arg - 1] == 0:
                    msg = "3011 Wait"
                    
                    try:
                        connectionSocket.send(msg.encode())
                    except socket.error as err:
                        print("Recv error: ", err)
                        connectionSocket.close()
                    
                    lock.acquire()
                    room_list[arg - 1] += 1
                    lock.release()
                    
                    lock.acquire()
                    room_member_list[arg][client] = ""
                    lock.release()
                    
                    lock.acquire()
                    user_state[client] = 2
                    lock.release()
                    
                    # connectionSocket.send(msg.encode())
                    
                    while room_list[arg - 1] < 2:
                        pass
                    
                    msg = "3012 Game started. Please guess true or false"
                    
                    try:
                        connectionSocket.send(msg.encode())
                    except socket.error as err:
                        print("Recv error: ", err)
                        connectionSocket.close()
            
                    lock.acquire()
                    user_state[client] = 3
                    lock.release()
                    
                    continue
                
        elif user_state[client] == 3: #Playing a game
            
            game_over = False
            cmd_list = CMD_LIST_FOR_STATE[3]
            
            while game_over == False:
                
                try:
                    msg = connectionSocket.recv(1024)
                except socket.error as err:
                    print("Recv error: ", err)
                    connectionSocket.close()
                msg = msg.decode()
                cmd_args = msg.split()
                cmd = cmd_args[0] #/guess
                
                if cmd not in cmd_list:
                    msg = "4002 Unrecognized message"
                    try:
                        connectionSocket.send(msg.encode())
                    except socket.error as err:
                        print("Recv error: ", err)
                        connectionSocket.close()
                
                if cmd == "/guess":
                    move = cmd_args[1].capitalize()
                    
                    lock.acquire()
                    room_member_list[arg][client] = move
                    lock.release()
                    
                    while "" in list(room_member_list[arg].values()):
                        pass
                    
                    player_list = list(room_member_list[arg].keys())
                    move_list = list(room_member_list[arg].values())
                
                    # print(player_list)
                    # print(move_list)
                    
                    if move_list[0] == move_list[1]:
                        msg = "3023 The result is a tie"
                        try:
                            connectionSocket.send(msg.encode())
                        except socket.error as err:
                            print("Recv error: ", err)
                            connectionSocket.close()
                        
                        lock.acquire()
                        user_state[client] = 1
                        lock.release()
                        
                        lock.acquire()
                        room_member_list[arg].clear()
                        lock.release()
                        
                        lock.acquire()
                        room_list[arg - 1] = 0
                        lock.release()
                        
                        game_over = True
                        
                    if move_list[0] != move_list[1]:
                        # print(r)
                        index = 0
                        
                        while move_list[index] != r:
                            index += 1
                        
                        if player_list[index] == client:
                            msg = "3021 You are the winner"
                        else:
                            msg = "3022 You lost this game"
                        
                        try:
                            connectionSocket.send(msg.encode())
                        except socket.error as err:
                            print("Recv error: ", err)
                            connectionSocket.close()
                        
                        lock.acquire()
                        user_state[client] = 1
                        lock.release()
                        
                        lock.acquire()
                        room_member_list[arg].clear()
                        lock.release()
                        
                        lock.acquire()
                        room_list[arg - 1] = 0
                        lock.release()
                        
                        game_over = True
        
        try:
            msg = connectionSocket.recv(1024)
        except socket.error as err:
            print("Recv error: ", err)
            connectionSocket.close()
        msg = msg.decode()
        
        cmd_args = msg.split()
        cmd = cmd_args[0] 
    
    msg = "4001 Bye bye"
    
    try:
        connectionSocket.send(msg.encode())
    except socket.error as err:
        print("Recv error: ", err)
        connectionSocket.close()
    
    connectionSocket.close()

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind( ("", server_port) )
serverSocket.listen(5)
print("The server is ready")

while True:
    r = str(bool(random.getrandbits(1)))
    client = serverSocket.accept()
    lock = threading.Lock()
    newthd = threading.Thread(target=thd_func, args=(client, lock,))
    newthd.start()
    
serverSocket.close()