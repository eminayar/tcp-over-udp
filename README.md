# tcp over udp

Messaging and file transfer application in Local Area Network(LAN).

Flow control and acknowledment implemented using UDP sockets.

Python version 3.7.3

Set your ip in **config.py** file then run with **python3 main.py**

Enter your username

Commands =>
    
    list ==> lists online users
        
    message <username> <message> ==> send a message to a user. message can't contain spaces.

    file <username> <filename> ==> send a file to a user. File must be in the same directory with the codes.

To simulate slow consumption of the receive buffer or close slow consumption simulation set **SIMULATE** value to **True** or **False** in the **config.py** file.
