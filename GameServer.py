import socket
import threading
import time
import sys
from threading import Lock
from enum import Enum
import random

port = 0
UserFilePath = ""
TotalRoomNum = 10
RoomUserNum = [0 for i in range(TotalRoomNum)]
RoomUserInstance = [[] for i in range(TotalRoomNum)]
RoomAnswer = [[-1, -1, -1] for i in range(TotalRoomNum)]
roomLock = Lock()

class Stage(Enum):
    Broken = 0
    Authorization = 1
    InTheGameHall = 2
    Waiting = 3
    Gaming = 4


def Output(cnn:socket.socket, code:int, msg:str):
    resp = str.encode(str(code) + " " + msg)
    cnn.send(resp)

def checkPermission(logStage):
    return logStage != Stage.Authorization

def checkPermissionGaming(logStage):
    return logStage == Stage.Gaming

def checkPermissionHall(logStage):
    return logStage == Stage.InTheGameHall

def outputWrongReq(cnn:socket.socket):
    Output(cnn, 4003, "Action and Stage not match")

def logIn(msg_list) -> bool:
    ret = False
    with open(UserFilePath, 'r') as f:
        line = f.readline()
        while line:
            userInfo = line.rstrip('\n').split(":")
            if userInfo[0] == msg_list[1] and userInfo[1] == msg_list[2]:
                print("successfully login")
                ret = True
                break
            line = f.readline()
    return ret

def handleLogIn(cnn:socket.socket, msg_list):
    success = logIn(msg_list)
    if success:
        Output(cnn, 1001, "Authentication successful")
        return Stage.InTheGameHall
    else:
        Output(cnn, 1002, 'Authentication failed')
        return Stage.Authorization

def handleList(cnn:socket.socket, msg_list, logStage):
    if not checkPermission(logStage):
        Output(cnn, 1002, 'Authentication failed')
        return

    if not checkPermissionHall(logStage):
        outputWrongReq(cnn)
        return

    roomLock.acquire()
    roomUserNumStr = [str(x) for x in RoomUserNum]
    roomLock.release()

    Output(cnn, 3001, str(TotalRoomNum) + " " + " ".join(roomUserNumStr))
    return

def handleEnter(cnn:socket.socket, msg_list, logStage):
    if not checkPermission(logStage):
        Output(cnn, 1002, "Authentication failed")
        return Stage.Authorization, None

    if not checkPermissionHall(logStage):
        outputWrongReq(cnn)
        return logStage, None

    roomNum = int(msg_list[1])
    roomLock.acquire()
    roomCount = RoomUserNum[roomNum-1]
    ret = Stage.InTheGameHall
    playerNum = None

    if roomCount == 0:
        RoomUserInstance[roomNum-1].append(cnn)
        RoomUserNum[roomNum-1] += 1
        ret = Stage.Waiting
        playerNum = 0
        Output(cnn, 3011, "Wait")
    elif roomCount == 2:
        ret = Stage.InTheGameHall
        Output(cnn, 3013, "The room is full")
    elif roomCount == 1:
        RoomUserInstance[roomNum - 1].append(cnn)
        RoomUserNum[roomNum - 1] += 1
        ret = Stage.Gaming
        playerNum = 1
        Output(cnn, 3012, "Game started. Please guess true or false")
    roomLock.release()
    return ret, playerNum, roomNum

def handleWaiting(cnn:socket.socket, logStage, roomNum):
    while True:
        # print("i'm waiting")
        roomLock.acquire()
        if RoomUserNum[roomNum-1] == 2:
            break
        roomLock.release()

        time.sleep(0.1)
    RoomAnswer[roomNum-1][0] = random.randint(0, 1)
    roomLock.release()
    Output(cnn, 3012, "Game started. Please guess true or false")
    print("Room"+str(roomNum)+" stop waiting")
    return Stage.Gaming

