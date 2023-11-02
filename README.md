# Network Programming Assignment
Xu Ziyin 3036173372

For both `GameClient.py` and `GameServer.py`, there is a class `Stage`, listed out all possible stages for the player.

First start `GameServer.py`, it will connect the server. 
Then call `HandleUser()`, which updates `logStatus`, `playerNum` and `roomNum` according to the `msg_list`.

For `handleWaiting()`

For `handleLogIn()`, check whether the Authenticaton infomation is correct. If so, return stage `InTheGameHall`.

For `handleList()`, 

For `handleEnter()`

For `handleGaming()`

For `handleExit()`