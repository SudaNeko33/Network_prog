import socket
import sys
from enum import Enum

serverIP = ""
serverPort = 0


class Stage(Enum):
    Broken = 0
    Authorization = 1
    InTheGameHall = 2
    Waiting = 3
    Gaming = 4

def recv_and_print(client:socket.socket):
    resp = bytes.decode(client.recv(1024))
    print(resp)
    return resp.split(" ")

def respHandler(client:socket.socket, resp):
    if resp[0] == "4001":
        client.close()
    elif resp[0] == "1001":
        return Stage.InTheGameHall
    elif resp[0] == "1002":
        return Stage.Authorization
    elif resp[0] == "3011":
        return Stage.Waiting
    elif resp[0] == "3012":
        return Stage.Gaming
    elif resp[0] == "3013":
        return Stage.InTheGameHall
    elif resp[0] in ["3021", "3022", "3023"]:
        return Stage.InTheGameHall

def output(client:socket.socket, cmd, *args):
    req = str.encode(cmd + " " + " ".join(args))
    client.send(req)

def login(client:socket.socket):
    username = input("Please input your user name:\n")
    password = input("Please input your password:\n")
    output(client, "/login", username, password)
    resp = recv_and_print(client)
    return respHandler(client, resp)

def handleWait(client:socket.socket):
    while True:
        try:
            return recv_and_print(client)
        except socket.timeout:
            continue


def handleClient(client:socket.socket, stage):
    if stage == Stage.Waiting:
        resp = handleWait(client)
        return respHandler(client, resp)

    cmd = input(">>")
    client.send(str.encode(cmd))

    resp = recv_and_print(client)
    return respHandler(client, resp)


if __name__ == "__main__":
    serverIP = sys.argv[1]
    serverPort = int(sys.argv[2])

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((serverIP, serverPort))

    stage = Stage.Authorization

    while not getattr(client, '_closed'):
        try:
            if stage == Stage.Authorization:
                stage = login(client)
                continue
            stage = handleClient(client, stage)
        except Exception as e:
            print("err msg: ", e)
            break