def gameOver(roomNum, other=-1):
    roomLock.acquire()
    if other != -1:
        Output(RoomUserInstance[roomNum-1][other], 3021, "You are the winner")
    elif RoomAnswer[roomNum-1][1] == RoomAnswer[roomNum-1][2]:
        Output(RoomUserInstance[roomNum-1][0], 3023, "The result is a tie")
        Output(RoomUserInstance[roomNum-1][1], 3023, "The result is a tie")
    elif RoomAnswer[roomNum-1][0] == RoomAnswer[roomNum-1][1]:
        Output(RoomUserInstance[roomNum-1][0], 3021, "You are the winner")
        Output(RoomUserInstance[roomNum-1][1], 3022, "You lost this game")
    elif RoomAnswer[roomNum-1][0] == RoomAnswer[roomNum-1][2]:
        Output(RoomUserInstance[roomNum-1][1], 3021, "You are the winner")
        Output(RoomUserInstance[roomNum-1][0], 3022, "You lost this game")

    RoomAnswer[roomNum-1] = [-1, -1, -1]
    RoomUserNum[roomNum-1] = 0
    RoomUserInstance[roomNum-1] = []
    roomLock.release()

def handleGaming(cnn:socket.socket, msg_list, logStage, playerNum:int, roomNum):
    if not checkPermissionGaming(logStage):
        outputWrongReq(cnn)
        return logStage
    if msg_list[1] not in ["true", "false"]:
        Output(cnn, 4002, "Unrecognized message")

    print("player"+str(playerNum)+" guess " + msg_list[1])
    ans = 1 if msg_list[1] == "true" else 0
    other = 0 if playerNum == 1 else 1

    roomLock.acquire()
    RoomAnswer[roomNum-1][playerNum+1] = ans

    if RoomAnswer[roomNum-1][other+1] == -1:
        roomLock.release()
        while True:
            roomLock.acquire()
            if RoomAnswer[roomNum-1][0] == -1:
                break
            roomLock.release()
            time.sleep(0.1)
        roomLock.release()
    else:
        roomLock.release()
        gameOver(roomNum)

    return Stage.InTheGameHall
def handleExit(cnn:socket.socket, msg_list, logStage):
    Output(cnn, 4001, "Bye bye")
    cnn.close()

def informOther(playerNum, roomNum, logStage):
    if not checkPermissionGaming(logStage):
        return
    other = 0 if playerNum == 1 else 1
    gameOver(roomNum, other)

def HandleUser(cnn:socket.socket):
    logStatus = Stage.Authorization
    playerNum = None
    roomNum = None
    while not getattr(cnn, '_closed'):
        try:
            if logStatus == Stage.Waiting:
                logStatus = handleWaiting(cnn, logStatus, roomNum)
                continue
            msg = bytes.decode(cnn.recv(1024))
            print("recv: ", msg)
            msg_list = msg.split(" ")
            if msg_list[0] == "/login" :
                logStatus = handleLogIn(cnn, msg_list)
            elif msg_list[0] == "/list":
                handleList(cnn, msg_list, logStatus)
            elif msg_list[0] == "/enter":
                logStatus, playerNum, roomNum = handleEnter(cnn, msg_list, logStatus)
            elif msg_list[0] == "/guess":
                logStatus = handleGaming(cnn, msg_list, logStatus, playerNum, roomNum)
            elif msg_list[0] == "/exit":
                handleExit(cnn, msg_list,logStatus)
                break
            else:
                Output(cnn, 4002, "Unrecognized message")
                print("Unexpected input")
        except BrokenPipeError:
            informOther(playerNum, roomNum, logStatus)
            break
        except Exception as e:
            Output(cnn, 4002, "Unrecognized message")
            print("Wrong input, err:", e)


if __name__ == "__main__":
    try:
        port = sys.argv[1]
        UserFilePath = sys.argv[2]
        with open(UserFilePath, 'r') as f:
            pass
    except:
        print("cannot start the server")
        exit(0)
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', int(port)))
        s.listen(5)
        print("Listening for client connection")
        cnn, addr = s.accept()
        th = threading.Thread(target=HandleUser, args=(cnn,), daemon=True)
        th.start()
